import pandas as pd
import numpy as np

def load_and_prepare_data(file_path="interval_workouts.csv"):
    """Load workout data from CSV if available; optional with user-input 2k."""
    try:
        df = pd.read_csv(file_path)
        numeric_cols = ["Reps", "Interval Distance", "Rest Time", "Latest 2000m Split", 
                        "Latest 5000m Split", "Latest 30@20 Split", "500m Split (s)"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        df = df.dropna(subset=numeric_cols)
        return df
    except FileNotFoundError:
        return None

def calculate_factors(interval_distance, num_intervals, rest_time):
    """
    Calculate relative speed factors for distance, reps, and rest.
    - Relative speed < 1 = faster than baseline, > 1 = slower.
    - Calibrated to 8*500m (2) ≈ 2k - 1s (e.g., 95s for 2k = 96s).
    """
    # Distance factor: Increases as distance goes from 50m to 5000m
    # 50m = 0.95 (fast), 500m ≈ 1.00 (baseline), 5000m = 1.18 (5k pace)
    d_min, d_max = 50, 5000
    d_scale = 2500  # Adjusted for smoother gradient
    distance_factor = 0.95 + 0.23 * (1 - np.exp(-interval_distance / d_scale))
    # - 50m: ~0.95
    # - 500m: ~1.00 (96 * 1.00 * 1.00 * 0.98 ≈ 94s → 95s)
    # - 1000m: ~1.06 (~102s with 8 reps, 2min)
    # - 5000m: ~1.18

    # Reps factor: Decreases as reps go from 50 to 1
    # 8 reps = 1.00 (baseline), fewer = faster, more = slower
    r_min, r_max = 1, 50
    reps_factor = 0.95 + (num_intervals - 1) * (0.10 / (50 - 1))
    # - 1 rep: 0.95
    # - 8 reps: ~1.00
    # - 50 reps: 1.05

    # Rest factor: Decreases as rest goes from 1min to 9min, subtle effect
    # 2min = 0.98 (baseline), extremes adjust slightly
    t_min, t_max = 1, 9
    rest_factor = 1.01 - (rest_time - 1) * (0.07 / (9 - 1))
    # - 1min: 1.01
    # - 2min: 0.98
    # - 9min: 0.94

    return distance_factor, reps_factor, rest_factor

def predict_target_split(interval_distance, num_intervals, rest_time, erg_splits):
    """
    Predict target split in seconds per 500m.
    - Baseline from erg splits (2k primary, 5k for long, blend in between).
    - Adjusted by continuous gradients.
    """
    latest_2000m, latest_5000m, latest_30at20 = erg_splits
    
    # Baseline: 2k for short (<750m), 5k for long (>2000m), blend in between
    if interval_distance <= 750:
        base_split = latest_2000m
    elif interval_distance >= 3000:
        base_split = latest_5000m
    else:
        weight = (interval_distance - 750) / (3000 - 750)
        base_split = latest_2000m * (1 - weight) + latest_5000m * weight
    
    # Calculate factors
    distance_factor, reps_factor, rest_factor = calculate_factors(interval_distance, num_intervals, rest_time)
    
    # Combine factors
    relative_speed = distance_factor * reps_factor * rest_factor
    
    # Target split
    target_split = base_split * relative_speed
    
    # Bounds: ±20% of baseline
    return max(min(target_split, base_split * 1.2), base_split * 0.8)