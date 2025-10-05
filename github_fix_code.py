# ===== CODE ZUM KOPIEREN UND EINFÜGEN =====
# Ersetzen Sie den Code in backend\app\api\github.py (ca. Zeile 652-668)
# mit diesem Code:

        # Parse repository URL
        # Clean up URL: remove trailing slashes and .git extension
        logger.info(f"📥 Original URL received: '{request.repo_url}'")
        clean_url = request.repo_url.strip().rstrip('/').replace('.git/', '').replace('.git', '')
        logger.info(f"🧹 Cleaned URL: '{clean_url}'")
        
        # Supports: https://github.com/owner/repo or git@github.com:owner/repo
        github_pattern = r'github\.com[:/]([^/]+)/([^/]+)'
        match = re.search(github_pattern, clean_url)
        
        if not match:
            raise HTTPException(
                status_code=400,
                detail=f"❌ Ungültige GitHub-URL: '{request.repo_url}'. Bitte verwende das Format: https://github.com/username/repository"
            )
        
        owner, repo_name = match.groups()
        # Remove any remaining extensions or special chars from repo_name
        repo_name = repo_name.split('.')[0].split('?')[0].split('#')[0]
