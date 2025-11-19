# PowerShell script to split Singularis into modular v5 repos using git subtree
# This preserves git history for each component
# Run from Singularis root directory

Write-Host "🧩 Splitting Singularis v5 into Modular Repositories..." -ForegroundColor Cyan
Write-Host ""

$rootDir = Get-Location
$parentDir = Split-Path $rootDir -Parent

# Check if we're in a git repo
if (-not (Test-Path ".git")) {
    Write-Host "❌ ERROR: Not in a git repository!" -ForegroundColor Red
    Write-Host "   Run this script from the Singularis root directory." -ForegroundColor Yellow
    exit 1
}

# Module definitions for v5 architecture
$modules = @{
    "singularis-core" = @{
        "paths" = @(
            "singularis/core",
            "singularis/consciousness",
            "singularis/learning"
        )
        "description" = "Core components: ModularNetwork, consciousness layer, learning systems"
        "dependencies" = @("numpy", "scipy", "networkx", "loguru")
    }
    "singularis-router" = @{
        "paths" = @(
            "singularis/llm",
            "singularis/data_brain",
            "singularis/life_ops",
            "singularis/agi_orchestrator.py",
            "singularis/unified_consciousness_layer.py"
        )
        "description" = "Router device: UnifiedConsciousnessLayer, Meta-MoE, DATA-Brain, LifeOps"
        "dependencies" = @("aiohttp", "openai", "loguru", "singularis-core")
    }
    "singularis-cygnus" = @{
        "paths" = @(
            "configs/cygnus_experts.yaml",
            "scripts/setup_cygnus.sh",
            "docs/CYGNUS_SETUP.md"
        )
        "description" = "Cygnus device: 10 expert model configs and setup scripts"
        "dependencies" = @("singularis-core")
    }
    "singularis-macbook" = @{
        "paths" = @(
            "singularis/aura_brain",
            "configs/macbook_orchestra.yaml",
            "scripts/setup_macbook.sh",
            "docs/ORCHESTRA_MODE.md"
        )
        "description" = "MacBook device: AURA-Brain bio-simulator + large MoE configs"
        "dependencies" = @("numpy", "scipy", "torch", "singularis-core")
    }
    "singularis-nvidia" = @{
        "paths" = @(
            "singularis/positronic",
            "configs/nvidia_positronic.yaml",
            "scripts/setup_nvidia.sh",
            "docs/POSITRONIC_NETWORK.md"
        )
        "description" = "NVIDIA device: Abductive Positronic Network"
        "dependencies" = @("torch", "numpy", "singularis-core")
    }
}

Write-Host "📋 Module Plan:" -ForegroundColor Cyan
foreach ($moduleName in $modules.Keys) {
    $module = $modules[$moduleName]
    Write-Host "   • $moduleName" -ForegroundColor Yellow
    Write-Host "     $($module.description)" -ForegroundColor Gray
}
Write-Host ""

