import httpx
import base64
from typing import Optional
from .base_provider import BaseGitProvider, RepoInfo

class BitbucketProvider(BaseGitProvider):
    """Bitbucket provider implementation."""
    
    BASE_URL = "https://api.bitbucket.org/2.0"
    
    @property
    def provider_name(self) -> str:
        return "bitbucket"
    
    async def create_repo(self, token: str, name: str, description: Optional[str] = None, private: bool = False) -> RepoInfo:
        """Create a Bitbucket repository."""
        async with httpx.AsyncClient() as client:
            # Get workspace first
            user_res = await client.get(
                f"{self.BASE_URL}/user",
                headers={"Authorization": f"Bearer {token}"},
                timeout=20
            )
            user_data = user_res.json()
            workspace = user_data.get("username")
            
            res = await client.post(
                f"{self.BASE_URL}/repositories/{workspace}/{name}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "scm": "git",
                    "is_private": private,
                    "description": description or f"Repository {name}"
                },
                timeout=30
            )
            
            if res.status_code not in [200, 201]:
                raise Exception(f"Bitbucket API error: {res.status_code} - {res.text}")
            
            data = res.json()
            return RepoInfo(
                url=data["links"]["html"]["href"],
                full_name=data["full_name"],
                owner=workspace,
                name=name,
                clone_url=data["links"]["clone"][0]["href"],
                provider="bitbucket"
            )
    
    async def put_file(self, token: str, repo_full_name: str, path: str, content_bytes: bytes, message: str) -> dict:
        """Upload a file to Bitbucket repo."""
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{self.BASE_URL}/repositories/{repo_full_name}/src",
                headers={"Authorization": f"Bearer {token}"},
                data={"message": message},
                files={path: content_bytes},
                timeout=30
            )
            
            if res.status_code not in [200, 201]:
                raise Exception(f"Bitbucket file upload error: {res.status_code}")
            
            return res.json()
    
    async def get_user_info(self, token: str) -> dict:
        """Get Bitbucket user info."""
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/user",
                headers={"Authorization": f"Bearer {token}"},
                timeout=20
            )
            
            if res.status_code != 200:
                raise Exception(f"Bitbucket API error: {res.status_code}")
            
            return res.json()
    
    async def list_repos(self, token: str, limit: int = 100) -> list:
        """List user's Bitbucket repositories."""
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/repositories",
                headers={"Authorization": f"Bearer {token}"},
                params={"pagelen": min(limit, 100), "role": "owner"},
                timeout=20
            )
            
            if res.status_code != 200:
                raise Exception(f"Bitbucket API error: {res.status_code}")
            
            return res.json().get("values", [])
