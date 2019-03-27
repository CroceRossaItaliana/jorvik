# FROM alfioemanuele/jorvik-docker-base:latest
FROM python:3.5
ENV PYTHONBUFFERED 1

# Working directory
RUN mkdir /code
ADD . /code/
WORKDIR /code

# Entrypoint
RUN chmod +x ./config/docker-entrypoint.sh

ENTRYPOINT ["bash", "./config/docker-entrypoint.sh"]

# Start development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
