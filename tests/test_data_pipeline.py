import pytest
import numpy as np
import pandas as pd
import tempfile
import os

from ml.preprocessing.transforms import convert_to_hu, apply_window, get_multi_window_image
from ml.datasets.splitter import create_patient_level_splits

def test_convert_to_hu():
    # Mock pixel array
    pixel_array = np.array([[-100, 0, 100], [200, 300, 400]])
    rescale_intercept = -1024
    rescale_slope = 1.0
    
    hu_image = convert_to_hu(pixel_array, rescale_intercept, rescale_slope)
    expected = np.array([[-1124, -1024, -924], [-824, -724, -624]])
    
    np.testing.assert_array_equal(hu_image, expected)

def test_apply_window():
    hu_image = np.array([[-10, 30, 40], [50, 80, 120]])
    # Brain window W:80 L:40 => Range is [0, 80]
    windowed = apply_window(hu_image, window_center=40, window_width=80)
    
    assert windowed.min() >= 0.0
    assert windowed.max() <= 1.0
    
    # Values <= 0 should be 0, >= 80 should be 1
    assert windowed[0, 0] == 0.0 # -10
    assert windowed[1, 1] == 1.0 # 80
    assert windowed[1, 2] == 1.0 # 120

def test_get_multi_window_image():
    hu_image = np.random.randint(-1000, 1000, size=(100, 100))
    multi_window = get_multi_window_image(hu_image)
    
    assert multi_window.shape == (3, 100, 100)
    assert multi_window.min() >= 0.0
    assert multi_window.max() <= 1.0

def test_patient_level_split():
    # Create mock dataset
    data = {
        'ID': ['ID_1', 'ID_2', 'ID_3', 'ID_4', 'ID_5', 'ID_6', 'ID_7'],
        'PatientID': ['P1', 'P1', 'P2', 'P2', 'P3', 'P4', 'P5'],
        'any': [1, 1, 0, 0, 1, 0, 1]
    }
    df = pd.DataFrame(data)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        csv_path = os.path.join(temp_dir, 'data.csv')
        df.to_csv(csv_path, index=False)
        
        create_patient_level_splits(csv_path, temp_dir, train_size=0.6, val_size=0.2, test_size=0.2)
        
        train_df = pd.read_csv(os.path.join(temp_dir, 'train_split.csv'))
        val_df = pd.read_csv(os.path.join(temp_dir, 'val_split.csv'))
        test_df = pd.read_csv(os.path.join(temp_dir, 'test_split.csv'))
        
        train_patients = set(train_df['PatientID'])
        val_patients = set(val_df['PatientID'])
        test_patients = set(test_df['PatientID'])
        
        # Verify no overlap
        assert len(train_patients.intersection(val_patients)) == 0
        assert len(train_patients.intersection(test_patients)) == 0
        assert len(val_patients.intersection(test_patients)) == 0
