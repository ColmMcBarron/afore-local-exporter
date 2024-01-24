FROM python:3.10

EXPOSE 18000

LABEL MAINTAINER="Colm McBarron"
LABEL NAME=afore-local-exporter

RUN mkdir -p /etc/afore-local-exporter/afore_local_exporter
COPY *.py *.txt /etc/afore-local-exporter/
COPY afore_local_exporter/*.py /etc/afore-local-exporter/afore_local_exporter/

WORKDIR /etc/afore-local-exporter/

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "python", "main.py" ]