#Any tool that we define that will act as our Vector Search Service must inherit from this Blueprint class and must contain the search function.

from abc import ABC, abstractmethod
from typing import Any , Dict , List

#Define the interface class, inheriting from the ABC

class VectorStoreInterface(ABC):
    @abstractmethod
    async def search(self , query : str , n_results : int = 3) -> List[Dict[str , Any]]:
        pass


