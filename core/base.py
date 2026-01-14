from abc import ABC, abstractmethod
from typing import Optional
from core.interfaces import MessageBroker

class Service(ABC):
    """
    Abstract Base Class for all services.
    Adheres to DIP: Depends on abstractions (MessageBroker), not concrete implementations (Redis).
    """

    def __init__(self, message_broker: Optional[MessageBroker] = None):
        self.message_broker = message_broker

    @abstractmethod
    def run(self):
        """Main execution loop for the service."""
        pass

    @abstractmethod
    def stop(self):
        """Signals the service to stop."""
        pass
