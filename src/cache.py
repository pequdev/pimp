import json
import os

class Cache:
    def __init__(self, cache_file='data/cache.json'):
        self.cache_file = cache_file
        self.data = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as file:
                return json.load(file)
        return {}

    def save_cache(self):
        with open(self.cache_file, 'w') as file:
            json.dump(self.data, file)

    def get(self, query):
        return self.data.get(query)

    def set(self, query, result):
        self.data[query] = result