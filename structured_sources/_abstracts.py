from abc import ABC, abstractmethod
class _abstractSource(ABC):
    @abstractmethod
    def bootstrap_connection(self, connection_kwargs):
        pass
    @abstractmethod
    def get_query_results(self, query):
        pass

class _abstractSourceConnection(ABC):
    @abstractmethod
    def get_query_types(self):
        pass
    @abstractmethod
    def prepare_query(self, query_type, **kwargs):
        pass
    @abstractmethod
    def execute_query(self, prepared_query, **kwargs):
        pass
