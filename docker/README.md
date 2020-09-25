We're working on porting local development to Docker. Please checkout the `docker` branch. You must have docker installed for this to work.

Theoretically all you need to do is:
```bash
git clone https://github.com/TeHikuMedia/corpora.git
cd corpora
git checkout docker
docker pull tehiku/corpora:local-dev
docker-compose up
```
Then visit https://localhost:8002/ to access the Django site. You'll need to login and create some things in the databse to get started.

1. https://localhost:8002/admin, the default username and passwords are `docker` and `password` respectively.
2. In particular, you'll want to add a License, https://localhost:8002/admin/license/license/add/,
3. and associate that with a Django Site, https://localhost:8002/admin/license/sitelicense/add/.

The license will show up when users start to record. How and why we collect data is essential to this project. See the "License: Kaitiakitanga" below.

## Building/Updating the docker containers

To build the docker containers you need to be in the root project directory and run,
```bash
docker-compose build
```
This modifies a canonical postgresql docker image to support unaccent of strings for searching. It also builds the docker image for this repository. This calls the `initialise` service which does some django management commands.