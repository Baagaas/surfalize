from pathlib import Path
from surfalize import Surface
from surfalize.addons_bv import operation_batch

file_path = Path.cwd() / 'data' / 'Si_55fs_1.80Jcm2_005Pulses_1.plux'
surf = Surface.load(file_path)

surf.level(inplace=True)
surf.fill_nonmeasured(minplace=True)

operation_batch.fft_filter_periodic(surf, type='pass', str_period_um=1/0.188, filter_radius=20, orders=3, plot_fft=True)

surf.show()
input("Press Enter to exit...")
