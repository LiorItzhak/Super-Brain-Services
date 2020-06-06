FROM python:3.8.3-slim-buster

#RUN apt-get update && \
#     apt-get install -y net-tools

RUN pip install gunicorn
COPY ./reactive_service/requirements.txt /code/reactive_service/requirements.txt
RUN pip3 install -r /code/reactive_service/requirements.txt

COPY ./reactive_service /code/reactive_service

RUN chmod +x /code/
ENV PYTONPATH /code

#CMD [ "gunicorn","-w 4", "./code/reactive_service/ReactiveApp.py:app"]

CMD [ "gunicorn","./code/reactive_service/ReactiveApp.py:app","--bind 0.0.0.0:1337","--worker-class sanic.worker.GunicornWorker"]