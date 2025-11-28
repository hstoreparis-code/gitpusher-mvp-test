import httpx
import base64
from typing import Optional
from .base_provider import BaseGitProvider, RepoInfo

class GitHubProvider(BaseGitProvider):
    """GitHub provider implementation."""
    
    BASE_URL = "https://api.github.com"
    
    @property
    def provider_name(self) -> str:
        return "github"
    
    async def create_repo(self, token: str, name: str, description: Optional[str] = None, private: bool = False) -> RepoInfo:
        """Create a GitHub repository."""
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{self.BASE_URL}/user/repos",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "name": name,
                    "description": description or f"Repository {name}",
                    "private": private,
                    "auto_init": False
                },
                timeout=30
            )
            
            if res.status_code not in [200, 201]:
                raise Exception(f"GitHub API error: {res.status_code} - {res.text}")
            
            data = res.json()
            return RepoInfo(
                url=data["html_url"],
                full_name=data["full_name"],
                owner=data["owner"]["login"],
                name=data["name"],
                clone_url=data["clone_url"],
                provider="github"
            )
    
    async def put_file(self, token: str, repo_full_name: str, path: str, content_bytes: bytes, message: str) -> dict:
        """Upload a file to GitHub repo."""
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")
        
        async with httpx.AsyncClient() as client:
            res = await client.put(
                f"{self.BASE_URL}/repos/{repo_full_name}/contents/{path}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={"message": message, "content": content_b64},
                timeout=30
            )
            
            if res.status_code not in [200, 201]:
                raise Exception(f"GitHub file upload error: {res.status_code} - {res.text}")
            
            return res.json()
    
    async def get_user_info(self, token: str) -> dict:
        """Get GitHub user info."""
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/user",
                headers={"Authorization": f"Bearer {token}"},
                timeout=20
            )
            
            if res.status_code != 200:
                raise Exception(f"GitHub API error: {res.status_code}")
            
            return res.json()
    
    async def list_repos(self, token: str, limit: int = 100) -> list:
        """List user's GitHub repositories."""
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/user/repos",
                headers={"Authorization": f"Bearer {token}"},
                params={"per_page": min(limit, 100), "sort": "updated"},
                timeout=20
            )
            
            if res.status_code != 200:
                raise Exception(f"GitHub API error: {res.status_code}")
            
            return res.json()
