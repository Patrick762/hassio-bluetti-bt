from enum import Enum
import hashlib
import logging
import os
import pyasn1.codec.der.decoder as der_decoder
import pyasn1.codec.der.encoder as der_encoder
from pyasn1.type import univ
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

from custom_components.bluetti_bt.bluetti_bt_lib.const import LOCAL_AES_KEY, PRIVATE_KEY_L1, PUBLIC_KEY_K2, SECP_256R1_PUBLIC_PREFIX


_LOGGER = logging.getLogger(__name__)

KEX_MAGIC = b"**"
AES_BLOCK_SIZE = 16

def hexsum(s, sz: int):
    checksum = sum(s)
    as_hex = f"{checksum:0{sz*2}x}"
    return bytes.fromhex(as_hex)

def hexxor(a: bytes, b: bytes) -> bytes | None:
    if len(a) != len(b):
        _LOGGER.error("Can only XOR two identical length byte strings")
        return None
    return bytes([x ^ y for x, y in zip(a, b)])

def raw_ecdsa_to_der(sig):
    # <byte r[32]> <byte s[32]>

    if len(sig) != 64:
        raise ValueError("ecdsa signature is the wrong size")

    seq = univ.SequenceOf()
    seq.extend(
        [
            univ.Integer(int.from_bytes(sig[:32], "big")),  # r
            univ.Integer(int.from_bytes(sig[32:], "big")),  # s
        ]
    )
    return der_encoder.encode(seq)

def der_to_raw_ecdsa(sig):
    # 30 45 02 20 1956307e59448178b47c222e4e1e6c8ef7d707bc230e5a9fa77f919ec44e5f74
    # |  |  |  |  |> byte r[0x20]
    # |  |  |  |---> Length
    # |  |  |------> DER type (int)
    # |  |---------> Payload size
    # |------------> DER type (sequence)

    #       02 21 00cfad6e11abd5e803fb6874c3838bc968db1f3c070ae6b85db9d8ed8936a1eb5c
    #       |  |  |> byte s[0x21]
    #       |  |---> Length
    #       |------> DER type (int)

    seq, remainder = der_decoder.decode(sig)
    if remainder:
        raise ValueError("Found trailing data")

    return b"".join([int.to_bytes(int(x), 0x20, "big") for x in seq])

def verify_and_extract_signed_data(message, signed_data_suffix: bytes | None):
    # 64 bytes of data
    # 64 bytes of signature
    if len(message) != 128:
        raise ValueError("Unexpected message length")

    data = message[:64]
    signature = message[64:]
    signed_data = data.tobytes() + signed_data_suffix
    der_signature = raw_ecdsa_to_der(signature)
    try:
        key_bytes = bytes.fromhex(PUBLIC_KEY_K2)
        serialization.load_der_public_key(key_bytes).verify(
            der_signature, signed_data, ec.ECDSA(hashes.SHA256())
        )
        _LOGGER.debug("Signature OK")
    except InvalidSignature:
        raise

    return data

def pubkey_from_bytes(data):
    encoded_peer_pubkey = bytes.fromhex(SECP_256R1_PUBLIC_PREFIX) + data
    return serialization.load_der_public_key(encoded_peer_pubkey)

def generate_keypair():
    private = ec.generate_private_key(ec.SECP256R1())
    return (private.public_key(), private)

def pubkey_to_bytes(pubkey):
    out = pubkey.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )

    if out[0] != 0x4 or len(out) != 65:
        raise RuntimeError(
            "First byte should be 04 for the uncompressed format, and total size 64"
        )

    return out[1:]

class MessageType(Enum):
    CHALLENGE = 1
    CHALLENGE_ACCEPTED = 3
    PEER_PUBKEY = 4
    PUBKEY_ACCEPTED = 6

class Message:
    """
    Two types of messages. The first one is for communication that happens before we have
    a proper symmetric key available. These are fully handled by this file, it's purely
    to setup the encryption protocol.

    2a2a .... 0000
    |         |> Body checksum
    |    |-----> Body
    |----------> Magic value for pre-key-exchange

    The second type is for anything after. This can either contain the type 1 message above, or
    anything else -- at this point we're just wrapping the regular protocol, and we just forward
    the packets dowm the regular processing path after decrypting them.

    See aes_decrypt() for the format.
    """

    def __init__(self, buffer: bytes):
        self.buffer = buffer
        self.view = memoryview(self.buffer)

    @property
    def header(self) -> memoryview:
        return self.view[:2]

    @property
    def is_pre_key_exchange(self) -> bool:
        return self.header == KEX_MAGIC

    @property
    def checksum(self) -> memoryview:
        return self.view[-2:]

    @property
    def body(self) -> memoryview:
        return self.view[len(self.header) : -len(self.checksum)]

    @property
    def data(self) -> memoryview:
        return self.body[2:]

    @property
    def type(self) -> int:
        return MessageType(self.body[0])

    def verify_checksum(self):
        message_checksum = self.checksum
        computed_checksum = hexsum(self.body, len(message_checksum))
        if computed_checksum != message_checksum:
            _LOGGER.error("Checksum error!")
        _LOGGER.debug("Checksum OK")

