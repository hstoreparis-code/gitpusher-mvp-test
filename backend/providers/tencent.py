from typing import Optional
from .base_provider import BaseGitProvider, RepoInfo

class TencentProvider(BaseGitProvider):
    """Tencent Cloud Coding provider."""
    
    @property
    def provider_name(self) -> str:
        return "tencent"
    
    async def create_repo(self, token: str, name: str, description: Optional[str] = None, private: bool = False) -> RepoInfo:
        """Create Tencent Coding repository."""
        raise NotImplementedError("Tencent Coding requires Tencent Cloud SDK")
    
    async def put_file(self, token: str, repo_full_name: str, path: str, content_bytes: bytes, message: str) -> dict:
        raise NotImplementedError("Tencent - use git push")
    
    async def get_user_info(self, token: str) -> dict:
        return {"provider": "tencent", "note": "Requires Tencent credentials"}
    
    async def list_repos(self, token: str, limit: int = 100) -> list:
        return []
