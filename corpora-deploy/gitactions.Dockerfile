FROM 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy:latest

WORKDIR /deploy
COPY . /deploy
RUN rm /deploy/ansible.cfg
RUN mv /deploy/ansible_docker.cfg /deploy/ansible.cfg
