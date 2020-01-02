from celery import Celery
import time
import redis
import json
from plotly.utils import PlotlyJSONEncoder
from data import DataStream
import random
import numpy as np

app = Celery('sample', backend='redis', broker='redis://localhost:6379')
redis_instance = redis.StrictRedis.from_url('redis://localhost')

datastream = DataStream()

data = datastream.get()

@app.task
def add(x, y):
    time.sleep(10)
    return x + y

@app.task
def rand():
    time.sleep(2)
    return np.random.randn(1)[0]


@app.task
def model(m):
    print("dddd")
    time.sleep(1)
    gyrox_data = []
    # for i, m_gyro_x in enumerate(data):
    #     gyrox_data.append(m_gyro_x)
    #     print(m_gyro_x)
    #     if i> 2:
    #         break
    gyrox_data = [np.random.randn(1)[0] for i in range(5)]
    print(gyrox_data)

    redis_instance.hset("data",
                        "dataset",
                        json.dumps(
                            {"a": gyrox_data},
                            # This JSON Encoder will handle things like numpy arrays
                            # and datetimes
                            cls=PlotlyJSONEncoder,
                        )
    )

    return m

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1.0, model.s('d'), name='add every 1')


if __name__ == "__main__":
    #python sample.py worker -l info
    #python sample.py beat -l info
    #docker run -d -p 6379:6379 redis
    app.start()