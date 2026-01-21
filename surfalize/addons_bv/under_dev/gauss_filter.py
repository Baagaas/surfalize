import numpy as np
import matplotlib.pyplot as plt

def create_2d_gaussian(size_x, size_y, center_x, center_y, sigma_x=None, sigma_y=None, n_pixels=256):
    """
    Create a 2D Gaussian plot.
    
    Parameters
    ----------
    size_x : float
        Size of image in x direction (frequency units, Hz)
    size_y : float
        Size of image in y direction (frequency units, Hz)
    center_x : float
        X coordinate of Gaussian center (frequency units)
    center_y : float
        Y coordinate of Gaussian center (frequency units)
    sigma_x : float, optional
        Standard deviation in x direction. Default is size_x/10
    sigma_y : float, optional
        Standard deviation in y direction. Default is size_y/10
    n_pixels : int, optional
        Resolution of the output image. Default is 256
    
    Returns
    -------
    gaussian : ndarray
        2D Gaussian array with values between 0 and 1
    x_coords : ndarray
        X coordinate array
    y_coords : ndarray
        Y coordinate array
    """
    # Set default sigma values
    if sigma_x is None:
        sigma_x = size_x / 10
    if sigma_y is None:
        sigma_y = size_y / 10
    
    # Create coordinate arrays (frequency domain)
    x_coords = np.linspace(-size_x/2, size_x/2, n_pixels)
    y_coords = np.linspace(-size_y/2, size_y/2, n_pixels)
    X, Y = np.meshgrid(x_coords, y_coords)
    
    # Create 2D Gaussian
    gaussian = np.exp(-((X - center_x)**2 / (2 * sigma_x**2) + 
                         (Y - center_y)**2 / (2 * sigma_y**2)))
    
    # Normalize to [0, 1]
    gaussian = gaussian / gaussian.max()
    
    return gaussian, x_coords, y_coords

# Example usage
gaussian, x, y = create_2d_gaussian(
    size_x=2.0,        # Size in Hz
    size_y=2.0,        # Size in Hz
    center_x=0.5,      # Center at (0.5, 0.5) Hz
    center_y=0.5,
    sigma_x=0.2,       # Width of Gaussian
    sigma_y=0.2
)

# Plot
fig, ax = plt.subplots(figsize=(8, 8))
extent = (x.min(), x.max(), y.min(), y.max())
im = ax.imshow(gaussian, extent=extent, cmap='viridis', origin='lower')
ax.set_xlabel('Frequency X [Hz]')
ax.set_ylabel('Frequency Y [Hz]')
ax.set_title('2D Gaussian Filter')
plt.colorbar(im, ax=ax, label='Magnitude')
plt.show()