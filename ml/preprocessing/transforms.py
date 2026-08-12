import numpy as np
import pydicom
from typing import Tuple, Union

def convert_to_hu(pixel_array: np.ndarray, rescale_intercept: float, rescale_slope: float) -> np.ndarray:
    """
    Converts DICOM pixel array to Hounsfield Units (HU).
    """
    # Use float32 to prevent overflow and maintain precision during calculation
    hu_image = pixel_array.astype(np.float32)
    hu_image = hu_image * rescale_slope + rescale_intercept
    return hu_image

def apply_window(hu_image: np.ndarray, window_center: float, window_width: float) -> np.ndarray:
    """
    Applies a specific window to the HU image.
    Returns normalized image between 0 and 1.
    """
    img_min = window_center - window_width // 2
    img_max = window_center + window_width // 2
    
    # Clip values to the window range
    windowed_img = np.clip(hu_image, img_min, img_max)
    
    # Normalize between 0 and 1
    windowed_img = (windowed_img - img_min) / window_width
    
    return windowed_img

def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Min-max normalization of an image array to [0, 1].
    """
    img_min = image.min()
    img_max = image.max()
    if img_max - img_min > 0:
        return (image - img_min) / (img_max - img_min)
    return np.zeros_like(image)

def get_multi_window_image(hu_image: np.ndarray) -> np.ndarray:
    """
    Applies three different clinical windows to create a 3-channel image (RGB-like).
    Channel 0: Brain Window (W:80, L:40)
    Channel 1: Subdural Window (W:130-300, L:50-100) -> using W:200, L:80 as standard
    Channel 2: Bone Window (W:2800, L:600)
    
    Returns array of shape (3, H, W).
    """
    brain_img = apply_window(hu_image, 40, 80)
    subdural_img = apply_window(hu_image, 80, 200)
    bone_img = apply_window(hu_image, 600, 2800)
    
    # Stack channels
    multi_channel_img = np.stack([brain_img, subdural_img, bone_img], axis=0)
    return multi_channel_img

def resize_image(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    """
    Resizes the image to the specified (H, W) using torch/torchvision or simple numpy methods.
    Since we are using PyTorch eventually, we can rely on torchvision transforms later,
    but we provide a simple placeholder or use PIL/cv2/scipy.
    For simplicity in raw numpy without cv2, we can just use torch interpolation later.
    """
    import torch
    import torch.nn.functional as F
    
    # Check if image is 2D or 3D (C, H, W)
    if image.ndim == 2:
        # Add batch and channel dimension (1, 1, H, W)
        tensor_img = torch.from_numpy(image).unsqueeze(0).unsqueeze(0)
    elif image.ndim == 3:
        # Add batch dimension (1, C, H, W)
        tensor_img = torch.from_numpy(image).unsqueeze(0)
    else:
        raise ValueError("Image must be 2D or 3D")
        
    resized = F.interpolate(tensor_img, size=size, mode='bilinear', align_corners=False)
    
    return resized.squeeze(0).numpy()
