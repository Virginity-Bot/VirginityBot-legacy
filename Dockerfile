FROM python:3

LABEL maintainer="louis@orleans.io"

# user-configurable vars
ENV DISCORD_TOKEN bot-token
ENV POSTGRES_HOST hostname
ENV POSTGRES_PORT 5432
ENV POSTGRES_USER postgres
ENV POSTGRES_PASS password
ENV POINTS_PER_MINUTE 5
ENV BOT_SCORE_MULTIPLIER 0.5

RUN apt-get update && apt-get install -y ffmpeg

# TODO: move this to another container
COPY crontab /etc/cron.d/virgin-cron
RUN chmod 0644 /etc/cron.d/virgin-cron
RUN service cron start

RUN useradd --create-home virginitybot
WORKDIR /home/virginitybot
USER virginitybot

COPY Dockerfile ./
COPY README.md ./
COPY LICENSE ./
COPY requirements.txt ./
COPY *.py ./

RUN pip install -r requirements.txt

CMD python -u main.py

# HEALTHCHECK CMD mcstatus localhost status || exit 1
