FROM python:3.8.3-slim-buster

COPY ./timeline_service/requirements.txt /code/timeline_service/requirements.txt
RUN pip3 install -r /code/timeline_service/requirements.txt

COPY ./timeline_service /code/timeline_service

RUN chmod +x /code/

CMD [ "python", "./code/timeline_service/TimelineApp.py"]