 # TODO replace w/ ubuntu and install geolibs
 # see https://docs.djangoproject.com/en/1.11/ref/contrib/gis/install/geolibs/#installing-geospatial-libraries
 FROM python:3
 ENV PYTHONUNBUFFERED 1
 RUN apt-get update; apt-get --assume-yes install binutils libproj-dev gdal-bin
 RUN mkdir /code
 WORKDIR /code
 ADD . /code/
 RUN pip install -r requirements.txt
