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

    ansible-playbook -i inventory/vagrant.py --vault-password-file=~/tehikudev/.vault_pass.txt --private-key=.vagrant/machines/default/virtualbox/private_key local.yml -t deploy

to get Django working correctly. Not sure why we have to do this. It would be good if "vagrant up" did everything - add this to the TO DO.

### Developing in Local ###

On a local environment all changes to your code in kuaka will happen immediately as your kuaka repository folder should be linked with a folder in the local virtual box (e.g. ../corpora => virtualbox://webapp/corpora/corpora). You'll need to run django's collectstatic command if you make changes to files in the templates/static folder, for example .css or .js files. This can be done with the command,

    ansible-playbook -i inventory/vagrant.py --vault-password-file=~/tehikudev/.vault_pass.txt --private-key=.vagrant/machines/default/virtualbox/private_key local.yml -t deploy

where we re-deploy the code (this play calls Django's colllecstatic command). Alternatively, one could log into the virtual box and run collectstatic. For example,

    vagrant ssh
    sudo sh /webapp/bin/activate && sudo sh /webapp/bin/postactivate && cd /webapp/corpora/corpora/ && python manage.py collectstatic --noinput 

NOTE: We've substituted variables into the command above.


Remote Instances
================

To deploy a staging instance,

    ansible-playbook -i inventory/ec2.py --vault-password-file=~/tehikudev/.vault_pass.txt --private-key=~/.ssh/tehiku.pem staging.yml

To deploy a production instance, 

    ansible-playbook -i inventory/ec2.py --vault-password-file=~/tehikudev/.vault_pass.txt --private-key=~/.ssh/tehiku.pem production.yml

We're now using dedicated servers for media transcoding. This requires building two machines running the kuaka app. The plays above run these extra steps, however there are handlers that will determine when the media machine should be re-deployed and built as an AMI.

Once the instances have been launched and provisioned, it's only necessary to run the code with the following tags,


**Staging:**

    ansible-playbook -i inventory/ec2.py --vault-password-file=~/tehikudev/.vault_pass.txt --private-key=~/.ssh/tehiku.pem staging.yml -t deploy,scale

**Production:**

    ansible-playbook -i inventory/ec2.py --vault-password-file=~/tehikudev/.vault_pass.txt --private-key=~/.ssh/tehiku.pem production.yml -t deploy,scale


The scale tag provisions Auto Scaling for the Media server.

Once the instances have been launched and provisioned, it's only necessary to run the code with the following tags,


**Staging:**

    ansible-playbook -i inventory/ec2.py --vault-password-file=~/tehikudev/.vault_pass.txt --private-key=~/.ssh/tehiku.pem staging.yml -t deploy

**Production:**

    ansible-playbook -i inventory/ec2.py --vault-password-file=~/tehikudev/.vault_pass.txt --private-key=~/.ssh/tehiku.pem production.yml -t deploy


Note that we need to pass the branch to the staging play as this allows us to test different branches on the same staging servers.

Ansible Vault
================
We store sensitive information for this deployment in an ansible vault.

To decrypt an encrypted file,

    ansible-vault decrypt env_vars/vault.yml 

To encrypt a file,

    ansible-vault encrypt env_vars/vault.yml