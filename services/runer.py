import multiprocessing
import time

from frame_producer import FrameProducer
import redis


class ParallelRunner:
    def __init__(self):
        self.instances = []
        self.processes = {}

    def add_instance(self, instance):
        self.instances.append(instance)

    def remove_instance(self, instance):
        if instance in self.instances:
            self.instances.remove(instance)

    def _run_instance(self, instance):
        if hasattr(instance, "run") and callable(instance.run):
            instance.run()
        else:
            raise AttributeError(f"{instance} sinifi 'run' metoduna sahip olmalidir.")

    def start_all(self):
        self.processes = {}
        for instance in self.instances:
            process = multiprocessing.Process(
                target=self._run_instance, args=(instance,)
            )
            process.start()
            self.processes[instance] = process

    def stop_all(self):
        for instance, process in self.processes.items():
            if process.is_alive():
                process.terminate()
        self.processes.clear()


if __name__ == "__main__":
    manager = ParallelRunner()

    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    task1 = FrameProducer(
        video_source="rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10",
        output_queue="camera1",
        redis_client=redis_client,
    )
    task2 = FrameProducer(
        video_source="rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10",
        output_queue="camera2",
        redis_client=redis_client,
    )
    task3 = FrameProducer(
        video_source="/home/birdal/izdetect/sahil.mp4",
        output_queue="camera3",
        redis_client=redis_client,
    )

    manager.add_instance(task1)
    manager.add_instance(task2)
    # manager.add_instance(task3)

    manager.start_all()
    time.sleep(60)
    manager.stop_all()
    print("Tüm işlemler durduruldu.")
