#FROM alfioemanuele/jorvik-docker-base:latest

#FROM python:3.5
FROM git.cri.it/gaia/gaiabase:latest

# Working directory
RUN mkdir /code
ADD . /code/
WORKDIR /code

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

# Entrypoint
RUN chmod +x ./config/docker-entrypoint.sh

RUN pip install --upgrade -r requirements.txt

ENTRYPOINT ["bash", "./config/docker-entrypoint.sh"]

# Start development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
