from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api
from endpoints.EventApi import EventListApi, EventApi
from endpoints.NotificationApi import NotificationListApi, NotificationApi

from endpoints.PersonApi import PersonApi, PersonListApi
from endpoints.UserApi import UserListApi, UserApi

app = Flask(__name__)  # Create a Flask WSGI application

app.config['MONGODB_SETTINGS'] = {
    'db': 'Db',
    'host': 'mongodb+srv://admin:1234@cluster0-jabzz.mongodb.net/Db?retryWrites=true&w=majority'
}
db = MongoEngine()
db.init_app(app)

api = Api(app)  # Create a Flask-RESTPlus API
api.add_resource(PersonApi, '/person/<person_id>')
api.add_resource(PersonListApi, '/person')
api.add_resource(EventApi, '/event/<event_id>')
api.add_resource(EventListApi, '/event')
api.add_resource(UserApi, '/user/<user_id>')
api.add_resource(UserListApi, '/user')
api.add_resource(NotificationApi, '/notification/<notification_id>')
api.add_resource(NotificationListApi, '/notification')

@app.route('/')
def index():
    return "CrudApp"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Start a development server
