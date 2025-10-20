# GitHub Setup Guide

This guide helps publish the Min Tokenization Translator codebase to a new GitHub repository.

## 1. Initialize Git (if not already)

```bash
git init
git add .
git commit -m "Initial commit"
```

## 2. Create Remote Repository

1. Navigate to https://github.com/new.
2. Name the repository (e.g., `min_tokenization_translator`), choose visibility, and skip initializing with README if this repo already has one.
3. Copy the remote URL (SSH or HTTPS).

## 3. Add Remote & Push

### SSH
```bash
git remote add origin git@github.com:<user>/<repo>.git
git push -u origin main
```

### HTTPS
```bash
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

If the local repository uses `master`, replace `main` accordingly.

## 4. Recommended Branch Protections

- Require pull request reviews before merging.
- Enable status checks (CI pipelines) for `main`.
- Restrict force pushes to mainline branches.

## 5. CI Suggestions

- Add a GitHub Actions workflow (`.github/workflows/ci.yml`) to run `py_compile`, `pytest`, and optionally build Docker images.
- Publish artifacts (packs, documentation) as needed.

## 6. Keeping Subprojects in Sync

- Commit subproject docs alongside core work so planning artifacts stay visible.
- Consider using Git submodules or separate repos if the MCP middleman grows into standalone infrastructure.
