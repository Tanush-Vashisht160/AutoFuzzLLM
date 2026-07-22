from abc import ABC, abstractmethod


class BaseJudge(ABC):

    @abstractmethod
    def evaluate(self, prompt, response):
        pass