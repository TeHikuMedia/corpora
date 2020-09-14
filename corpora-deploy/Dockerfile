FROM python:3.7.9-slim
# 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy:latest

RUN apt-get update
RUN apt-get install -y python3 python3-pip openssh-client

RUN python3 -m pip install pip --upgrade
RUN python3 -m pip install ansible==2.9.11
RUN python3 -m pip install boto3
RUN python3 -m pip install boto
RUN python3 -m pip install netaddr

WORKDIR /deploy
COPY . /deploy

ENTRYPOINT ["/deploy/scripts/setup.sh"]
