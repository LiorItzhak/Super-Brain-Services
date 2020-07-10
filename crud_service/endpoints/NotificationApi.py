import os
from datetime import datetime
from logging import getLogger
from time import sleep
from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with, marshal
from kafka.errors import NoBrokersAvailable
from mongoengine import Q
import dateutil.parser
from database.data import Notification
import json


notification_fields = {
    'id': fields.String(),
    'user_id': fields.String(),
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'creation_timestamp': fields.DateTime(dt_format='iso8601'),
    'modified_timestamp': fields.DateTime(dt_format='iso8601'),
    'type': fields.String(),
    'data': fields.Raw(),
    'is_active': fields.Boolean(),
    'notes': fields.String()
}

parser = reqparse.RequestParser()
parser.add_argument('id', type=str)
parser.add_argument('user_id', type=str)
parser.add_argument('timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('creation_timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('modified_timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('type', type=str)
parser.add_argument('data', type=dict)
parser.add_argument('is_active', type=bool)
parser.add_argument('notes', type=str)


class NotificationApi(Resource):
    @marshal_with(notification_fields)
    def get(self, notification_id):
        return Notification.objects().get(id=notification_id)

    @marshal_with(notification_fields)
    def delete(self, notification_id):
        return Notification.objects().get(id=notification_id)

    @marshal_with(notification_fields)
    def put(self, notification_id):
        notification = Notification(**parser.parse_args())
        notification.id = notification_id
        notification.save()
        return notification


class NotificationListApi(Resource):
    @marshal_with(notification_fields)
    def get(self):
        modified_after = request.args.get('modified_after', None)
        if modified_after: modified_after = dateutil.parser.parse(modified_after)
        created_on = request.args.get('created_on')
        if created_on: created_on = dateutil.parser.parse(created_on)
        from_timestamp = request.args.get('from_timestamp')
        if from_timestamp: from_timestamp = dateutil.parser.parse(from_timestamp)
        to_timestamp = request.args.get('to_timestamp')
        if to_timestamp: to_timestamp = dateutil.parser.parse(to_timestamp)

        is_active = request.args.get('is_active', None)
        user_id = request.args.get('user_id', None)
        notification_type = request.args.get('type', None)
        page = int(request.args.get('page', 0))
        size = int(request.args.get('size', 10))

        objs = Notification.objects
        if user_id: objs = objs.filter(Q(user_id=user_id))
        if notification_type: objs = objs.filter(Q(type=notification_type))
        if modified_after:  objs = objs.filter(Q(modified_timestamp__gt=modified_after))
        if created_on:  objs = objs.filter(Q(creation_timestamp=created_on))
        if to_timestamp:  objs = objs.filter(Q(timestamp__lte=to_timestamp))
        if from_timestamp:  objs = objs.filter(Q(timestamp__gte=from_timestamp))
        if is_active: objs = objs.filter(Q(is_active=from_timestamp))
        page = objs[page * size:page * size + size]
        return list(page)

    @marshal_with(notification_fields)
    def post(self):
        notification = Notification(**parser.parse_args())
        notification.save()
        return notification
