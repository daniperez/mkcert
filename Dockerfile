FROM python:2.7.8

MAINTAINER Dani Perez

ADD mkcert.py /app/mkcert.py

ENTRYPOINT ["/app/mkcert.py"]

# Needed by keytool
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-7-jdk

ADD ca.cnf /app/ca.cnf