class BluettiEncryption:
    # Derived exclusively from data sent over the network
    # Used for the initial handshake
    unsecure_aes_key: bytes | None = None

    # Predictably derived from a seed sent by the peer
    # This is the same for all the messages encrypted
    # with that key during the connection
    unsecure_aes_iv: bytes | None = None

    # Proper key exchange gives us another key,
    # that is used for the remainder of the connection
    # IV is random per message
    secure_aes_key: bytes | None = None

    # Received through key exchange
    # The signing key for the key exchange is well-known
    peer_pubkey: bytes | None = None

    @property
    def is_ready_for_commands(self) -> bool:
        return self.secure_aes_key is not None and self.peer_pubkey is not None

    def aes_decrypt(self, data: bytes, aes_key: bytes | None, iv: bytes | None):
        data_len = (data[0] << 8) + data[1]

        if iv is None:
            iv = hashlib.md5(data[2:6]).digest()
            encrypted = memoryview(data)[6:]
        else:
            encrypted = memoryview(data[2:])

        if len(encrypted) % AES_BLOCK_SIZE != 0:
            raise ValueError("Data not aligned on aes block size")

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        decrypted = decrypted[:data_len]

        _LOGGER.debug(">PLAIN " + decrypted.hex())
        return decrypted


    def aes_encrypt(self, data: bytes, aes_key: bytes | None, iv: bytes | None):
        message_header = int.to_bytes(len(data), 2, "big")

        if iv is None:
            iv_seed = os.urandom(4)
            iv = hashlib.md5(iv_seed).digest()
            message_header += iv_seed

        padding = (AES_BLOCK_SIZE - len(data) % AES_BLOCK_SIZE) % AES_BLOCK_SIZE
        data += bytes(padding)

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(data) + encryptor.finalize()
        encrypted = message_header + encrypted

        _LOGGER.debug("PLAIN> " + data.hex())
        return encrypted
    
    def msg_challenge(self, message: Message) -> bytes | None:
        _LOGGER.debug("Received challenge")

        if len(message.data) != 4:
            _LOGGER.error("Unexpected message length")
            return None

        self.unsecure_aes_iv = hashlib.md5(message.data[::-1].tobytes()).digest()
        static_key = bytes.fromhex(LOCAL_AES_KEY)
        self.unsecure_aes_key = hexxor(self.unsecure_aes_iv, static_key)

        _LOGGER.info("Unsecure iv  " + self.unsecure_aes_iv.hex())
        _LOGGER.info("Unsecure key " + self.unsecure_aes_key.hex())

        body = bytes.fromhex("0204") + self.unsecure_aes_iv[8:12]
        return b"".join([KEX_MAGIC, body, hexsum(body, 2)])

    def msg_peer_pubkey(self, message: Message) -> bytes | None:
        _LOGGER.debug("Received peer pubkey, checking signature")
        data = verify_and_extract_signed_data(message.data, self.unsecure_aes_iv)
        self.peer_pubkey = pubkey_from_bytes(data)

        _LOGGER.debug("Generating a local keypair")
        self.my_pubkey, self.my_privkey = generate_keypair()
        my_pubkey_bytes = pubkey_to_bytes(self.my_pubkey)

        _LOGGER.debug("Signing the local pubkey")
        signing_secret = int.from_bytes(
            bytes.fromhex(PRIVATE_KEY_L1), "big"
        )
        signing_key = ec.derive_private_key(signing_secret, ec.SECP256R1())
        to_sign = my_pubkey_bytes + self.unsecure_aes_iv
        signature = signing_key.sign(to_sign, ec.ECDSA(hashes.SHA256()))
        raw_signature = der_to_raw_ecdsa(signature)

        body = b"".join([bytes.fromhex("0580"), my_pubkey_bytes, raw_signature])
        msg = b"".join([KEX_MAGIC, body, hexsum(body, 2)])
        return self.aes_encrypt(msg, self.unsecure_aes_key, self.unsecure_aes_iv)
    
    def msg_key_accepted(self, message: Message) -> None:
        _LOGGER.debug("Received key exchange confirmation, calculating shared secret")

        if len(message.data) != 1:
            raise ValueError("Unexpected message length")
        if message.data[0] != 0:
            raise ValueError("Key acceptance response is not 0")

        self.secure_aes_key = self.my_privkey.exchange(ec.ECDH(), self.peer_pubkey)
        _LOGGER.info("Secure key   " + self.secure_aes_key.hex())

    def getKeyIv(self):
        return (
            (self.unsecure_aes_key, self.unsecure_aes_iv)
                if self.secure_aes_key is None
                else (self.secure_aes_key, None)
        )
    
    def reset(self):
        self.peer_pubkey = None
        self.secure_aes_key = None
