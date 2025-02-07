FROM python:3

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY tests ./tests
COPY custom_components ./custom_components

RUN python3 -m unittest discover -s tests -p "*_test.py"
