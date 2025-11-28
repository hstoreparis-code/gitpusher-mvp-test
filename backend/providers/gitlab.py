import httpx
import base64
from typing import Optional
from .base_provider import BaseGitProvider, RepoInfo

class GitLabProvider(BaseGitProvider):
    """GitLab provider implementation."""
    
    BASE_URL = "https://gitlab.com/api/v4"
    
    @property
    def provider_name(self) -> str:
        return "gitlab"
    
    async def create_repo(self, token: str, name: str, description: Optional[str] = None, private: bool = False) -> RepoInfo:
        """Create a GitLab project."""
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{self.BASE_URL}/projects",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "name": name,
                    "description": description or f"Repository {name}",
                    "visibility": "private" if private else "public",
                    "initialize_with_readme": False
                },
                timeout=30
            )
            
            if res.status_code not in [200, 201]:
                raise Exception(f"GitLab API error: {res.status_code} - {res.text}")
            
            data = res.json()
            return RepoInfo(
                url=data["web_url"],
                full_name=data["path_with_namespace"],
                owner=data["namespace"]["path"],
                name=data["name"],
                clone_url=data["http_url_to_repo"],
                provider="gitlab"
            )
    
    async def put_file(self, token: str, repo_full_name: str, path: str, content_bytes: bytes, message: str) -> dict:
        """Upload a file to GitLab project."""
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")
        project_id = repo_full_name.replace("/", "%2F")
        file_path = path.replace("/", "%2F")
        
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{self.BASE_URL}/projects/{project_id}/repository/files/{file_path}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "branch": "main",
                    "content": content_b64,
                    "commit_message": message,
                    "encoding": "base64"
                },
                timeout=30
            )
            
            if res.status_code not in [200, 201]:
                raise Exception(f"GitLab file upload error: {res.status_code} - {res.text}")
            
            return res.json()
    
    async def get_user_info(self, token: str) -> dict:
        """Get GitLab user info."""
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/user",
                headers={"Authorization": f"Bearer {token}"},
                timeout=20
            )
            
            if res.status_code != 200:
                raise Exception(f"GitLab API error: {res.status_code}")
            
            return res.json()
    
    async def list_repos(self, token: str, limit: int = 100) -> list:
        """List user's GitLab projects."""
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/projects",
                headers={"Authorization": f"Bearer {token}"},
                params={"per_page": min(limit, 100), "owned": True},
                timeout=20
            )
            
            if res.status_code != 200:
                raise Exception(f"GitLab API error: {res.status_code}")
            
            return res.json()
