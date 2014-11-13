FROM python:2.7.8

MAINTAINER Dani Perez

# Needed by keytool
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-7-jdk

ADD mkcert.py /app/mkcert.py

ENTRYPOINT ["/app/mkcert.py"]
