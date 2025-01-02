import time


class ProcessingTimer:
    def __init__(self):
        self.times = {}
        self.start_times = {}

    def start(self, key):
        self.start_times[key] = time.time()

    def stop(self, key):
        if key in self.start_times:
            elapsed_time = time.time() - self.start_times[key]
            self.times[key] = self.times.get(key, 0) + elapsed_time
            del self.start_times[key]

    def get_total_time(self):
        return sum(self.times.values())

    def get_time(self, key):
        return self.times.get(key, 0)

    def print_summary(self):
        total_time = self.get_total_time()
        print(f"Total time: {total_time:.2f} seconds")
        for key, elapsed in self.times.items():
            print(f"Total {key} time: {elapsed:.2f} seconds")


            