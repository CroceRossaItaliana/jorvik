FROM alfioemanuele/jorvik-docker-base:latest

# Working directory
RUN mkdir /code
ADD . /code/
WORKDIR /code

# Entrypoint
RUN chmod +x ./config/docker-entrypoint.sh

ENTRYPOINT ["bash", "./config/docker-entrypoint.sh"]

# Start development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
