import os
from datetime import datetime
from logging import getLogger
from time import sleep

from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with, marshal
from kafka.errors import NoBrokersAvailable
from mongoengine import Q
import dateutil.parser
from database.data import Event
from kafka import KafkaProducer
import json
import threading

# datetime.strptime(modified_after, "%Y-%m-%dT%H:%M:%S.%f")

event_fields = {
    'id': fields.String(),
    'user_id': fields.String(),
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'creation_timestamp': fields.DateTime(dt_format='iso8601'),
    'modified_timestamp': fields.DateTime(dt_format='iso8601'),
    'type': fields.String(),
    'data': fields.Raw()
}

parser = reqparse.RequestParser()
parser.add_argument('id', type=str)
parser.add_argument('user_id', type=str)
parser.add_argument('timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('creation_timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('modified_timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('type', type=str)
parser.add_argument('data', type=dict)

# producer = KafkaProducer(
#     bootstrap_servers="kafka-34f1d98c-sean98goldfarb-28b7.aivencloud.com:10402",
#     value_serializer=lambda x: json.dumps(x).encode('utf-8'),
#     security_protocol="SSL",
#     ssl_cafile="kafka_auth/ca.pem",
#     ssl_certfile="kafka_auth/service.cert",
#     ssl_keyfile="kafka_auth/service.key",
# )


class EventApi(Resource):
    @marshal_with(event_fields)
    def get(self, event_id):
        return Event.objects().get(id=event_id)

    @marshal_with(event_fields)
    def delete(self, event_id):
        return Event.objects().get(id=event_id)

    @marshal_with(event_fields)
    def put(self, event_id):
        event = Event(**parser.parse_args())
        event.id = event_id
        event.save()
        return event


class EventListApi(Resource):
    @marshal_with(event_fields)
    def get(self):
        modified_after = request.args.get('modified_after', None)
        if modified_after: modified_after = dateutil.parser.parse(modified_after)
        created_on = request.args.get('created_on')
        if created_on: created_on = dateutil.parser.parse(created_on)
        from_timestamp = request.args.get('from_timestamp')
        if from_timestamp: from_timestamp = dateutil.parser.parse(from_timestamp)
        to_timestamp = request.args.get('to_timestamp')
        if to_timestamp: to_timestamp = dateutil.parser.parse(to_timestamp)

        user_id = request.args.get('user_id', None)
        event_type = request.args.get('type', None)
        page = int(request.args.get('page', 0))
        size = int(request.args.get('size', 10))

        objs = Event.objects
        if user_id: objs = objs.filter(Q(user_id=user_id))
        if event_type: objs = objs.filter(Q(type=event_type))
        if modified_after:  objs = objs.filter(Q(modified_timestamp__gt=modified_after))
        if created_on:  objs = objs.filter(Q(creation_timestamp=created_on))
        if to_timestamp:  objs = objs.filter(Q(timestamp__lte=to_timestamp))
        if from_timestamp:  objs = objs.filter(Q(timestamp__gte=from_timestamp))
        page = objs[page * size:page * size + size]
        return list(page)

    @marshal_with(event_fields)
    def post(self):

        event = Event(**parser.parse_args())
        if not event.timestamp:
            event.timestamp = datetime.now()
        event.save()
        # producer.send('event', value=marshal(event, event_fields))
        return event
