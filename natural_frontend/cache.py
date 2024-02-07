import json
import os
import time


class Cache:
    def __init__(self, directory, cache_expiry_time):
        self.directory = directory
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except:
                pass
        self.expiry_time = cache_expiry_time  # 600 seconds cache expiration time

    def get_file_path(self, key):
        filename = f"{key}.json"
        return os.path.join(self.directory, filename)

    def get(self, key):
        file_path = self.get_file_path(key)
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                cached = json.load(file)
                if time.time() - cached["time"] < self.expiry_time:
                    return cached["data"]
        return None

    def set(self, key, value):
        file_path = self.get_file_path(key)
        try:
            with open(file_path, "w") as file:
                json.dump({"data": value, "time": time.time()}, file)
        except:
            pass
