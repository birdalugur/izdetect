import time
import threading
import redis


class Foo:
    def __init__(self, name: str):
        self.name = name

        self.redis_client = redis.Redis(host="localhost", port=6379)
        self.value = 5

        self.update_thread = threading.Thread(target=self.update, daemon=True)
        self.update_thread.start()

    def update(self):
        while True:
            new_value = int(self.redis_client.get("value"))
            if new_value != self.value:
                print("new value detected {}".format(new_value))
                self.value = new_value
            time.sleep(2)

    def run(self):
        while True:
            print("{}: Value: {}".format(self.name, self.value))
            time.sleep(2)


if __name__ == "__main__":
    import multiprocessing

    foo1 = Foo(name="foo1")
    foo2 = Foo(name="foo2")

    process1 = multiprocessing.Process(target=foo1.run)
    process2 = multiprocessing.Process(target=foo2.run)

    process1.start()
    process2.start()
