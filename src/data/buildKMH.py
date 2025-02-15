import pandas as pd
import numpy as np

# Read the CSV file
file_path = "D:/BAAFootwear/data/Raw/RaceTime.csv"
data = pd.read_csv(file_path)
df = pd.DataFrame(data)

# Define checkpoint distances in km
distances = {
    '5K': 5,
    '10K': 10,
    '15K': 15,
    '20K': 20,
    'HALF': 21.1,
    '25K': 25,
    '30K': 30,
    '35K': 35,
    '40K': 40,
    'Finish Net': 42.2
}

# First convert all times to hours
for key in distances:
    df[f'{key}_hours'] = pd.to_timedelta(df[key]).dt.total_seconds() / 3600

# Calculate speeds between checkpoints
checkpoints = list(distances.keys())
for i in range(len(checkpoints)):  # Changed to include all checkpoints
    current = checkpoints[i]
    if i < len(checkpoints) - 1:  # For all but the last checkpoint
        next_point = checkpoints[i+1]
        
        # Calculate time difference between checkpoints
        time_diff = df[f'{next_point}_hours'] - df[f'{current}_hours']
        # Calculate distance between checkpoints
        distance_diff = distances[next_point] - distances[current]
        # Calculate speed between checkpoints
        df[current] = distance_diff / time_diff
    else:  # For the last checkpoint (Finish Net)
        prev_point = checkpoints[i-1]
        # Calculate time difference between checkpoints
        time_diff = df[f'{current}_hours'] - df[f'{prev_point}_hours']
        # Calculate distance between checkpoints
        distance_diff = distances[current] - distances[prev_point]
        # Calculate speed between checkpoints
        df[current] = distance_diff / time_diff

# Create percent change dataframe
df_percent = df.copy()
base_speed = df['5K']  # Using 5K as the reference point

# Calculate percent change relative to 5K (negative values indicate slower speeds)
for checkpoint in checkpoints:
    df_percent[checkpoint] = ((df[checkpoint] - base_speed) / base_speed) * 100

# Remove the temporary hours columns from both dataframes
hours_columns = [col for col in df.columns if col.endswith('_hours')]
df = df.drop(columns=hours_columns)
df_percent = df_percent.drop(columns=hours_columns)

# Save both dataframes to CSV files
df.to_csv("D:/BAAFootwear/data/Raw/KMH.csv", index=False)
df_percent.to_csv("D:/BAAFootwear/data/Raw/KMH_percent.csv", index=False)