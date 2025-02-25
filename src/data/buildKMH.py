import pandas as pd
import matplotlib.pyplot as plt


# Read the CSV file
file_path = "D:/BAAFootwear/data/Raw/RaceTimeSeconds.csv"
data = pd.read_csv(file_path)
df = pd.DataFrame(data)

# Define checkpoint distances in km
distances = {
    '5K': 5000,
    '10K': 10000,
    '15K': 15000,
    '20K': 20000,
    '25K': 25000,
    '30K': 30000,
    '35K': 35000,
    '40K': 40000,
    'Finish Net': 42200
}

#remove the Half column
df = df.drop(columns=['HALF'])

# # First convert all times to hours
# for key in distances:
#     df[f'{key}_hours'] = (df[key]) / 3600


df_speed = df.copy()
# Calculate speeds between checkpoints
checkpoints = list(distances.keys())
for i in range(len(checkpoints)):  # Changed to include all checkpoints
    current = checkpoints[i]
    if i == 0: #for the first checkpoint
        df_speed[current] = distances[current] / df[current]
    else:
        prev_point = checkpoints[i-1]
        # Calculate time difference between checkpoints
        time_diff = df[current] - df[prev_point]
        # Calculate distance between checkpoints
        distance_diff = distances[current] - distances[prev_point]
        # Calculate speed between checkpoints
        df_speed[current] = distance_diff / time_diff

# checkpoints = list(distances.keys())
# for i in range(len(checkpoints)):  # Changed to include all checkpoints
#     current = checkpoints[i]
#     if i == 0: #for the first checkpoint
#         df[current] = distances[current] / df[f'{current}_hours']
#     else:
#         prev_point = checkpoints[i-1]
#         # Calculate time difference between checkpoints
#         time_diff = df[f'{current}_hours'] - df[f'{prev_point}_hours']
#         # Calculate distance between checkpoints
#         distance_diff = distances[current] - distances[prev_point]
#         # Calculate speed between checkpoints
#         df[current] = distance_diff / time_diff


# Create percent change dataframe
df_percent = df_speed.copy()
base_speed = df_speed['5K']  # Using 5K as the reference point

# Calculate percent change relative to 5K (negative values indicate slower speeds)
for checkpoint in checkpoints:
    df_percent[checkpoint] = ((df_speed[checkpoint] - base_speed) / base_speed) * 100


#create a boxplot for the percent change data
plt.figure(figsize=(12, 8))
df_speed.boxplot()

plt.show()


# Save both dataframes to CSV files
df_speed.to_csv("D:/BAAFootwear/data/Raw/MeterPerSec.csv", index=False)
df_percent.to_csv("D:/BAAFootwear/data/Raw/KMH_percent_noHalf.csv", index=False)