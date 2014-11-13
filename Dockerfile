FROM python:2.7.8

MAINTAINER Dani Perez

ADD mkcert.py /app/mkcert.py

ENTRYPOINT ["/app/mkcert.py"]:
