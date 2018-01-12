FROM alfioemanuele/jorvik-docker-base:latest

# Working directory

# Entrypoint
COPY ./config/docker-entrypoint.sh /tmp
RUN chmod +x /tmp/docker-entrypoint.sh
ENTRYPOINT ["bash", "/tmp/docker-entrypoint.sh"]

# Start development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
