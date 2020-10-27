FROM python:3.7.9-slim

RUN apt-get update
RUN apt-get install -y python3 python3-pip openssh-client

RUN python3 -m pip install pip --upgrade
RUN python3 -m pip install ansible==2.10.1
RUN python3 -m pip install boto3
RUN python3 -m pip install boto
RUN python3 -m pip install netaddr

WORKDIR /deploy
COPY . /deploy
COPY ansible_docker.cfg /deploy/ansible.cfg
