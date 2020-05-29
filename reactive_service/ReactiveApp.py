from sanic import Sanic
from sanic.response import json
from sanic import response
import asyncio
from kafka import KafkaConsumer

app = Sanic("hello_example")

@app.route("/")
async def test(request):
  return json({"hello": "world"})


@app.route("/register/<user_id>/<type>")
async def register(request, user_id, type):
    async def streaming_fn(response):
        consumer = KafkaConsumer(
            f'activity_{user_id}_{type}',
            bootstrap_servers=['localhost:9092'],
            enable_auto_commit=True,
            group_id='my-group')

        for message in consumer:
            message = message.value
            print(message)
            await response.write(message)
    return response.stream(streaming_fn, content_type='text/plain')




if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)