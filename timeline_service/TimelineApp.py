import requests
from flask import Flask
from flask_restful import Api
from TimelineApi import TimelineApi

app = Flask(__name__)  # Create a Flask WSGI application

api = Api(app)  # Create a Flask-RESTPlus API
api.add_resource(TimelineApi, '/timeline/<user_id>')

@app.route('/')
def index():
    return "TimelineApp"

@app.route('/liveness_check')
def liveness_check():
    try:
        return requests.get('http://crud:5000').text
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Start a development server
