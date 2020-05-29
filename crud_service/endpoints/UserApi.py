from datetime import datetime
from flask_restful import Resource, reqparse, fields, marshal_with, marshal
from database.data import User
from flask import request
import dateutil.parser

user_fields = {
    'id': fields.String(),
    'creation_timestamp': fields.DateTime(dt_format='iso8601'),
    'modified_timestamp': fields.DateTime(dt_format='iso8601'),
    'first_name': fields.String(),
    'last_name': fields.String(),

}

parser = reqparse.RequestParser()
parser.add_argument('id', type=str)
parser.add_argument('creation_timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('modified_timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('first_name', type=str)
parser.add_argument('last_name', type=str)


class UserApi(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        return User.objects().get(id=user_id)

    @marshal_with(user_fields)
    def delete(self, user_id):
        return User.objects().get(id=user_id)

    @marshal_with(user_fields)
    def put(self, user_id):
        user = User(**parser.parse_args())
        user.id = user_id
        User.objects().get(id=user_id).update(user)
        return User.objects().get(id=user_id)


class UserListApi(Resource):
    @marshal_with(user_fields)
    def get(self):
        user_id = request.args.get('user_id')
        page = int(request.args.get('page', 0))
        size = int(request.args.get('size', 10))
        objs = User.objects
        if user_id: objs = objs.filter(Q(user_id=user_id))
        page = objs[page * size:page * size + size]
        return list(page)

    @marshal_with(user_fields)
    def post(self):
        user = User(**parser.parse_args())
        user.save()
        return user
