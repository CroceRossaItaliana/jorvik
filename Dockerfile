FROM alfioemanuele/gaia-jorvik

RUN rm -rf /vagrant

RUN rm /usr/bin/python3
RUN ln -s /usr/bin/python3.5 /usr/bin/python3

ADD . /vagrant
WORKDIR /vagrant

#ENV PYTHONPATH \$PYTHONPATH:/usr/local/lib/python3.5/dist-packages
RUN pip3 install -r requirements.txt

RUN cp /vagrant/config/pgsql.cnf.sample /vagrant/config/pgsql.cnf
RUN sed -i -e 's/host = localhost/host = db/' /vagrant/config/pgsql.cnf
RUN sed -i -e 's/user = postgres/user = jorvik/' /vagrant/config/pgsql.cnf
RUN sed -i -e 's/password =/password = jorvik/' /vagrant/config/pgsql.cnf

EXPOSE 8000

CMD python3 manage.py migrate --noinput && python3 manage.py collectstatic --noinput && python3 manage.py runserver 0.0.0.0:8000