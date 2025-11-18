# Splitting Singularis into Modular Repositories

This guide explains how to split the Singularis monorepo into 5 modular repositories for the v5 distributed architecture.

## Overview

The split creates:

1. **`singularis-core`** - Shared foundation (ModularNetwork, consciousness, learning)
2. **`singularis-router`** - Router device (UnifiedConsciousnessLayer, Meta-MoE, DATA-Brain, LifeOps)
3. **`singularis-cygnus`** - Cygnus device (10 expert configs, setup scripts)
4. **`singularis-macbook`** - MacBook device (AURA-Brain, orchestra mode configs)
5. **`singularis-nvidia`** - NVIDIA device (Positronic Network)

## Prerequisites

- Git repository with commit history
- PowerShell (Windows) or Bash (Linux/macOS)
- ~2GB free disk space for split repos
- GitHub/GitLab accounts (for pushing)

## Running the Split

### Option 1: PowerShell (Windows)

```powershell
cd d:\Projects\Singularis
.\scripts\split_modular_repos_v5.ps1
```

### Option 2: Bash (Linux/macOS)

```bash
cd ~/Projects/Singularis
# Convert PowerShell script to Bash or use git commands directly
```

## What the Script Does

1. **Creates 5 new directories** in the parent folder:
   ```
   d:\Projects\
   ├── Singularis\                    (original monorepo)
   ├── singularis-core\               (new)
   ├── singularis-router\             (new)
   ├── singularis-cygnus\             (new)
   ├── singularis-macbook\            (new)
   └── singularis-nvidia\             (new)
   ```

2. **Extracts git history** using `git subtree split`:
   - Preserves commit history for each component
   - Creates separate branches for each path
   - Merges into new repos

3. **Copies files** not in git history:
   - Config files
   - Documentation
   - Setup scripts

4. **Creates boilerplate**:
   - `README.md` for each repo
   - `setup.py` for pip installation
   - `requirements.txt` with dependencies
   - `.gitignore` for Python projects
   - Initial git commit

## After the Split

### 1. Review Each Repo

```bash
cd ../singularis-core
ls -la
git log --oneline
```

### 2. Test Installation

```bash
# Install core
cd ../singularis-core
pip install -e .

# Install router (depends on core)
cd ../singularis-router
pip install -e .

# Test imports
python -c "from singularis.core import ModularNetwork; print('✅ Core works')"
```

### 3. Create GitHub Repos

```bash
# On GitHub, create 5 new repositories:
# - singularis-core
# - singularis-router
# - singularis-cygnus
# - singularis-macbook
# - singularis-nvidia
```

### 4. Push to GitHub

```bash
cd ../singularis-core
git remote add origin https://github.com/yourusername/singularis-core.git
git branch -M main
git push -u origin main

cd ../singularis-router
git remote add origin https://github.com/yourusername/singularis-router.git
git branch -M main
git push -u origin main

# Repeat for cygnus, macbook, nvidia
```

### 5. Update Dependencies

Each repo's `setup.py` should reference `singularis-core`:

```python
# singularis-router/setup.py
install_requires=[
    "singularis-core>=5.0.0",  # From GitHub or PyPI
    "openai>=1.0.0",
    "aiohttp>=3.9.0",
    # ...
]
```

To install from GitHub before PyPI publish:

```bash
pip install git+https://github.com/yourusername/singularis-core.git
pip install git+https://github.com/yourusername/singularis-router.git
```

## Deployment to Devices

### Cygnus (AMD 2x7900XT)

```bash
# Clone only what's needed
git clone https://github.com/yourusername/singularis-core.git
git clone https://github.com/yourusername/singularis-cygnus.git

cd singularis-core && pip install -e .
cd ../singularis-cygnus
pip install -r requirements.txt
./scripts/setup_cygnus.sh
```

### Router (AMD 6900XT)

```bash
git clone https://github.com/yourusername/singularis-core.git
git clone https://github.com/yourusername/singularis-router.git

cd singularis-core && pip install -e .
cd ../singularis-router
pip install -r requirements.txt
```

### MacBook Pro M3

```bash
git clone https://github.com/yourusername/singularis-core.git
git clone https://github.com/yourusername/singularis-macbook.git

cd singularis-core && pip install -e .
cd ../singularis-macbook
pip install -r requirements.txt
./scripts/setup_macbook.sh
```

### NVIDIA Laptop

```bash
git clone https://github.com/yourusername/singularis-core.git
git clone https://github.com/yourusername/singularis-nvidia.git

cd singularis-core && pip install -e .
cd ../singularis-nvidia
pip install -r requirements.txt
./scripts/setup_nvidia.sh
```

## Benefits

✅ **Smaller deployments** - Each device only clones what it needs  
✅ **Independent updates** - Update AURA-Brain without touching Cygnus  
✅ **Clear dependencies** - `singularis-core` is the shared foundation  
✅ **Easier testing** - Test each component in isolation  
✅ **Git history preserved** - Full commit history for each component  

## Rollback

If you need to go back to the monorepo:

```bash
# The original Singularis repo is unchanged
cd d:\Projects\Singularis
git status  # Still intact

# Delete split repos if needed
rm -rf ../singularis-core
rm -rf ../singularis-router
# etc.
```

## Publishing to PyPI (Optional)

Once tested, you can publish to PyPI:

```bash
cd ../singularis-core
python setup.py sdist bdist_wheel
twine upload dist/*

# Then other repos can install with:
pip install singularis-core
```

## Troubleshooting

### "git subtree split failed"

Some paths may not be in git history. The script will copy them instead.

### "Import errors after split"

Check that `singularis-core` is installed:

```bash
pip list | grep singularis
```

### "Circular dependencies"

Ensure only `singularis-core` is a dependency, not cross-dependencies between device repos.

## See Also

- `docs/MODULAR_DEPLOYMENT.md` - Detailed deployment architecture
- `verify_cluster.py` - Health check for all devices
- `test_cluster_integration_minimal.py` - Functional tests

---

**Questions?** See the main [Singularis v5 README](SINGULARIS_V5_README.md)
