from datetime import datetime
from flask_restful import Resource, reqparse, fields, marshal_with, marshal
from database.data import Person
import dateutil.parser
from mongoengine import Q

from flask import request

person_fields = {
    'id': fields.String(),
    'user_id': fields.String(),
    'creation_timestamp': fields.DateTime(dt_format='iso8601'),
    'modified_timestamp': fields.DateTime(dt_format='iso8601'),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'image_features': fields.List(fields.List(fields.Float)),
    'description': fields.String()
}


def arrayType(value, name):
    full_json_data = request.get_json()
    my_list = full_json_data[name]
    if not isinstance(my_list, list):
        raise ValueError("The parameter " + name + " is not a valid array")
    return my_list


parser = reqparse.RequestParser()
parser.add_argument('id', type=str)
parser.add_argument('user_id', type=str)
parser.add_argument('creation_timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('modified_timestamp', type=lambda x: dateutil.parser.parse(x))
parser.add_argument('first_name', type=str)
parser.add_argument('last_name', type=str)
parser.add_argument('image_features', type=arrayType)
parser.add_argument('description', type=str)


class PersonApi(Resource):
    @marshal_with(person_fields)
    def get(self, person_id):
        return Person.objects().get(id=person_id)

    @marshal_with(person_fields)
    def delete(self, person_id):
        return Person.objects().get(id=person_id)

    @marshal_with(person_fields)
    def put(self, person_id):
        person = Person(**parser.parse_args())
        person.id = person_id
        Person.objects().get(id=person_id).update(person)
        return Person.objects().get(id=person_id)


class PersonListApi(Resource):
    @marshal_with(person_fields)
    def get(self):
        modified_after = request.args.get('modified_after', None)
        if modified_after: modified_after = dateutil.parser.parse(modified_after)

        user_id = request.args.get('user_id', None)
        page = int(request.args.get('page', 0))
        size = int(request.args.get('size', 10))

        objs = Person.objects
        if user_id: objs = objs.filter(Q(user_id=user_id))
        if modified_after:  objs = objs.filter(Q(modified_timestamp__gt=modified_after))

        page = objs[page * size:page * size + size]
        return list(page)

    @marshal_with(person_fields)
    def post(self):
        person = Person(**parser.parse_args())
        person.save()
        return person
