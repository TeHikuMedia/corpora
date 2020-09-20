#!/bin/bash

. /deploy/scripts/setup.sh

echo "$ANSIBLE_VAULT_PASS"
echo "$AWS_SECRET_ACCESS_KEY"

# Default deploytment tags
tag='deploy'
# if [[ -z "$SERVER_TYPE" ]]; then
# 	tag='deploy'
# elif [[ "$SERVER_TYPE" == "web" ]]; then
# 	tag='deploy-web'
# elif [[ "$SERVER_TYPE" == "media" ]]; then
# 	tag='deploy-media'
# fi

# Overwrite ansible tags
if [[ -n "$TAGS" ]]; then
	tag=$TAGS
	echo "Using tags: $tag"
fi

if [[ -z "$ENV_TYPE" ]]; then
	# ENV_TYPE not defined
	echo "Please set ENV_TYPE variable"

elif [[ "$ENV_TYPE" == "staging" ]]; then
	echo "Running staging deployment with -t $tag"
	ansible-playbook \
		-i inventory/aws_ec2.yml \
		--vault-password-file=~/.vault_pass.txt \
		--private-key=$KEY_PATH \
		--extra-vars "repo_branch=develop" \
		staging.yml \
		-t $tag

elif [[ "$ENV_TYPE" == "production" ]]; then
	echo "Running production deployment with -t $tag"

	# if [[ -z "$SERVER_TYPE" ]] && [[ -z "$TAGS" ]]; then

	# 	ansible-playbook \
	# 		-i inventory/aws_ec2.yml \
	# 		--vault-password-file=~/.vault_pass.txt \
	# 		--private-key=$KEY_PATH \
	# 		production.yml \
	# 		-t $tag-web

	# 	ansible-playbook \
	# 		-i inventory/aws_ec2.yml \
	# 		--vault-password-file=~/.vault_pass.txt \
	# 		--private-key=$KEY_PATH \
	# 		production.yml \
	# 		-t $tag-media
	# else
	ansible-playbook \
		-i inventory/aws_ec2.yml \
		--vault-password-file=~/.vault_pass.txt \
		--private-key=$KEY_PATH \
		production.yml \
		-t $tag
	# fi
fi



