import threading
import time

from inference import Inference
import redis


class ParallelRunner:
    def __init__(self):
        self.instances = []
        self.threads = {}

    def add_instance(self, instance):
        self.instances.append(instance)

    def remove_instance(self, instance):
        if instance in self.instances:
            self.instances.remove(instance)

    def _run_instance(self, instance):
        if hasattr(instance, "run") and callable(instance.run):
            instance.run()
        else:
            raise AttributeError(f"{instance} sınıfı 'run' metoduna sahip olmalıdır.")

    def start_all(self):
        self.threads = {}
        for instance in self.instances:
            thread = threading.Thread(target=self._run_instance, args=(instance,))
            thread.start()
            self.threads[instance] = thread

    def stop_all(self):
        for instance, thread in self.threads.items():
            thread.join(
                timeout=0
            )  # Thread'leri zorla kapatmak yerine zaman aşımı belirtiyoruz
        self.threads.clear()


if __name__ == "__main__":
    manager = ParallelRunner()

    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=False)
    task1 = Inference(
        input_queue="camera1",
        output_queue="inference1",
        image_bytes_queue="camera1_image_bytes",
        redis_client=redis_client,
    )
    task2 = Inference(
        input_queue="camera2",
        output_queue="inference2",
        image_bytes_queue="camera2_image_bytes",
        redis_client=redis_client,
    )
    task3 = Inference(
        input_queue="camera3",
        output_queue="inference3",
        image_bytes_queue="camera3_image_bytes",
        redis_client=redis_client,
    )

    manager.add_instance(task1)
    manager.add_instance(task2)
    manager.add_instance(task3)

    manager.start_all()
    time.sleep(10)
    # manager.stop_all()
    print("Tüm işlemler durduruldu.")
