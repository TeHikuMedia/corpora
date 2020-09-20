# FROM python:3.7.9-slim
FROM 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy:latest

RUN apt-get update
RUN apt-get install -y python3 python3-pip openssh-client

RUN python3 -m pip install pip --upgrade
RUN python3 -m pip install ansible==2.9.11
RUN python3 -m pip install boto3
RUN python3 -m pip install boto
RUN python3 -m pip install netaddr

WORKDIR /deploy
COPY . /deploy
RUN rm /deploy/ansible.cfg
RUN mv /deploy/ansible_docker.cfg /deploy/ansible.cfg

# ENTRYPOINT ["/deploy/scripts/setup.sh"]


# docker build . -t corpora-deploy
# docker run -dit --name corpora-deploy corpora-deploy
# docker exec -it corpora-deploy /bin/bash
# docker rm corpora-deploy 
# docker logs corpora-deploy -f
# docker run -dit --name corpora-deploy --entrypoint /deploy/scripts/deploy.sh -e ENV_TYPE=staging -e TAGS=deploy-now -e VAULT_PASS= corpora-deploy