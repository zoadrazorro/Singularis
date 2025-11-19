# PowerShell script to split Singularis into modular v5 repos
# This is a SIMPLIFIED version that just copies files (no git subtree)
# Run from Singularis root directory

Write-Host "Splitting Singularis v5 into Modular Repositories..." -ForegroundColor Cyan
Write-Host ""

$rootDir = Get-Location
$parentDir = Split-Path $rootDir -Parent

# Check if we are in a git repo
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Not in a git repository!" -ForegroundColor Red
    Write-Host "Run this script from the Singularis root directory." -ForegroundColor Yellow
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
            "scripts/setup_cygnus.sh"
        )
        "description" = "Cygnus device: 10 expert model configs and setup scripts"
        "dependencies" = @("singularis-core")
    }
    "singularis-macbook" = @{
        "paths" = @(
            "singularis/aura_brain",
            "configs/macbook_orchestra.yaml",
            "scripts/setup_macbook.sh"
        )
        "description" = "MacBook device: AURA-Brain bio-simulator + large MoE configs"
        "dependencies" = @("numpy", "scipy", "torch", "singularis-core")
    }
    "singularis-nvidia" = @{
        "paths" = @(
            "singularis/positronic",
            "configs/nvidia_positronic.yaml",
            "scripts/setup_nvidia.sh"
        )
        "description" = "NVIDIA device: Abductive Positronic Network"
        "dependencies" = @("torch", "numpy", "singularis-core")
    }
}

Write-Host "Module Plan:" -ForegroundColor Cyan
foreach ($moduleName in $modules.Keys) {
    $module = $modules[$moduleName]
    Write-Host "  - $moduleName" -ForegroundColor Yellow
    Write-Host "    $($module.description)" -ForegroundColor Gray
}
Write-Host ""

# Ask for confirmation
$confirm = Read-Host "This will create 5 new directories in $parentDir. Continue? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Create each module repo
foreach ($moduleName in $modules.Keys) {
    $module = $modules[$moduleName]
    
    Write-Host "Creating $moduleName..." -ForegroundColor Yellow
    
    $moduleDir = Join-Path $parentDir $moduleName
    
    # Create module directory
    if (Test-Path $moduleDir) {
        Write-Host "  Directory exists. Remove it first or skip." -ForegroundColor Yellow
        $overwrite = Read-Host "  Remove and recreate? (y/n)"
        if ($overwrite -eq 'y') {
            Remove-Item -Path $moduleDir -Recurse -Force
        } else {
            Write-Host "  Skipping $moduleName" -ForegroundColor Yellow
            continue
        }
    }
    
    New-Item -ItemType Directory -Path $moduleDir -Force | Out-Null
    
    # Copy files
    foreach ($path in $module.paths) {
        $sourcePath = Join-Path $rootDir $path
        
        if (Test-Path $sourcePath) {
            $destPath = Join-Path $moduleDir $path
            $destParent = Split-Path $destPath -Parent
            
            if ($destParent -and -not (Test-Path $destParent)) {
                New-Item -ItemType Directory -Path $destParent -Force | Out-Null
            }
            
            if (Test-Path $sourcePath -PathType Container) {
                Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
            } else {
                Copy-Item -Path $sourcePath -Destination $destPath -Force
            }
            
            Write-Host "  Copied: $path" -ForegroundColor Green
        } else {
            Write-Host "  Not found: $path" -ForegroundColor Yellow
        }
    }
    
    # Create README.md
    $readmePath = Join-Path $moduleDir "README.md"
    $readmeContent = @"
# $moduleName

$($module.description)

Part of the **Singularis v5.0** distributed Meta-MoE AGI architecture.

## Installation

``````bash
pip install -e .
``````

## Dependencies

$($module.dependencies | ForEach-Object { "- $_" } | Out-String)

## License

MIT
"@
    Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
    Write-Host "  Created README.md" -ForegroundColor Green
    
    # Create requirements.txt
    $requirementsPath = Join-Path $moduleDir "requirements.txt"
    $reqContent = "# Dependencies for $moduleName`n"
    $reqContent += ($module.dependencies | Where-Object { $_ -notlike "singularis-*" } | ForEach-Object { "$_`n" }) -join ""
    Set-Content -Path $requirementsPath -Value $reqContent -Encoding UTF8
    Write-Host "  Created requirements.txt" -ForegroundColor Green
    
    # Create setup.py
    $setupPath = Join-Path $moduleDir "setup.py"
    $depList = ($module.dependencies | Where-Object { $_ -notlike "singularis-*" } | ForEach-Object { "        '$_'," }) -join "`n"
    $setupContent = @"
from setuptools import setup, find_packages

setup(
    name="$moduleName",
    version="5.0.0",
    description="$($module.description)",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
$depList
    ],
    python_requires=">=3.10",
)
"@
    Set-Content -Path $setupPath -Value $setupContent -Encoding UTF8
    Write-Host "  Created setup.py" -ForegroundColor Green
    
    # Create .gitignore
    $gitignorePath = Join-Path $moduleDir ".gitignore"
    $gitignoreContent = @"
__pycache__/
*.py[cod]
*`$py.class
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
    Write-Host "  Created .gitignore" -ForegroundColor Green
    
    # Initialize git
    Push-Location $moduleDir
    git init | Out-Null
    git add .
    git commit -m "Initial commit: $moduleName v5.0.0" | Out-Null
    Pop-Location
    Write-Host "  Initialized git repository" -ForegroundColor Green
    
    Write-Host ""
}

Write-Host "All modular repositories created!" -ForegroundColor Green
Write-Host ""
Write-Host "Repositories created in: $parentDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review each module files and git history"
Write-Host "2. Update setup.py with correct author/URL"
Write-Host "3. Test each module independently"
Write-Host "4. Create GitHub repos and push"
Write-Host "5. Publish to PyPI (optional)"
Write-Host ""
Write-Host "See docs/MODULAR_DEPLOYMENT.md for deployment instructions" -ForegroundColor Cyan
Write-Host ""
