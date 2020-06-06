FROM python:3.8.3-buster

COPY ./crud_service/requirements.txt /code/crud_service/requirements.txt
RUN pip3 install -r /code/crud_service/requirements.txt

COPY ./crud_service /code/crud_service

RUN chmod +x /code/

CMD [ "python", "./code/crud_service/CrudApp.py"]