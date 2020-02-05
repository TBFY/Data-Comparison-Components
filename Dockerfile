FROM sirensolutions/siren-platform:latest

RUN apt-get update && apt-get install -y python-pip git && pip install elasticsearch

COPY script/init.sh /init.sh