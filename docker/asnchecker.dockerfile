FROM ubuntu:latest

RUN apt-get update && apt-get install python3 python3-pip -y
COPY asnchecker.tar.gz /
COPY entrypoint.sh /
RUN tar -zxvf /asnchecker.tar.gz
RUN pip3 install -r /asnchecker/requirements.txt

ENTRYPOINT ["sh", "/entrypoint.sh"]
