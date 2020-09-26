# Script to rebuild our docker image for deployment.
docker build . -t corpora-deploy
$(aws ecr get-login --no-include-email)
docker tag corpora-deploy 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
docker push 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
docker build . -t corpora-deploy --file gitactions.Dockerfile
docker tag corpora-deploy 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
docker push 473856431958.dkr.ecr.ap-southeast-2.amazonaws.com/corpora/deploy
