from surfalize import Surface
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
import cropper

cropper.crop_all_files(data_path=Path.cwd() / 'data')