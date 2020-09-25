FROM 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy:latest

WORKDIR /deploy
RUN cp /deploy/env_vars/vault.yml /tmp/vault.yml
COPY . /deploy
COPY ansible_docker.cfg /deploy/ansible.cfg
RUN cp /tmp/vault.yml /deploy/env_vars/vault.yml
