import pandas as pd
import string
import time

def process_url(url):
    # Read the table from the website
    
    RaceTime = pd.DataFrame()
    MinMile = pd.DataFrame()
    MilesPerHour= pd.DataFrame()
    
    tables = pd.read_html(url)

    name = tables[0].iloc[0, :]
    bib = tables[0].iloc[2, :]

    # Create a DataFrame from name and bib
    df = pd.DataFrame({'name': name, 'bib': bib})
    
    # Drop the first row
    df = df.drop(0)

    # Assuming the table you want is the first one
    times = tables[3]
    # Convert the times to a DataFrame
    df_times = pd.DataFrame(times)

    # Check for '-' in name or times DataFrame
    if '-' in df['name'].values or '-' in df_times.values:
        return None, None, None
    
    realdata = df_times.iloc[0:14, 0]
    # Delete the rows in realdata that contain '*'
    realdata = realdata[~realdata.str.contains(r'\*', regex=True)]
    
    # Check if df_times has enough rows to drop
    if df_times.shape[0] < 14 or realdata.shape[0] < 14:
        return None, None, None
    
    # Drop the first row
    df_times = df_times.drop([7, 8, 10, 11, 13])
    
        # Check if df_times has enough columns
    if df_times.shape[1] < 6:
        return None, None, None
    
    # I want to keep the Split column and the time columns
    RaceTime = df_times.iloc[:, [0, 2]].T
    MinMile = df_times.iloc[:, [0, 4]].T
    MilesPerHour = df_times.iloc[:, [0, 5]].T

    # Set the first row as the column names for RaceTime
    RaceTime.columns = RaceTime.iloc[0]
    RaceTime = RaceTime.drop(RaceTime.index[0])

    # Set the first row as the column names for MinMile
    MinMile.columns = MinMile.iloc[0]
    MinMile = MinMile.drop(MinMile.index[0])

    # Set the first row as the column names for MilesPerHour
    MilesPerHour.columns = MilesPerHour.iloc[0]
    MilesPerHour = MilesPerHour.drop(MilesPerHour.index[0])

    # Join df and RaceTime
    RaceTime = pd.concat([df.reset_index(drop=True), RaceTime.reset_index(drop=True)], axis=1)
    MinMile = pd.concat([df.reset_index(drop=True), MinMile.reset_index(drop=True)], axis=1)
    MilesPerHour = pd.concat([df.reset_index(drop=True), MilesPerHour.reset_index(drop=True)], axis=1)

    return RaceTime, MinMile, MilesPerHour

# List of URLs to process
# urls_list = [
#     'https://results.baa.org/2024/?content=detail&fpid=search&pid=search&idp=9TGHS6FF19CD8B',
#     'https://results.baa.org/2024/?content=detail&fpid=search&pid=search&idp=9TGHS6FF19ED5B',
#     'https://results.baa.org/2024/?content=detail&fpid=search&pid=search&idp=9TGHS6FF19AA1A',
#     'https://results.baa.org/2024/?content=detail&fpid=search&pid=search&idp=9TGHS6FF19AA0D'
# ]

#Create a list of all possible combinations of 'AA2A' to 'ZZ9Z'
combinations = []
for a in string.ascii_uppercase:
    for b in string.ascii_uppercase:
        for c in string.digits:
            for d in string.ascii_uppercase[0:10]:
                combinations.append(f'{a}{b}{c}{d}')
                
# append the combinations to the end of the URL
url = str('https://results.baa.org/2024/?content=detail&fpid=search&pid=search&idp=9TGHS6FF19')

urls = [f'{url}{combination}' for combination in combinations]

# Initialize empty lists to store results
all_RaceTime = []
all_MinMile = []
all_MilesPerHour = []
checked = 0

# Loop through the URLs and process each one
for url in urls:
    RaceTime, MinMile, MilesPerHour = process_url(url)
    if RaceTime is not None and MinMile is not None and MilesPerHour is not None:
        all_RaceTime.append(RaceTime)
        all_MinMile.append(MinMile)
        all_MilesPerHour.append(MilesPerHour)
    # time.sleep(.25)
    #create a tracker to show percentage of urls checked
    checked = checked + 1
    print(f"{url} finished, {len(all_RaceTime)} Runners collected, {round(checked/len(urls)*100, 3)}% of URLs Checked")
    
    
        
# Concatenate all results into DataFrames
df_RaceTime = pd.concat(all_RaceTime, ignore_index=True)
df_MinMile = pd.concat(all_MinMile, ignore_index=True)
df_MilesPerHour = pd.concat(all_MilesPerHour, ignore_index=True)

# Save the DataFrames to CSV files
df_RaceTime.to_csv('data\Raw\RaceTime.csv', index=False)
df_MinMile.to_csv('data\Raw\MinMile.csv', index=False)
df_MilesPerHour.to_csv('data\Raw\MilesPerHour.csv', index=False)


