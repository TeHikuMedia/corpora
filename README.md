
![Build staging vue client](https://github.com/TeHikuMedia/corpora/workflows/Build%20staging%20vue%20client/badge.svg)
![Deploy Staging](https://github.com/TeHikuMedia/corpora/workflows/Deploy%20Staging/badge.svg)

![Build production vue client](https://github.com/TeHikuMedia/corpora/workflows/Build%20production%20vue%20client/badge.svg)
![Deploy Production](https://github.com/TeHikuMedia/corpora/workflows/Deploy%20Production/badge.svg)

# corpora
corpora is a Django project for gathering corpora for different languages. It's been built to support any number of languages with Te Reo Māori as its first.

The goal of this app is to streamline corpora gathering for minority languages so that dictation, personal assistants, and 
other technologies can work in te reo Māori, ʻōlelo Hawaiʻi, and other indigenous languages.

## Supported Languages
- Māori

You can help us add more languages by translating this app. The current project is live at https://koreromaori.com/. If you'd like to lead a copora gathering campaign for your language, get in touch as we'd love to help.

# Getting Started

## Local Development
Please see `corpora-deploy` for details on getting a local environment running.

## Docker
We've temporarily stopped working on a docker port. The docs below are kept for reference.

### Running Django manually
You might need to run django administration commands such as makemessages which is used to create locale files for multi-language support. In order to do this you should mount your repo into the docker image when you run it so those changes are reflected in your local files,

```bash
docker run -it --env-file=local.env --mount type=bind,source="$(pwd)"/corpora,target=/webapp/corpora/corpora tehiku/corpora:local-dev /bin/bash
```
The `local.env` file has all the environment variables required to get django running.

### Docker Images
Currently we are hosting the docker images here: https://hub.docker.com/repository/docker/tehiku/corpora

We probably want some more docs here about different docker images for say different language and/or environments.

# Kōrero Māori
Kōrero Māori is the project that's funding the build of corpora. Kōrero Māori is an initiative started by Te Hiku Media and supported by a number of organizations. The goal is to train machines to transcribe thousands of hours or native language speaker audio recordings to make native te reo Māori more accessible to language learners as our native speaker population is in decline.

We are always looking for more support either financially or through in kind contributions. If you're keen to get involved please get in touch by emailing us at koreromaori@tehiku.nz.

## Current Funding
- Papa Reo, MBIE SSIF, Data Science Platform - https://papareo.nz

## Past Funding
- Ka Hao Fund, Te Puni Kōkiri - https://www.tpk.govt.nz/en

## Project Partners
- Te Reo Irirangi o Te Hiku o Te Ika (Te Hiku Media) - https://tehiku.nz/
- Dragonfly Data Science - https://www.dragonfly.co.nz/
- Te Pūnaha Matatini - http://www.tepunahamatatini.ac.nz/

# Contact
Make an issue or send an email to koreromaori@tehiku.nz.

# License: Kaitiakitanga 
Corpora (the code in this repository) is copyrighted by Te Reo Irirangi o Te Hiku o Te Ika (Te Hiku Media) under our Kaitiakitanga License. Kaitiaki is a Māori word  without specific English translation, but its meaning is similar to the words guardian, protector, and custodian . In this context we protect the code in this repository and will provide access to the code as we deem fit through our tikanga (Māori customs and protocols).

While we recognize the importance of open source technology, we're mindful that the majority of tangata whenua and other indigenous peoples may not have access to the resources that enable them to benefit from open source technologies. As tangata whenua, our ability to grow, develop, and innovate has been stymied through colonization. We must protect our ability to grow as tangata whenua.  By simply open sourcing our data and knowledge, we further allow ourselves to be colonised digitally in the modern world.

The Kaitiakitanga License is a work in progress. It's a living license. It will evolve as we see fit. We hope to develop a license that is an international example for indigenous people's retention of mana over data and other intellectual property in a Western construct.

While the Kaitiakitanga License is still under development, here are some of its terms:
1. You must contact us and seek permission to access, use, contribute towards, or modify code in this repository;
2. You may not use code in this repository or any derivations for commercial purposes unless we explicitly grant you the right to do so;
3. All works derived from code in this repository are bound by the Kaitiakitanga License;
4. All works that make use of any code in this repository are bound by the Kaitiakitanga License.

# This project is funded through past grievances committed by the Crown
This project was made possible by funds that support the revitalisation of te reo Māori and that supports the growth of Māori people and organizations in the ICT industry. These funds were made available because the New Zealand Government failed to uphold The Treaty of Waitangi (https://teara.govt.nz/en/treaty-of-waitangi). Te reo Māori was onced banned in schools, with some students being physically abused for speaking te reo Māori. The Crown recognizes its unlawful behaviour in disenfranchising the tangata whenua of New Zealand, and legislation like the Māori Language Act have enabled steps towards the revitalisation of te reo Māori. 

