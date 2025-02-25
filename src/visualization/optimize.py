import os
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import statsmodels.api as sm

# Set matplotlib style
plt.style.use('seaborn-v0_8-dark-palette')
# Constants
MINIMUM_RUNNERS = 20
FIGURE_SIZE = (12, 8)
SIGNIFICANCE_LEVEL = 0.05
CHECKPOINT_DISTANCES = ['0K', '5K', '10K', '15K', '20K', '25K', '30K', '35K', '40K', 'Finish']  # distances in KM
CHECKPOINT_METERS = [0,5000,10000,15000,20000,25000,30000,35000,40000,42200]  # convert to meters, marathon is 42.195km


@dataclass
class ShoeFamily:
    name: str
    keywords: List[str]

# Configuration
SHOE_FAMILIES = [
    ShoeFamily("Adios", ["adios"]),
    ShoeFamily("Vaporfly", ["vaporfly"]),
    ShoeFamily("Alphafly", ["alphafly"]),
]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(data_path: str) -> pd.DataFrame:
    """Load data from CSV file with error handling."""
    try:
        return pd.read_csv(data_path, encoding='latin1')
    except Exception as e:
        logger.error(f"Error loading data from {data_path}: {str(e)}")
        raise

def fix_percents(data: pd.DataFrame) -> pd.DataFrame:
    """Fix percentage data structure."""
    #add a column for 0K that is all zeros
    data['0K'] = 0
    #reorder columns
    data = data[['bib', 'name', '0K', '5K', '10K', '15K', '20K', '25K', '30K', '35K', '40K', 'Finish Net']]
    return data

    

def fix_shoe_choices(data: pd.DataFrame) -> pd.DataFrame:
    """Fix shoe choices data structure."""
    data = pd.concat([data, data.loc[[0]]], ignore_index=True)
    data.columns = ['bib', 'LastName', 'shoeChoice']
    #remove any rows with "Question Mark" in the shoeChoice column
    data = data[~data['shoeChoice'].str.contains('Question Mark')]
    return data

def merge_data(data1: pd.DataFrame, data2: pd.DataFrame) -> pd.DataFrame:
    """Merge two dataframes on bib number."""
    merged = pd.merge(
        data1.assign(bib=data1['bib'].astype(str)),
        data2.assign(bib=data2['bib'].astype(str)),
        on='bib',
        how='inner'
    )
    return merged.drop(['LastName', 'name'], axis=1)

def get_shoe_choices(data: pd.DataFrame) -> np.ndarray:
    """Get unique shoe choices and print counts."""
    shoe_counts = data['shoeChoice'].value_counts()
    logger.info("Shoe choice distribution:\n%s", shoe_counts)
    return data['shoeChoice'].unique()

def calculate_trendline(data: np.ndarray) -> Tuple[float, float]:
    """Calculate trendline parameters using actual meter distances."""
    x = np.array(CHECKPOINT_METERS)  # Use actual meter distances
    return np.polyfit(x, data, 1)

def plot_elevation_profile(ax):
    #load the elevation data from csv
    elevation_data = pd.read_csv(r'D:\BAAFootwear\src\visualization\RouteProfile.csv')
    rename = {'Distance from Start (km)': 'Distance (M)', 'Height Above Sea Level (m)': 'Elevation (M)'}
    elevation_data = elevation_data.rename(columns=rename)
    # Convert kilometers to meters in the elevation data
    elevation_data['Distance (M)'] = elevation_data['Distance (M)'] * 1000
    ax.plot(elevation_data['Distance (M)'], elevation_data['Elevation (M)'], 'k-', label='Elevation')
    ax.fill_between(elevation_data['Distance (M)'], elevation_data['Elevation (M)'], color='lightgrey', alpha=0.5)
    ax.set_ylabel('Elevation (M)')
    ax.set_title('Boston Marathon Elevation Profile')
    ax.set_xticks(CHECKPOINT_METERS)
    ax.set_ylim(0, 150)
    ax.legend(loc='upper right')
    ax.grid(True)

    
def plot_shoe_data(data_to_plot: pd.DataFrame, name: str, 
                   trendline_data: Dict, ax) -> None:
    """Plot data for a specific shoe or shoe family."""
    runner_count = len(data_to_plot)
    logger.info(f"{name} includes {runner_count} runners")
    
    processed_data = data_to_plot.drop(['shoeChoice', 'bib'], axis=1).T.astype(float)
    avg_curve = processed_data.mean(axis=1)
    
    # Use the meter distances for x-axis
    x = np.array(CHECKPOINT_METERS)
    slope, intercept = calculate_trendline(avg_curve.values)
    
    trendline_data[name] = {
        'slope': slope,
        'intercept': intercept,
        'std': np.std(processed_data.values),
        'n': len(processed_data.columns)
    }
    
    # Let matplotlib use its default color cycle
    ax.plot(x, avg_curve.values, 'o-', label=f'{name} ({runner_count})')
    ax.plot(x, slope * x + intercept, '--', alpha=0.5)

def analyze_data(data: pd.DataFrame, shoe_choices: np.ndarray) -> Dict:
    """Analyze and visualize shoe performance data."""
    # Create figure with two subplots sharing x-axis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[1, 3], sharex=True)
    fig.subplots_adjust(hspace=0.1)
    
    # Plot elevation profile on top subplot
    plot_elevation_profile(ax1)
    
    # Plot speed data on bottom subplot
    trendline_data = {}
    processed_shoes = set()
    plot_index = 0
    
    # Process shoe families
    for family in SHOE_FAMILIES:
        family_shoes = [shoe for shoe in shoe_choices 
                       if any(kw in shoe.lower() for kw in family.keywords)]
        if not family_shoes:
            continue
            
        family_data = pd.concat([data[data['shoeChoice'] == shoe] 
                               for shoe in family_shoes])
        processed_shoes.update(family_shoes)
        
        if len(family_data) >= MINIMUM_RUNNERS:
            plot_shoe_data(family_data, family.name, trendline_data, ax2)
            plot_index += 1
    
    # Process remaining individual shoes
    for shoe in shoe_choices:
        if shoe not in processed_shoes:
            shoe_data = data[data['shoeChoice'] == shoe]
            if len(shoe_data) >= MINIMUM_RUNNERS:
                plot_shoe_data(shoe_data, shoe, trendline_data, ax2)
                plot_index += 1
    
    configure_plot(ax2)
    # plt.tight_layout()
    plt.show()
    return trendline_data

def configure_plot(ax) -> None:
    """Configure plot parameters."""
    ax.set_title('Average Pace Profile Comparison')
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Percent Pace Change')
    ax.set_xlim(-500, 42700)
    ax.set_xticks(CHECKPOINT_METERS)
    ax.set_xticklabels(CHECKPOINT_DISTANCES)  # Add thousands separator
    ax.legend(loc='upper right')
    ax.grid(True)
    




def main():
    """Main execution function."""
    try:
        shoe_choice = load_data(r'D:\BAAFootwear\data\Raw\ShoeChoices.csv')
        speed = load_data(r'D:\BAAFootwear\data\Raw\KMH_percent_noHalf.csv')
        
        speed = fix_percents(speed)
        shoe_choice = fix_shoe_choices(shoe_choice)
        data = merge_data(shoe_choice, speed)
        shoe_choices = get_shoe_choices(data)
        
        trendline_data = analyze_data(data, shoe_choices)

    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        raise

if __name__ == "__main__":
    main()