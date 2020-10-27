# Build & Run a Deploy Machine
This step is only necessary if you want to build a "deployment machine" locally.
A deployment machine is a Linux machine with the packages required to deploy this project using ansible.
We created this docker container so that we can use Git Actions for continuous deployment. Currently this docker container only supports deployment to staging and production environments. Perhaps we should look at including a local deployment.

We use our env_vars/vault.yml file to copy over required credentials such as AWS access and
the ec2 key (env_vars/base.yml:ec2_key_pair) used to ssh into the machines created in this deployment.

Before you start, you'll need some environment variables.
The first is a `ANSIBLE_VAULT_PASSWORD` to access credentials in the ansible vault
(ask one of the developers for theirs).
The second is a var saying which environment you want to deploy
e.g. production or staging.

```bash
export ENV_TYPE=production
export ANSIBLE_VAULT_PASSWORD=ASKSOMEONE
docker build ./ -t corpora-deploy
docker run \
  --entrypoint /deploy/scripts/deploy.sh \
  -e ENV_TYPE=$ENV_TYPE \
  -e ANSIBLE_VAULT_PASS=$ANSIBLE_VAULT_PASSWORD \
  corpora-deploy
```

## Help with Docker
Below are useful commands when having issues with docker

```bash
# Build
docker build . -t corpora-deploy
# Run the docker container with a name
docker run -dit --name corpora-deploy corpora-deploy
# Run a bash terminal for the running ^ container
docker exec -it corpora-deploy /bin/bash
# Removes the docker image?
docker rm corpora-deploy 
# Show logs
docker logs corpora-deploy -f
# Sample deployment command
docker run -dit --name corpora-deploy --entrypoint /deploy/scripts/deploy.sh -e ENV_TYPE=staging -e TAGS=deploy-django -e ANSIBLE_VAULT_PASS=$ANSIBLE_VAULT_PASSWORD corpora-deploy
```

## Building & Pushing corpora-deploy docker to AWS ECR
```bash
# Build the base docker
docker build . -t corpora-deploy
# Get & run login
$(aws ecr get-login --no-include-email)
# Tag our image
docker tag corpora-deploy 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
# Push image to repo
docker push 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
# Now re-build the ECR with the proper Dockerfile
docker build . -t corpora-deploy --file gitactions.Dockerfile
# Tag our image
docker tag corpora-deploy 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
# Push image to repo
docker push 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
# Run from ECR
docker run --entrypoint /deploy/scripts/deploy.sh -e ENV_TYPE=staging -e TAGS=deploy-django -e ANSIBLE_VAULT_PASS=$ANSIBLE_VAULT_PASSWORD 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
```


# NPM Workflow

