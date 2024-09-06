import os.path
import sys
# Add top-level source directory to path, so that all local packages become visible (REF: https://docs.python-guide.org/writing/structure/)
src_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(src_path)
print(f'Added {src_path} to PATH to allow local package import')