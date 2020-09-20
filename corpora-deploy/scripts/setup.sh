#!/bin/sh

# Setup system for running ansible

SSH_PATH=~/.ssh
KEY_FILE=corpora_2020.pem
KEY_PATH=$SSH_PATH/$KEY_FILE

echo "$ANSIBLE_VAULT_PASS" > ~/.vault_pass.txt

credentials=$(\
	ansible localhost \
	--inventory='localhost,' \
	--connection=local \
	--vault-password-file=~/.vault_pass.txt \
	--extra-vars=@env_vars/vault.yml \
	-m debug \
	-a 'msg="{{ ansible_aws_id }}:{{ ansible_aws_secret }}"' |\
	tr -d ' ' | grep '"msg":' | cut -d'"' -f4)

key=$(\
	ansible localhost \
	--inventory='localhost,' \
	--connection=local \
	--vault-password-file=~/.vault_pass.txt \
	--extra-vars=@env_vars/vault.yml \
	-m debug \
	-a 'msg="{{ corpora_ec2_key }}"' |\
	grep '"msg":' | cut -d'"' -f4)


export AWS_ACCESS_KEY_ID=$(echo $credentials | cut -d: -f1)
export AWS_SECRET_ACCESS_KEY=$(echo $credentials | cut -d: -f2)

mkdir $SSH_PATH
echo $key > ~/out.pem
awk '{gsub(/\\n/,"\n")}1' ~/out.pem > $KEY_PATH
rm ~/out.pem
chmod 0600 $KEY_PATH
