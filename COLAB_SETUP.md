# Running in Google Colab or Jupyter

If you're getting `ModuleNotFoundError: No module named 'src'`, here are two solutions:

## Option 1: Use the Standalone Notebook (Easiest)

Use `notebooks/standalone_demo.ipynb` which has all code inline - no imports needed!

```python
# Just open and run:
# notebooks/standalone_demo.ipynb
```

## Option 2: Fix Imports in Original Notebook

Add this cell at the top of your notebook:

```python
# If in Colab, clone the repo first
!git clone https://github.com/woodai0120/claude.git
%cd claude

# Install package in development mode
!pip install -e .

# Now imports will work
import sys
sys.path.insert(0, '/content/claude')

from src.data.data_loader import DataLoader
from src.factors.factor_signals import FactorSignals
# ... etc
```

## Option 3: Copy Module Files to Colab

```python
# Upload the entire 'src' folder to your Colab session
# Then:
import sys
sys.path.append('/content')  # or wherever you uploaded

from src.data.data_loader import DataLoader
# ... etc
```

## Option 4: Install as Package

In your terminal or Colab:

```bash
# Clone repo
git clone https://github.com/woodai0120/claude.git
cd claude

# Install in editable mode
pip install -e .

# Now you can import from anywhere
python
>>> from src.data.data_loader import DataLoader
>>> # Works!
```

## Quick Test

To verify imports work:

```python
import sys
print(sys.path)  # Should show your repo directory

from src.data.data_loader import DataLoader
print("✓ Imports working!")
```

## Recommended: Use Standalone Demo

The simplest solution is to use `notebooks/standalone_demo.ipynb` which:
- Has all code inline
- No external imports
- Works in any environment
- Just run cell-by-cell!

---

**For local development:** The regular imports work fine - this is only an issue in cloud notebooks.
