#!/bin/bash
# Fix dependency compatibility issues for embedding generation
# This script ensures numpy, scipy, and related packages are compatible

echo "🔧 Fixing dependency compatibility issues..."
echo ""

# Backup current requirements
if [ -f "requirements.txt" ]; then
    cp requirements.txt requirements.txt.backup
    echo "✅ Backed up requirements.txt"
fi

# Uninstall problematic versions
echo "📦 Uninstalling incompatible versions..."
pip uninstall -y numpy scipy 2>/dev/null || true

# Install compatible versions
echo "📦 Installing compatible versions..."
pip install "numpy>=1.24.0,<2.0.0"
pip install "scipy>=1.11.0,<1.17.0"

# Reinstall dependent packages
echo "📦 Reinstalling dependent packages..."
pip install --upgrade sentence-transformers scikit-learn

# Verify installation
echo ""
echo "✅ Dependency fix complete!"
echo ""
echo "Verifying versions:"
python -c "import numpy; import scipy; print(f'numpy: {numpy.__version__}'); print(f'scipy: {scipy.__version__}')" 2>&1

echo ""
echo "🎯 Next steps:"
echo "1. Run: python scripts/generate_recipe_embeddings.py"
echo "2. Run: python scripts/generate_ingredient_embeddings.py"
echo "3. Verify: python verify_database.py"

