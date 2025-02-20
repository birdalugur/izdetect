import multiprocessing
import threading
import time


class Runner:
    def __init__(self, mode="process"):
        if mode not in ("process", "thread"):
            raise ValueError("Mode must be either 'process' or 'thread'")
        self.mode = mode
        self.instances = []
        self.tasks = {}

    def add_instance(self, instance):
        self.instances.append(instance)

    def remove_instance(self, instance):
        if instance in self.instances:
            self.instances.remove(instance)

    def _run_instance(self, instance):
        if hasattr(instance, "run") and callable(instance.run):
            instance.run()
        else:
            raise AttributeError(f"The class {instance} must have a 'run' method.")

    def start_all(self):
        self.tasks = {}
        for instance in self.instances:
            if self.mode == "process":
                task = multiprocessing.Process(
                    target=self._run_instance, args=(instance,)
                )
            else:
                task = threading.Thread(target=self._run_instance, args=(instance,))
            task.start()
            self.tasks[instance] = task

    def stop_all(self):
        for instance in self.instances:
            if hasattr(instance, "stop"):
                instance.stop()

        for instance, task in self.tasks.items():
            if self.mode == "process":
                if task.is_alive():
                    task.terminate()
            else:
                task.join(timeout=1)
        self.tasks.clear()


if __name__ == "__main__":
    mode = "thread"
    manager = Runner(mode=mode)

    from frame_producer import FrameProducer
    from inference import Inference

    if mode == "process":
        task1 = FrameProducer(
            video_source="rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10",
            output_queue="camera1",
        )
        task2 = FrameProducer(
            video_source="rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10",
            output_queue="camera2",
        )
    else:
        task1 = Inference(
            input_queue="camera1",
            output_queue="inference1",
            image_bytes_queue="camera1_inf",
        )
        task2 = Inference(
            input_queue="camera2",
            output_queue="inference2",
            image_bytes_queue="camera2_inf",
        )

    manager.add_instance(task1)
    manager.add_instance(task2)
    manager.start_all()
    time.sleep(15)
    manager.stop_all()
    print("All operations have been stopped.")
