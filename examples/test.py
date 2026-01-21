from surfalize import Surface
import matplotlib
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
import cropper
from make_circles import fill_circle_in_matrix

data_path = Path.cwd() / 'data'
crop_folder_name = 'cropped'
file_name = 'Steel_55fs_1.8Jcm2_009Pulses_1'

path = data_path / (file_name + '.plux')
s1 = Surface.load(path)    
s1.level(inplace=True)
s1.remove_outliers(inplace=True)
s1.fill_nonmeasured(inplace=True, method='median', size=5)
s1.show(block=False)
rows, cols = s1.size

# Compute and visualize Fourier space
fft_data = np.fft.fft2(s1.data)
fft_shifted = np.fft.fftshift(fft_data)

# Plot Fourier transform with period units in 1/µm
freq_x = np.fft.fftshift(np.fft.fftfreq(cols, d=s1.step_x))
freq_y = np.fft.fftshift(np.fft.fftfreq(rows, d=s1.step_y))

# Draw a circle on the real part of fft_shifted
# Using physical units: center at (0, 0) 1/µm with radius 5.0 1/µm
mask = np.zeros((rows, cols))

rc=0.05
mask = fill_circle_in_matrix(mask, 0, 0, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, 0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, 2*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, 3*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, 4*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, 5*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, 6*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, 7*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, -0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, -2*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, -3*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, -4*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, -5*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, -6*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
mask = fill_circle_in_matrix(mask, 0, -7*0.188, rc, step_x=s1.step_x, step_y=s1.step_y, use_physical_units=True)
fft_shifted[mask == 0] = 0

magnitude_spectrum = np.log1p(np.abs(fft_shifted))


fig_fft, ax_fft = plt.subplots(figsize=(8, 8))
extent = [freq_x.min(), freq_x.max(), freq_y.min(), freq_y.max()]
im = ax_fft.imshow(magnitude_spectrum, cmap='gray', extent=extent, origin='lower')
ax_fft.set_title('Fourier Transform of Surface')
ax_fft.set_xlabel('Frequency X [1/µm]')
ax_fft.set_ylabel('Frequency Y [1/µm]')
plt.colorbar(im, ax=ax_fft, label='Log Magnitude')
plt.savefig('fourier_transform.png', dpi=150, bbox_inches='tight')
print('Saved fourier_transform.png')



# Reconstruct image from the shifted FFT
reconstructed = np.fft.ifft2(np.fft.ifftshift(fft_shifted)).real



# Plot the reconstructed image
fig_rec, ax_rec = plt.subplots(figsize=(8, 8))
im_rec = ax_rec.imshow(reconstructed, cmap='viridis', extent=[0, cols * s1.step_x, 0, rows * s1.step_y], origin='lower')
ax_rec.set_title('Reconstructed Image from FFT')
ax_rec.set_xlabel('X [µm]')
ax_rec.set_ylabel('Y [µm]')
plt.colorbar(im_rec, ax=ax_rec, label='Height')
plt.show()
print('Saved reconstructed_image.png')

print(f"FFT shape: {fft_shifted.shape}")
print(f"Max magnitude: {np.abs(fft_shifted).max()}")