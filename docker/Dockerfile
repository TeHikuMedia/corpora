# Use an official Python runtime as a parent image
FROM python:3.7.9-slim

# Install required system packages
RUN apt-get update && \
    apt-get -y install gcc
RUN apt-get -y install ffmpeg

# Bower stuff, which we need to get rid of
RUN apt-get -y install git
RUN apt-get -y install npm
RUN npm install -g bower 

# Required for compilemessages in django
RUN apt-get -y install gettext


# Create necessary folders and files
RUN mkdir /webapp
RUN mkdir /webapp/logs
RUN touch /webapp/logs/celery.log
RUN touch /webapp/logs/django.log
RUN mkdir /webapp/run/


# Install any needed packages specified in requirements.txt
COPY requirements.txt /webapp/corpora/
WORKDIR /webapp/corpora/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Temp hack to get things working
# We need to install the wahi-korero package
RUN pip install pydub webrtcvad

# Manual install wahi_korero
WORKDIR /webapp/corpora/corpora/
RUN curl -L -o wahi_korero.tar.gz https://github.com/TeHikuMedia/wahi-korero/archive/v0.5.1.tar.gz 
RUN tar -xzvf wahi_korero.tar.gz
RUN rm -rf wahi_korero
RUN mv wahi-korero-0.5.1/wahi_korero/ wahi_korero || true
RUN rm wahi_korero.tar.gz
RUN rm -r wahi-korero-0.5.1

# Make port 80 available to the world outside this container
# EXPOSE 80

# Finally, install the codebase and requirend ENV VARS
# Copy files over
COPY corpora /webapp/corpora/corpora
COPY local.env /webapp/local.env
COPY entry.sh /webapp/corpora/

COPY django.sh /webapp/django.sh
RUN /bin/sh /webapp/django.sh
