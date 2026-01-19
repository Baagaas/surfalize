from surfalize import Batch
from pathlib import Path
root = Path.cwd() / 'matrix'
files = list(root.glob('*.vk4'))
print("Finished listing files.")