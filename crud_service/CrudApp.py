from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api
from endpoints.ActivityApi import ActivityListApi, ActivityApi
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
api.add_resource(ActivityApi, '/activity/<activity_id>')
api.add_resource(ActivityListApi, '/activity')
api.add_resource(UserApi, '/user/<user_id>')
api.add_resource(UserListApi, '/user')


@app.route('/')
def index():
    return "CrudApp"


if __name__ == '__main__':
    app.run(debug=True)  # Start a development server
