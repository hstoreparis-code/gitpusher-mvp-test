from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class RepoInfo:
    url: str
    full_name: str
    owner: str
    name: str
    clone_url: str
    provider: str

class BaseGitProvider(ABC):
    """Base class for all Git providers."""
    
    @abstractmethod
    async def create_repo(self, token: str, name: str, description: Optional[str] = None, private: bool = False) -> RepoInfo:
        """Create a new repository."""
        pass
    
    @abstractmethod
    async def put_file(self, token: str, repo_full_name: str, path: str, content_bytes: bytes, message: str) -> dict:
        """Upload a file to repository."""
        pass
    
    @abstractmethod
    async def get_user_info(self, token: str) -> dict:
        """Get user information from provider."""
        pass
    
    @abstractmethod
    async def list_repos(self, token: str, limit: int = 100) -> list:
        """List user's repositories."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name identifier."""
        pass
