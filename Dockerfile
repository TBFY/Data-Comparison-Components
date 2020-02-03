FROM python:latest 

RUN mkdir /oesia
COPY python/carga-inicial.py /oesia
RUN pip3 install elasticsearch

