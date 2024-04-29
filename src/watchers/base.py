from abc import ABCMeta, abstractmethod

class WatcherBase(metaclass=ABCMeta):
    """Base class for watchers."""

    @abstractmethod
    def start(self):
        """Start watcher."""
        
    @abstractmethod
    def zorb(self):
        """Absorb new events."""