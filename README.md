# hassio-bluetti-bt
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate with hassfest](https://github.com/Patrick762/hassio-bluetti-bt/actions/workflows/hassfest_validation.yml/badge.svg)](https://github.com/Patrick762/hassio-bluetti-bt/actions/workflows/hassfest_validation.yml)
[![HACS Action](https://github.com/Patrick762/hassio-bluetti-bt/actions/workflows/HACS.yml/badge.svg)](https://github.com/Patrick762/hassio-bluetti-bt/actions/workflows/HACS.yml)

Bluetti Integration for Home Assistant

Based on [bluetti_mqtt](https://github.com/warhammerkid/bluetti_mqtt).

### Supported devices:
(based on [supported devices of bluetti_mqtt](https://github.com/warhammerkid/bluetti_mqtt/tree/main/bluetti_mqtt/core/devices))

- AC60
- AC200M
- AC300 (tested)
- AC500
- EB3A
- EP500
- EP500P
- EP600 (tested)

### Available sensors:
All sensors which are available in bluetti_mqtt (Based on [this file](https://github.com/warhammerkid/bluetti_mqtt/blob/main/bluetti_mqtt/mqtt_client.py))
excluding battery pack fields.

### Available controls:
If enabled in the Integration options (you need to reload the integration if you change this option):
AC and DC outputs
