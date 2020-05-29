from sanic import Sanic
from sanic.response import json
from sanic import response
import asyncio
from kafka import KafkaConsumer
import threading

app = Sanic("hello_example")


@app.route("/")
async def test(request):
    return json({"hello": "world"})


@app.route("/register/<user_id>/<type>")
async def register(request, user_id, type):
    async def streaming_fn(response):
        print(f'{user_id} {threading.current_thread().ident}')
        topic = f'activity{user_id}{type}'
        print(topic)
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            enable_auto_commit=True,
            group_id='my-group')
        #
        for message in consumer:
            print(f'hi {user_id}')
            message = message.value
            print(message)
            await response.write(message)

    return response.stream(streaming_fn, content_type='text/plain')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, workers=8)
