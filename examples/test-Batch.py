from surfalize import Batch
from pathlib import Path
root = Path.cwd() / 'examples' / 'data'
files = list(root.glob('*.plux'))
print(files)