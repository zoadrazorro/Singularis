#!/bin/bash
# Setup script for Sephirot cluster local-only configuration
# Run this on the LifeOps core node (AMD desktop)

set -e

echo "=================================================="
echo "Singularis Sephirot Cluster Setup"
echo "=================================================="
echo ""

# Prompt for MacBook IP
read -p "Enter MacBook Pro LAN IP (e.g., 192.168.1.100): " MACBOOK_IP
MACBOOK_IP=${MACBOOK_IP:-"192.168.1.100"}

# Construct LM Studio URL
LM_STUDIO_URL="http://${MACBOOK_IP}:1234/v1"

echo ""
echo "Configuration:"
echo "  MacBook Pro IP: ${MACBOOK_IP}"
echo "  LM Studio URL: ${LM_STUDIO_URL}"
echo ""

# Test connection to MacBook
echo "Testing connection to LM Studio..."
if curl -s --max-time 5 "${LM_STUDIO_URL}/models" > /dev/null 2>&1; then
    echo "✓ Connection successful"
else
    echo "✗ WARNING: Cannot connect to LM Studio at ${LM_STUDIO_URL}"
    echo "  Make sure:"
    echo "  1. LM Studio is running on MacBook Pro"
    echo "  2. Server is bound to 0.0.0.0:1234 (not 127.0.0.1)"
    echo "  3. Firewall allows connections from this machine"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Setting up environment variables..."

# Create/update .env file
cat > .env <<EOF
# Singularis Local-Only Cluster Configuration
# Generated: $(date)

# Node role
NODE_ROLE=lifeops_core

# Enable local-only mode (no cloud API calls)
SINGULARIS_LOCAL_ONLY=1

# Point to MacBook Pro LM Studio endpoint
OPENAI_BASE_URL=${LM_STUDIO_URL}

# Optional: API key (not required for local endpoints)
OPENAI_API_KEY=local-only

# Cluster topology
INFERENCE_PRIMARY=${MACBOOK_IP}:1234
EOF

echo "✓ Created .env file"

# Add to shell profile (optional)
echo ""
read -p "Add to ~/.bashrc? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cat >> ~/.bashrc <<EOF

# Singularis Local-Only Cluster Configuration
export NODE_ROLE=lifeops_core
export SINGULARIS_LOCAL_ONLY=1
export OPENAI_BASE_URL=${LM_STUDIO_URL}
export OPENAI_API_KEY=local-only
EOF
    echo "✓ Added to ~/.bashrc (run 'source ~/.bashrc' to apply)"
fi

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. On MacBook Pro, start LM Studio with phi-4-mini-reasoning model"
echo "  2. Verify: curl ${LM_STUDIO_URL}/models"
echo "  3. Run tests: python test_local_only_llm.py"
echo "  4. Start LifeOps: python -m singularis.agi_orchestrator"
echo ""
echo "Documentation: docs/SEPHIROT_CLUSTER_SETUP.md"
echo ""
