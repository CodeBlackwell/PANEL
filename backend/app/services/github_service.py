"""GitHub API service for repository access."""

from typing import Optional
import httpx
from pydantic import BaseModel


class RepoInfo(BaseModel):
    """Repository information."""
    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    private: bool
    html_url: str
    default_branch: str
    language: Optional[str] = None
    stargazers_count: int = 0
    updated_at: str


class RepoContext(BaseModel):
    """Repository context for PRD generation."""
    repo_name: str
    repo_full_name: str
    description: Optional[str] = None
    readme_content: Optional[str] = None
    file_tree: list[str] = []
    config_files: dict[str, str] = {}  # filename -> content


class GitHubService:
    """Service for interacting with GitHub API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def get_user_repos(
        self,
        page: int = 1,
        per_page: int = 30,
        sort: str = "updated",
    ) -> list[RepoInfo]:
        """Get repositories for the authenticated user."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/user/repos",
                headers=self.headers,
                params={
                    "page": page,
                    "per_page": per_page,
                    "sort": sort,
                    "affiliation": "owner,collaborator,organization_member",
                },
            )

            if response.status_code != 200:
                return []

            repos = response.json()
            return [
                RepoInfo(
                    id=repo["id"],
                    name=repo["name"],
                    full_name=repo["full_name"],
                    description=repo.get("description"),
                    private=repo["private"],
                    html_url=repo["html_url"],
                    default_branch=repo.get("default_branch", "main"),
                    language=repo.get("language"),
                    stargazers_count=repo.get("stargazers_count", 0),
                    updated_at=repo["updated_at"],
                )
                for repo in repos
            ]

    async def get_repo_readme(self, owner: str, repo: str) -> Optional[str]:
        """Get the README content for a repository."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/readme",
                headers={
                    **self.headers,
                    "Accept": "application/vnd.github.v3.raw",
                },
            )

            if response.status_code == 200:
                return response.text
            return None

    async def get_file_tree(
        self,
        owner: str,
        repo: str,
        max_depth: int = 3,
    ) -> list[str]:
        """Get the file tree for a repository (up to max_depth)."""
        async with httpx.AsyncClient() as client:
            # Get the default branch tree
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/HEAD",
                headers=self.headers,
                params={"recursive": "1"},
            )

            if response.status_code != 200:
                return []

            tree_data = response.json()
            files = []

            for item in tree_data.get("tree", []):
                path = item["path"]
                # Filter by depth
                depth = path.count("/") + 1
                if depth <= max_depth:
                    # Add type indicator
                    if item["type"] == "tree":
                        files.append(f"{path}/")
                    else:
                        files.append(path)

            return sorted(files)

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
    ) -> Optional[str]:
        """Get the content of a specific file."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                headers={
                    **self.headers,
                    "Accept": "application/vnd.github.v3.raw",
                },
            )

            if response.status_code == 200:
                # Limit content size to prevent huge files
                content = response.text
                if len(content) > 50000:  # ~50KB limit
                    return content[:50000] + "\n... (truncated)"
                return content
            return None

    async def get_repo_context(self, owner: str, repo: str) -> RepoContext:
        """
        Get full repository context for PRD generation.
        Extracts README, file tree, and key config files.
        """
        # Get repo info first
        async with httpx.AsyncClient() as client:
            repo_response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}",
                headers=self.headers,
            )
            repo_data = repo_response.json() if repo_response.status_code == 200 else {}

        # Get README
        readme = await self.get_repo_readme(owner, repo)

        # Get file tree
        file_tree = await self.get_file_tree(owner, repo, max_depth=3)

        # Get key config files
        config_file_names = [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "Cargo.toml",
            "go.mod",
            "docker-compose.yml",
            "docker-compose.yaml",
            "Dockerfile",
            ".env.example",
            "tsconfig.json",
            "vite.config.ts",
            "vite.config.js",
            "webpack.config.js",
            "next.config.js",
            "nuxt.config.ts",
        ]

        config_files = {}
        for filename in config_file_names:
            if filename in file_tree:
                content = await self.get_file_content(owner, repo, filename)
                if content:
                    config_files[filename] = content

        return RepoContext(
            repo_name=repo,
            repo_full_name=f"{owner}/{repo}",
            description=repo_data.get("description"),
            readme_content=readme,
            file_tree=file_tree,
            config_files=config_files,
        )
