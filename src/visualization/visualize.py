import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats



# Load data 
def load_data(data_path):
    data = pd.read_csv(data_path, encoding='latin1')  # Specify correct encoding
    return data

def fix_shoeChoices(data):
    # Add a row for the header using pd.concat
    data = pd.concat([data, data.loc[[0]]], ignore_index=True)
    # Rename the columns
    data.columns = ['bib', 'LastName', 'shoeChoice']
    return data

def merge_data(data1, data2):
    data1['bib'] = data1['bib'].astype(str)  # Convert 'bib' to string
    data2['bib'] = data2['bib'].astype(str)
    data = pd.merge(data1, data2, on='bib', how='inner')
    #drop name columns 
    data = data.drop(['LastName'], axis=1)
    data = data.drop(['name'], axis=1)
    return data

#create a data frame for each shoe in the shoe choice column
def get_shoeChoices(data):
    shoeChoices = data['shoeChoice'].unique()
    #count each shoe choice
    shoeChoiceCount = data['shoeChoice'].value_counts()
    #print the count of each shoe choice and the name of each shoe
    print(shoeChoiceCount)
    return shoeChoices
   
# sort the data by shoe choice
def fit_data(data, shoeChoices):
    # Define shoe families using keywords
    shoe_families = {
        'Adios': [shoe for shoe in shoeChoices if 'adios' in shoe.lower()],
        'Vaporfly': [shoe for shoe in shoeChoices if 'vaporfly' in shoe.lower()],
        'Alphafly': [shoe for shoe in shoeChoices if 'alphafly' in shoe.lower()],
    }
    
    plt.figure(figsize=(12, 8))
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', '#FFA500', '#800080', '#008080']  # Extended color list
    trendline_data = {}
    
    # Track processed shoes to avoid duplicates
    processed_shoes = set()
    plot_index = 0
    
    # First process shoe families
    for family_name, family_shoes in shoe_families.items():
        if not family_shoes:
            continue
            
        family_data = pd.DataFrame()
        for shoe in family_shoes:
            shoe_data = data[data['shoeChoice'] == shoe]
            family_data = pd.concat([family_data, shoe_data])
            processed_shoes.add(shoe)
        
        if len(family_data) > 4:
            plot_data(family_data, family_name, colors[plot_index % len(colors)], trendline_data)
            plot_index += 1
            
    # Then process individual shoes not in families
    for shoe in shoeChoices:
        if shoe not in processed_shoes:
            shoe_data = data[data['shoeChoice'] == shoe]
            if len(shoe_data) > 3:
                plot_data(shoe_data, shoe, colors[plot_index % len(colors)], trendline_data)
                plot_index += 1
    
    plt.title('Average Pace Profile Comparison')
    plt.xlabel('Mile')
    plt.ylabel('Pace (MPH)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Perform statistical comparison of trendlines
    compare_trendlines(trendline_data)
    
    return trendline_data

def plot_data(data_to_plot, name, color, trendline_data):
    runner_count = len(data_to_plot)
    print(f"\n{name} includes {runner_count} runners")
    
    # Process the data
    processed_data = data_to_plot.drop(['shoeChoice', 'bib'], axis=1)
    processed_data = processed_data.T
    processed_data = processed_data[1:]  # Remove header row
    processed_data = processed_data.astype(float)
    
    # Use the original index (splits in KM) for the x-axis
    split_labels = processed_data.index
    # Helper function to extract a float from a string label
    def extract_float(x):
        import re
        match = re.search(r'[\d.]+', str(x))
        return float(match.group()) if match else np.nan
    
    x_numeric = split_labels.map(extract_float)
    
    # Compute average curve and trendline
    avg_curve = processed_data.mean(axis=1)
    m, b = np.polyfit(x_numeric, avg_curve.values, 1)
    
    # Store trendline data
    trendline_data[name] = {
        'slope': m, 
        'intercept': b,
        'std': np.std(processed_data.values),
        'n': len(processed_data.columns)
    }
    
    # Plot using x_numeric so the x-axis shows original KM splits
    plt.plot(x_numeric, avg_curve.values, f'{color}o-', label=f'{name} ({runner_count})')
    plt.plot(x_numeric, m * x_numeric + b, f'{color}--', alpha=0.5)

def compare_trendlines(trendline_data):
    if len(trendline_data) >= 2:
        names = list(trendline_data.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                name1, name2 = names[i], names[j]
                data1, data2 = trendline_data[name1], trendline_data[name2]
                
                t_statistic, p_value = stats.ttest_ind_from_stats(
                    mean1=data1['slope'], std1=data1['std'], nobs1=data1['n'],
                    mean2=data2['slope'], std2=data2['std'], nobs2=data2['n'],
                    equal_var=False
                )
                
                print(f"\nComparing {name1} and {name2}:")
                print(f"T-statistic: {t_statistic:.3f}, P-value: {p_value:.3f}")
                if p_value < 0.05:
                    print("THE SLOPES ARE SIGNIFICANTLY DIFFERENT.")
                else:
                    print("The slopes are not significantly different.")
    else:
        print("\nNot enough groups to perform statistical comparison.")


shoeChoice = load_data(r'D:\BAAFootwear\data\Raw\ShoeChoices.csv')
speed = load_data(r'D:\BAAFootwear\data\Raw\KMH.csv')

shoeChoice = fix_shoeChoices(shoeChoice)

data = merge_data(shoeChoice, speed)

shoeChoices = get_shoeChoices(data)

workingData = fit_data(data, shoeChoices)

