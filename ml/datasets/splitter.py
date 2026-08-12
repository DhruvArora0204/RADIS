import pandas as pd
import numpy as np
import os
from sklearn.model_selection import GroupShuffleSplit

def create_patient_level_splits(
    csv_path: str, 
    output_dir: str,
    train_size: float = 0.7, 
    val_size: float = 0.15,
    test_size: float = 0.15,
    random_state: int = 42
):
    """
    Splits the RSNA dataset into train, validation, and test sets.
    Crucially, ensures that all slices from a single patient (StudyInstanceUID or PatientID)
    stay in the same split to prevent data leakage.
    
    Assumes the CSV has at least:
    - 'SOPInstanceUID' (or 'ID')
    - 'PatientID' (or 'StudyInstanceUID') for grouping
    - label columns (any, epidural, intraparenchymal, intraventricular, subarachnoid, subdural)
    """
    
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Cannot perform split.")
        return
        
    df = pd.read_csv(csv_path)
    
    if 'PatientID' not in df.columns:
        raise ValueError("CSV must contain a 'PatientID' column to group by.")
    
    # We want to split the remaining (val + test) after train split
    val_test_ratio = val_size / (val_size + test_size)
    
    # 1. Split Train vs (Val + Test)
    gss_train = GroupShuffleSplit(n_splits=1, train_size=train_size, random_state=random_state)
    train_idx, val_test_idx = next(gss_train.split(df, groups=df['PatientID']))
    
    df_train = df.iloc[train_idx]
    df_val_test = df.iloc[val_test_idx]
    
    # 2. Split Val vs Test
    gss_val = GroupShuffleSplit(n_splits=1, train_size=val_test_ratio, random_state=random_state)
    val_idx, test_idx = next(gss_val.split(df_val_test, groups=df_val_test['PatientID']))
    
    df_val = df_val_test.iloc[val_idx]
    df_test = df_val_test.iloc[test_idx]
    
    # Verification
    train_patients = set(df_train['PatientID'])
    val_patients = set(df_val['PatientID'])
    test_patients = set(df_test['PatientID'])
    
    assert len(train_patients.intersection(val_patients)) == 0, "Leakage detected between Train and Val"
    assert len(train_patients.intersection(test_patients)) == 0, "Leakage detected between Train and Test"
    assert len(val_patients.intersection(test_patients)) == 0, "Leakage detected between Val and Test"
    
    # Save splits
    os.makedirs(output_dir, exist_ok=True)
    df_train.to_csv(os.path.join(output_dir, 'train_split.csv'), index=False)
    df_val.to_csv(os.path.join(output_dir, 'val_split.csv'), index=False)
    df_test.to_csv(os.path.join(output_dir, 'test_split.csv'), index=False)
    
    print(f"Splits saved to {output_dir}")
    print(f"Train: {len(df_train)} slices, Val: {len(df_val)} slices, Test: {len(df_test)} slices")

if __name__ == "__main__":
    # Example usage:
    # create_patient_level_splits('path/to/rsna_processed.csv', 'data/splits/')
    pass
