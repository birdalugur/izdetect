import multiprocessing
import threading
from typing import List, Dict, Union, Any


class ServiceManager:
    def __init__(self, mode: str = "process"):
        if mode not in ("process", "thread"):
            raise ValueError("Mode must be either 'process' or 'thread'")
        self.mode = mode
        self.instances: List[Any] = []
        self.tasks: Dict[Any, Union[multiprocessing.Process, threading.Thread]] = {}

    def add_instance(self, instance: Any) -> None:
        self.instances.append(instance)

    def remove_instance(self, instance: Any) -> None:
        if instance in self.instances:
            self.instances.remove(instance)

    def _run_instance(self, instance: Any) -> None:
        if hasattr(instance, "run") and callable(instance.run):
            instance.run()
        else:
            raise AttributeError(f"The instance {instance} must have a 'run' method.")

    def start_all(self) -> None:
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

    def stop_all(self) -> None:
        for instance in self.instances:
            if hasattr(instance, "stop"):
                instance.stop()

        for instance, task in self.tasks.items():
            if self.mode == "process":
                if task.is_alive():
                    # Give it a moment to stop gracefully if implemented
                    task.join(timeout=1)
                    if task.is_alive():
                        task.terminate()
                        task.join()
            else:
                task.join(timeout=1)
        self.tasks.clear()
        self.instances.clear()
