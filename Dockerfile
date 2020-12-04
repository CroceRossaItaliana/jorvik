FROM git.cri.it/gaia/gaiabase:latest

# Working directory
RUN mkdir /code
COPY requirements.txt /code/
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /code/

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

# Entrypoint
RUN chmod +x ./config/docker-entrypoint.sh

RUN cp libgeos.py /usr/local/lib/python3.5/site-packages/django/contrib/gis/geos/libgeos.py

ENTRYPOINT ["bash", "./config/docker-entrypoint.sh"]

# Start development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
