"""GitHub API routes for repository access."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from ...models import User
from ...services.user_store import user_store
from ...services.github_service import GitHubService, RepoInfo, RepoContext
from ..dependencies import get_current_user

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/repos", response_model=list[RepoInfo])
async def list_repositories(
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    sort: str = Query("updated", regex="^(created|updated|pushed|full_name)$"),
    user: User = Depends(get_current_user),
):
    """
    List repositories for the authenticated user.
    Includes both public and private repositories.
    """
    # Get GitHub access token for user
    github_token = user_store.get_github_token(user.id)
    if not github_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="GitHub token not found. Please re-authenticate.",
        )

    github_service = GitHubService(github_token)
    repos = await github_service.get_user_repos(
        page=page,
        per_page=per_page,
        sort=sort,
    )

    return repos


@router.get("/repos/{owner}/{repo}/context", response_model=RepoContext)
async def get_repository_context(
    owner: str,
    repo: str,
    user: User = Depends(get_current_user),
):
    """
    Get repository context for PRD generation.
    Extracts README, file tree, and key configuration files.
    """
    # Get GitHub access token for user
    github_token = user_store.get_github_token(user.id)
    if not github_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="GitHub token not found. Please re-authenticate.",
        )

    github_service = GitHubService(github_token)

    try:
        context = await github_service.get_repo_context(owner, repo)
        return context
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not fetch repository context: {str(e)}",
        )


@router.get("/repos/{owner}/{repo}/readme")
async def get_repository_readme(
    owner: str,
    repo: str,
    user: User = Depends(get_current_user),
):
    """Get the README content for a repository."""
    github_token = user_store.get_github_token(user.id)
    if not github_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="GitHub token not found. Please re-authenticate.",
        )

    github_service = GitHubService(github_token)
    readme = await github_service.get_repo_readme(owner, repo)

    if readme is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="README not found",
        )

    return {"content": readme}


@router.get("/repos/{owner}/{repo}/tree")
async def get_repository_tree(
    owner: str,
    repo: str,
    max_depth: int = Query(3, ge=1, le=5),
    user: User = Depends(get_current_user),
):
    """Get the file tree for a repository."""
    github_token = user_store.get_github_token(user.id)
    if not github_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="GitHub token not found. Please re-authenticate.",
        )

    github_service = GitHubService(github_token)
    tree = await github_service.get_file_tree(owner, repo, max_depth)

    return {"files": tree}
