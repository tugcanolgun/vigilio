FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && apt-get install -y --no-install-recommends build-essential git

# cleaning up unused files
RUN  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
COPY ./requirements/prod.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./compose/dev/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/dev/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./compose/dev/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

WORKDIR /app

RUN useradd -d /app -m -s /bin/bash vigilio && echo "vigilio:vigilio" | chpasswd && adduser vigilio sudo

# Make the files owned by tester
RUN chown -R vigilio:vigilio /app

# Switch to your new user in the docker image
USER vigilio

ENTRYPOINT ["/entrypoint"]
