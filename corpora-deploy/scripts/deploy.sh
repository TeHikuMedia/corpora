#!/bin/bash

. /deploy/scripts/setup.sh

export ANSIBLE_STDOUT_CALLBACK=debug
export ANSIBLE_LOAD_CALLBACK_PLUGINS=True
export ANSIBLE_FORCE_COLOR=True

# Default deploytment tags
tag='deploy'

# Overwrite ansible tags
if [[ -n "$TAGS" ]]; then
	tag=$TAGS
	echo "Using tags: $tag"
fi

if [[ -z "$ENV_TYPE" ]]; then
	# ENV_TYPE not defined
	echo "Please set ENV_TYPE variable"

elif [[ "$ENV_TYPE" == "staging" ]]; then
	if [[ -z "$BRANCH" ]]; then
		BRANCH=staging

	echo "Running staging deployment with -t $tag and branch:$BRANCH"
	ansible-playbook \
		-i inventory/aws_ec2.yml \
		--vault-password-file=~/.vault_pass.txt \
		--private-key=$KEY_PATH \
		--extra-vars "git_branch=$BRANCH" \
		staging.yml \
		-t $tag

elif [[ "$ENV_TYPE" == "production" ]]; then
	echo "Running production deployment with -t $tag"
	ansible-playbook \
		-i inventory/aws_ec2.yml \
		--vault-password-file=~/.vault_pass.txt \
		--private-key=$KEY_PATH \
		production.yml \
		-t $tag
fi