The following ansible roles are requied for running our npm workflow,
- **webpack** [link](https://github.com/TeHikuMedia/ansible-django-stack/tree/master/roles/webpack/tasks)
  - this installs the latest node
- **webpack-build** [link](https://github.com/TeHikuMedia/ansible-django-stack/tree/master/roles/webpack-build)
  - this builds the actual bundle by running e.g. `npm run build`
  - you have to define the ansible variable `npm_dir: {{ application_path }}/vue_frontend`
  - you have to define the build command: `npm_build_cmd: "npm run build"`
  - our webpack is configured to use environment variables provided by `/webapp/bin/postactivate`.
    this is used to set things like the static files url e.g. if they are behind a cdn.

Checkout the following code to see how this works,
- [npm installation](https://github.com/TeHikuMedia/ansible-django-stack/blob/master/roles/webpack/tasks/main.yml)
- [npm build](https://github.com/TeHikuMedia/ansible-django-stack/blob/master/roles/webpack-build/tasks/main.yml)
- [vue configuration](https://github.com/TeHikuMedia/corpora/blob/vue_frontend/corpora/vue_frontend/vue.config.js)
- variables defined in [`env_vars/base.yml`](https://github.com/TeHikuMedia/corpora/blob/bc4bd334dfb7aaa170eeee34eef0e3d8f92d53ac/corpora-deploy/env_vars/base.yml#L27)
- [vue.config.js](https://github.com/TeHikuMedia/corpora/blob/tumu/corpora/vue_frontend/vue.config.js)

## Automated npm build with gitactions
We have two workflows for building our npm stuff. Here is our staging workflow: 
https://github.com/TeHikuMedia/corpora/blob/tumu/.github/workflows/build_vue_staging.yml. 
These are set up to only run when vue related code is changed. 
If you add more vue code to other directories, you'll need to ensure those directories are included in this workflow's `paths`. 
These are only run on pull requests to `staging` or `tumu` branches or on a push to `tumu`. 

## TODO
- Add npm tests to the [npm tasks](https://github.com/TeHikuMedia/ansible-django-stack/blob/master/roles/webpack-build/tasks/main.yml)


# Setup

To deploy the kuaka platform, you will need the following packages: 

* [boto] (https://github.com/boto/boto)
* [virtual box](https://www.virtualbox.org/)
* [vagrant](https://www.vagrantup.com/)
* [ansible](http://docs.ansible.com/ansible/intro_installation.html)

You will also need to export your AWS credentials as boto uses these when talking with our servers in AWS,

    export AWS_SECRET_ACCESS_KEY='...'
    export AWS_ACCESS_KEY_ID='...'


## Mac OS X ##
Note on Mac OS you should install homebrew and then install python. This lets you install pip through a user modifiable python installation, which will prevent headaches. See [this](http://apple.stackexchange.com/questions/209572/how-to-use-pip-after-the-os-x-el-capitan-upgrade).


```
#!bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install python
pip install boto ansible etc.
```


Ansible
=======
Our ansible deployment is written for three environments,

  1. Local
  2. Staging
  3. Production

And in each of those environments we have three sets of plays,

  1. Launch - this is where we "turn on" our servers in the cloud
  2. Provision - this is where we install all the base packages we need
  3. Deploy - this is the deployment associated with the actual code base in the repository kuaka

Once an environment has 1) Launched and been 2) Provisioned, you only need to 3) Deploy changes to kuaka for the changes to be live.

### Tags ###

All of our plays are in master.yaml in the top directory. We use tags to different environments and plays. For example,

  * deploy-local: deploys the kuaka code
  * launch-staging: launches servers in AWS for the staging environment
  * provision-production: installs base packages into the production environment


Local Instance
==============

### Starting From Scratch ###
Run the command:

    ansible-playbook -i inventory/vagrant.py local.yml


### Starting From Shutdown/Restart ###
If you restart or shutdown your computer, you'll need to run,

    vagrant up

in order to get the virtual box running again. You'll also need to re-deploy the code with,

    ansible-playbook -i inventory/vagrant.py --private-key=.vagrant/machines/default/virtualbox/private_key local.yml -t deploy

to get Django working correctly. Not sure why we have to do this. It would be good if "vagrant up" did everything - add this to the TO DO.

### Developing in Local ###

On a local environment all changes to your code in kuaka will happen immediately as your kuaka repository folder should be linked with a folder in the local virtual box (e.g. ../corpora => virtualbox://webapp/corpora/corpora). You'll need to run django's collectstatic command if you make changes to files in the templates/static folder, for example .css or .js files. This can be done with the command,

    ansible-playbook -i inventory/vagrant.py --private-key=.vagrant/machines/default/virtualbox/private_key local.yml -t deploy

where we re-deploy the code (this play calls Django's colllecstatic command). Alternatively, one could log into the virtual box and run collectstatic. For example,

    vagrant ssh
    sudo sh /webapp/bin/activate && sudo sh /webapp/bin/postactivate && cd /webapp/corpora/corpora/ && python manage.py collectstatic --noinput 

NOTE: We've substituted variables into the command above.


Remote Instances
================

To deploy a staging instance,

    ansible-playbook -i inventory/aws_ec2.yml --private-key ~/.ssh/corpora_2020.pem staging.yml

To deploy a production instance, 

    ansible-playbook -i inventory/aws_ec2.yml --private-key ~/.ssh/corpora_2020.pem production.yml

We're now using dedicated servers for media transcoding. This requires building two machines running the kuaka app. The plays above run these extra steps, however there are handlers that will determine when the media machine should be re-deployed and built as an AMI.

Once the instances have been launched and provisioned, it's only necessary to run the code with the following tags,


**Staging:**

    ansible-playbook -i inventory/aws_ec2.yml --private-key ~/.ssh/corpora_2020.pem staging.yml -t deploy,scale

**Production:**

    ansible-playbook -i inventory/aws_ec2.yml --private-key ~/.ssh/corpora_2020.pem production.yml -t deploy,scale


The scale tag provisions Auto Scaling for the Media server.

Once the instances have been launched and provisioned, it's only necessary to run the code with the following tags,


**Staging:**

    ansible-playbook -i inventory/aws_ec2.yml --private-key ~/.ssh/corpora_2020.pem staging.yml -t deploy

**Production:**

    ansible-playbook -i inventory/aws_ec2.yml --private-key ~/.ssh/corpora_2020.pem production.yml -t deploy


Note that we need to pass the branch to the staging play as this allows us to test different branches on the same staging servers.

Ansible Vault
================
We store sensitive information for this deployment in an ansible vault.

To decrypt an encrypted file,

    ansible-vault decrypt env_vars/vault.yml 

To encrypt a file,

    ansible-vault encrypt env_vars/vault.yml
