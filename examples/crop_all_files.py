from surfalize import Surface
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
import surfalize.addons_bv.operations as operations_bv

operations_bv.crop_all_files(data_path=Path.cwd() / 'data')