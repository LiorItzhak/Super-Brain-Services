FROM python:3.8.3-slim-buster

COPY ./crud_service /code/crud_service
RUN pip3 install -r /code/crud_service/requirements.txt

RUN chmod +x /code/
ENV PYTONPATH /code

CMD [ "python", "./code/crud_service/CrudApp.py"]