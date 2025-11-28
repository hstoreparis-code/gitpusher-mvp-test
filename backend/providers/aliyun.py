from typing import Optional
from .base_provider import BaseGitProvider, RepoInfo

class AliyunProvider(BaseGitProvider):
    """Alibaba Cloud Code provider."""
    
    @property
    def provider_name(self) -> str:
        return "aliyun"
    
    async def create_repo(self, token: str, name: str, description: Optional[str] = None, private: bool = False) -> RepoInfo:
        """Create Aliyun Code repository."""
        raise NotImplementedError("Aliyun Code requires Alibaba Cloud SDK")
    
    async def put_file(self, token: str, repo_full_name: str, path: str, content_bytes: bytes, message: str) -> dict:
        raise NotImplementedError("Aliyun - use git push")
    
    async def get_user_info(self, token: str) -> dict:
        return {"provider": "aliyun", "note": "Requires Aliyun credentials"}
    
    async def list_repos(self, token: str, limit: int = 100) -> list:
        return []
