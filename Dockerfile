#FROM alfioemanuele/jorvik-docker-base:latest

FROM python:3.5
ENV PYTHONUNBUFFERED 1

ADD . /tmp
WORKDIR /tmp

# Installa tutti i requisiti Ubuntu
RUN apt-get update
RUN wget https://raw.githubusercontent.com/CroceRossaItaliana/jorvik-docker-base/2e0c524a41bcb86632930a02aa39009cf008a8b8/apt-dependencies.txt
RUN apt-get --assume-yes install `cat apt-dependencies.txt | grep -v "#" | xargs`
# actually not deleting the file, to fix
RUN rm apt-dependencies.txt

# Scarica e installa i requisiti PIP da CroceRossaItalian/jorvik (branch master)
RUN pip install -r https://raw.githubusercontent.com/CroceRossaItaliana/jorvik/master/requirements.txt

# Working directory
RUN mkdir /code
ADD . /code/
WORKDIR /code

# Entrypoint
RUN chmod +x ./config/docker-entrypoint.sh

ENTRYPOINT ["bash", "./config/docker-entrypoint.sh"]

# Start development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
