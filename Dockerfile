FROM python:3.10

EXPOSE 18000

LABEL MAINTAINER="Colm McBarron"
LABEL NAME=afore-local-exporter

RUN mkdir /etc/afore-local-exporter
COPY *.py *.txt afore_local_exporter /etc/afore-local-exporter/

WORKDIR /etc/afore-local-exporter/

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "python", "./main.py" ]