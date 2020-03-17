FROM python:latest

LABEL maintainer="louis@orleans.io"

# user-configurable vars
ENV DISCORD_TOKEN bot-token
ENV POSTGRES_HOST hostname
ENV POSTGRES_PORT 5432
ENV POSTGRES_USER postgres
ENV POSTGRES_PASS password

COPY Dockerfile /virginity-bot/
COPY README.md /virginity-bot/
COPY LICENSE /virginity-bot/
COPY requirements.txt /virginity-bot/
COPY *.py /virginity-bot/

WORKDIR /virginity-bot

RUN pip install -r requirements.txt

CMD python bot.py

# HEALTHCHECK CMD mcstatus localhost status || exit 1
