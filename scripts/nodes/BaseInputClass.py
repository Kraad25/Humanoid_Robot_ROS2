from abc import ABC, abstractmethod

class BaseInput(ABC):
    
    @abstractmethod
    def get_input(self):
        pass

    @abstractmethod
    def clean_input(self):
        pass

    @abstractmethod
    def publish_cleaned_input(self, msg):
        pass