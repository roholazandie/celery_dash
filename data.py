import random


class DataStream:

    def __init__(self):
        pass

    def get(self):

        while True:
            yield random.uniform(0, 10)



if __name__ == "__main__":
    stream = DataStream()
    for s in stream.get():
        print(s)