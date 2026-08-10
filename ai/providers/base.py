from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Base interface for all AI quote providers."""

    @abstractmethod
    def is_available(self):
        """Return True when the provider is configured and available."""
        raise NotImplementedError

    @abstractmethod
    def generate_quote(self, service_request):
        """Generate a quote for the given service request."""
        raise NotImplementedError
