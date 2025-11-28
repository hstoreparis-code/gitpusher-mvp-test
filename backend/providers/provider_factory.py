from typing import Dict, Optional
from .base_provider import BaseGitProvider
from .github import GitHubProvider
from .gitlab import GitLabProvider
from .bitbucket import BitbucketProvider
from .gitea import GiteaProvider
from .codeberg import CodebergProvider
from .azure import AzureDevOpsProvider
from .aws import AWSCodeCommitProvider
from .gcp import GCPSourceRepoProvider
from .gitee import GiteeProvider
from .aliyun import AliyunProvider
from .tencent import TencentProvider
from .sourceforge import SourceForgeProvider


class ProviderFactory:
    """Factory to get the right Git provider based on name."""
    
    _providers: Dict[str, BaseGitProvider] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider: BaseGitProvider):
        """Register a provider."""
        cls._providers[name.lower()] = provider
    
    @classmethod
    def get_provider(cls, name: str) -> BaseGitProvider:
        """Get provider by name."""
        provider_name = name.lower()
        
        if provider_name not in cls._providers:
            # Lazy initialization
            if provider_name == "github":
                cls._providers[provider_name] = GitHubProvider()
            elif provider_name == "gitlab":
                cls._providers[provider_name] = GitLabProvider()
            elif provider_name == "bitbucket":
                cls._providers[provider_name] = BitbucketProvider()
            elif provider_name == "gitea":
                cls._providers[provider_name] = GiteaProvider()
            elif provider_name == "codeberg":
                cls._providers[provider_name] = CodebergProvider()
            elif provider_name == "azure":
                cls._providers[provider_name] = AzureDevOpsProvider()
            elif provider_name == "aws":
                cls._providers[provider_name] = AWSCodeCommitProvider()
            elif provider_name == "gcp":
                cls._providers[provider_name] = GCPSourceRepoProvider()
            elif provider_name == "gitee":
                cls._providers[provider_name] = GiteeProvider()
            elif provider_name == "aliyun":
                cls._providers[provider_name] = AliyunProvider()
            elif provider_name == "tencent":
                cls._providers[provider_name] = TencentProvider()
            elif provider_name == "sourceforge":
                cls._providers[provider_name] = SourceForgeProvider()
            else:
                raise ValueError(f"Unknown provider: {name}")
        
        return cls._providers[provider_name]
    
    @classmethod
    def get_all_providers(cls) -> list:
        """Get list of all supported providers."""
        return [
            {"name": "github", "label": "GitHub", "status": "active"},
            {"name": "gitlab", "label": "GitLab", "status": "active"},
            {"name": "bitbucket", "label": "Bitbucket", "status": "active"},
            {"name": "gitea", "label": "Gitea", "status": "active"},
            {"name": "codeberg", "label": "Codeberg", "status": "active"},
            {"name": "gitee", "label": "Gitee", "status": "active"},
            {"name": "azure", "label": "Azure DevOps", "status": "limited"},
            {"name": "aws", "label": "AWS CodeCommit", "status": "limited"},
            {"name": "gcp", "label": "Google Cloud", "status": "limited"},
            {"name": "aliyun", "label": "Alibaba Cloud", "status": "limited"},
            {"name": "tencent", "label": "Tencent Cloud", "status": "limited"},
            {"name": "sourceforge", "label": "SourceForge", "status": "limited"}
        ]
