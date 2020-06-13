import pickle
from abc import ABC
from dataclasses import dataclass


@dataclass
class Data(ABC):
    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

