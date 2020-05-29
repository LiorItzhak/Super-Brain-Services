from flask import Flask
from flask_restful import Api
from TimelineApi import TimelineApi

app = Flask(__name__)  # Create a Flask WSGI application

api = Api(app)  # Create a Flask-RESTPlus API
api.add_resource(TimelineApi, '/timeline/<user_id>')

if __name__ == '__main__':
    app.run(debug=True)  # Start a development server
