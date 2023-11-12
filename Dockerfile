FROM python:3.11

COPY . /automata
WORKDIR /automata
RUN ["pip", "install", "-r", "requirements.txt"]

RUN ["chmod", "+x", "docker-entrypoint.sh"]
ENTRYPOINT ["sh", "docker-entrypoint.sh"]