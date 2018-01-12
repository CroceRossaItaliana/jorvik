FROM alfioemanuele/jorvik-docker-base:latest

# Working directory
RUN mkdir /code
ADD . /code/

# Entrypoint
RUN chmod +x ./config/docker-entrypoint.sh
WORKDIR /code
ENTRYPOINT ["bash", "./config/docker-entrypoint.sh"]

# Start development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