# Ask for confirmation
$confirm = Read-Host "This will create 5 new git repositories in $parentDir. Continue? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Function to create a module repo
function New-ModuleRepo {
    param(
        [string]$ModuleName,
        [hashtable]$ModuleConfig,
        [string]$ParentDir,
        [string]$RootDir
    )
    
    Write-Host "📦 Creating $ModuleName..." -ForegroundColor Yellow
    
    $moduleDir = Join-Path $ParentDir $ModuleName
    
    # Create module directory
    if (Test-Path $moduleDir) {
        Write-Host "   ⚠️  Directory exists. Remove it first or skip." -ForegroundColor Yellow
        $overwrite = Read-Host "   Remove and recreate? (y/n)"
        if ($overwrite -eq 'y') {
            Remove-Item -Path $moduleDir -Recurse -Force
        } else {
            Write-Host "   Skipping $ModuleName" -ForegroundColor Yellow
            return
        }
    }
    
    New-Item -ItemType Directory -Path $moduleDir -Force | Out-Null
    Push-Location $moduleDir
    
    # Initialize new git repo
    git init | Out-Null
    Write-Host "   ✅ Initialized git repository" -ForegroundColor Green
    
    # Add remote to original repo (for subtree split)
    git remote add origin-full $RootDir 2>$null
    
    # For each path, try to extract history using subtree split
    $branchesToMerge = @()
    
    foreach ($path in $ModuleConfig.paths) {
        $fullPath = Join-Path $RootDir $path
        
        if (Test-Path $fullPath) {
            Write-Host "   📂 Extracting history for: $path" -ForegroundColor Cyan
            
            # Use git subtree split to extract history
            Push-Location $RootDir
            try {
                # Create a branch with just this path's history
                $branchName = "split-$($path.Replace('/', '-').Replace('\', '-'))"
                
                # Check if path exists in git history
                $gitLsFiles = git ls-files $path 2>$null
                if ($gitLsFiles) {
                    Write-Host "      Splitting subtree..." -ForegroundColor Gray
                    $splitResult = git subtree split --prefix=$path --branch=$branchName 2>&1
                    
                    if ($LASTEXITCODE -eq 0) {
                        $branchesToMerge += @{
                            "branch" = $branchName
                            "path" = $path
                        }
                        Write-Host "      ✅ Created branch: $branchName" -ForegroundColor Green
                    } else {
                        Write-Host "      ⚠️  Subtree split failed, will copy files instead" -ForegroundColor Yellow
                    }
                } else {
                    Write-Host "      ⚠️  Path not in git history, will copy files" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "      ⚠️  Error during split: $_" -ForegroundColor Yellow
            }
            Pop-Location
        } else {
            Write-Host "   ⚠️  Path not found: $path" -ForegroundColor Yellow
        }
    }
    
    # Merge all split branches into the new repo
    if ($branchesToMerge.Count -gt 0) {
        Write-Host "   🔀 Merging extracted histories..." -ForegroundColor Cyan
        
        foreach ($branchInfo in $branchesToMerge) {
            $branch = $branchInfo.branch
            $path = $branchInfo.path
            
            # Fetch the branch from original repo
            git fetch origin-full $branch 2>$null
            
            # Create subdirectory structure
            $targetPath = $path
            $targetDir = Split-Path $targetPath -Parent
            
            if ($targetDir -and -not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            
            # Merge with --allow-unrelated-histories
            git merge --allow-unrelated-histories -X theirs origin-full/$branch -m "Import $path history" 2>$null
            
            Write-Host "      ✅ Merged: $path" -ForegroundColor Green
        }
    }
    
    # Copy any files that weren't in git history
    foreach ($path in $ModuleConfig.paths) {
        $sourcePath = Join-Path $RootDir $path
        $destPath = Join-Path $moduleDir $path
        
        if ((Test-Path $sourcePath) -and -not (Test-Path $destPath)) {
            Write-Host "   📋 Copying (not in git): $path" -ForegroundColor Gray
            
            $destParent = Split-Path $destPath -Parent
            if ($destParent -and -not (Test-Path $destParent)) {
                New-Item -ItemType Directory -Path $destParent -Force | Out-Null
            }
            
            if (Test-Path $sourcePath -PathType Container) {
                Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
            } else {
                Copy-Item -Path $sourcePath -Destination $destPath -Force
            }
        }
    }
    
    # Create README.md
    $readmePath = Join-Path $moduleDir "README.md"
    $readmeContent = @"
# $ModuleName

$($ModuleConfig.description)

Part of the **Singularis v5.0** distributed Meta-MoE AGI architecture.

## Installation

``````bash
pip install -e .
``````

## Dependencies

$($ModuleConfig.dependencies | ForEach-Object { "- $_" } | Out-String)

## Documentation

See the main [Singularis v5 README](https://github.com/yourusername/Singularis) for architecture details.

## License

MIT
"@
    Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
    Write-Host "   ✅ Created README.md" -ForegroundColor Green
    
    # Create requirements.txt
    $requirementsPath = Join-Path $moduleDir "requirements.txt"
    $reqContent = "# Dependencies for $ModuleName`n"
    $reqContent += ($ModuleConfig.dependencies | Where-Object { $_ -notlike "singularis-*" } | ForEach-Object { "$_`n" }) -join ""
    Set-Content -Path $requirementsPath -Value $reqContent -Encoding UTF8
    Write-Host "   ✅ Created requirements.txt" -ForegroundColor Green
    
    # Create setup.py
    $setupPath = Join-Path $moduleDir "setup.py"
    $setupContent = @"
from setuptools import setup, find_packages

setup(
    name="$ModuleName",
    version="5.0.0",
    description="$($ModuleConfig.description)",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        $($ModuleConfig.dependencies | Where-Object { $_ -notlike "singularis-*" } | ForEach-Object { "`n        '$_'," } | Out-String)
    ],
    python_requires=">=3.10",
)
"@
    Set-Content -Path $setupPath -Value $setupContent -Encoding UTF8
    Write-Host "   ✅ Created setup.py" -ForegroundColor Green
    
    # Create .gitignore
    $gitignorePath = Join-Path $moduleDir ".gitignore"
    $gitignoreContent = @"
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.env
.venv
venv/
*.log
.DS_Store
"@
    Set-Content -Path $gitignorePath -Value $gitignoreContent -Encoding UTF8
    Write-Host "   ✅ Created .gitignore" -ForegroundColor Green
    
    # Initial commit
    git add .
    git commit -m "Initial commit: $ModuleName v5.0.0" 2>$null
    Write-Host "   ✅ Created initial commit" -ForegroundColor Green
    
    # Clean up remote
    git remote remove origin-full 2>$null
    
    Pop-Location
    Write-Host ""
}

# Create each module repo
foreach ($moduleName in $modules.Keys) {
    New-ModuleRepo -ModuleName $moduleName -ModuleConfig $modules[$moduleName] -ParentDir $parentDir -RootDir $rootDir
}

Write-Host "✅ All modular repositories created!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Repositories created in: $parentDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review each module files and git history"
Write-Host "2. Update setup.py with correct author/URL"
Write-Host "3. Test each module independently:"
Write-Host "   cd $parentDir\singularis-core && pip install -e ."
Write-Host "4. Create GitHub repos and push:"
Write-Host "   cd $parentDir\singularis-core"
Write-Host "   git remote add origin https://github.com/yourusername/singularis-core.git"
Write-Host "   git push -u origin main"
Write-Host "5. Publish to PyPI (optional):"
Write-Host "   python setup.py sdist bdist_wheel"
Write-Host "   twine upload dist/*"
Write-Host ""
Write-Host "See docs/MODULAR_DEPLOYMENT.md for deployment instructions" -ForegroundColor Cyan
Write-Host ""
