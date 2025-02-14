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

# Constants
MINIMUM_RUNNERS = 5
FIGURE_SIZE = (12, 8)
COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k', '#FFA500', '#800080', '#008080']
SIGNIFICANCE_LEVEL = 0.05
CHECKPOINT_DISTANCES = [5, 10, 15, 20, 21.1, 25, 30, 35, 40, 42.2]  # distances in KM

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
    """Calculate trendline parameters."""
    x = np.arange(len(data))
    return np.polyfit(x, data, 1)

def plot_shoe_data(data_to_plot: pd.DataFrame, name: str, color: str, 
                   trendline_data: Dict) -> None:
    """Plot data for a specific shoe or shoe family."""
    runner_count = len(data_to_plot)
    logger.info(f"{name} includes {runner_count} runners")
    
    # Updated: Remove [1:] to include all 10 data points
    processed_data = data_to_plot.drop(['shoeChoice', 'bib'], axis=1).T.astype(float)
    
    avg_curve = processed_data.mean(axis=1)
    x = np.arange(len(avg_curve))
    slope, intercept = calculate_trendline(avg_curve.values)
    
    trendline_data[name] = {
        'slope': slope,
        'intercept': intercept,
        'std': np.std(processed_data.values),
        'n': len(processed_data.columns)
    }
    
    plt.plot(x, avg_curve.values, f'{color}o-', label=f'{name} ({runner_count})')
    plt.plot(x, slope * x + intercept, f'{color}--', alpha=0.5)

def analyze_data(data: pd.DataFrame, shoe_choices: np.ndarray) -> Dict:
    """Analyze and visualize shoe performance data."""
    plt.figure(figsize=FIGURE_SIZE)
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
            plot_shoe_data(family_data, family.name, 
                          COLORS[plot_index % len(COLORS)], trendline_data)
            plot_index += 1
    
    # Process remaining individual shoes
    for shoe in shoe_choices:
        if shoe not in processed_shoes:
            shoe_data = data[data['shoeChoice'] == shoe]
            if len(shoe_data) >= MINIMUM_RUNNERS:
                plot_shoe_data(shoe_data, shoe, 
                             COLORS[plot_index % len(COLORS)], trendline_data)
                plot_index += 1
    
    configure_plot()
    return trendline_data

def configure_plot() -> None:
    """Configure plot parameters."""
    plt.title('Average Pace Profile Comparison')
    plt.xlabel('Distance')
    plt.ylabel('Pace (MPH)')
    distances = ["5K","10K","15K","20K","HALF","25K","30K","35K","40K","Finish Net"]
    plt.xticks(range(len(distances)), distances)
    # Updated: Place legend in the top right inside the plot
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def perform_ancova(trendline_data: Dict, data: pd.DataFrame) -> None:
    """Perform ANCOVA analysis on shoe performance data."""
    if len(trendline_data) < 2:
        logger.warning("Not enough groups to perform statistical comparison.")
        return

    # Prepare data for ANCOVA
    ancova_data = []
    
    # Only process shoes that are in trendline_data
    for shoe_name, shoe_stats in trendline_data.items():
        # Find the corresponding shoe data
        shoe_data = data[data['shoeChoice'].str.contains(shoe_name, case=False)]
        
        # Reshape data for analysis
        shoe_speeds = shoe_data.drop(['shoeChoice', 'bib'], axis=1)
        
        # Update: Use actual checkpoint distances instead of sequential miles
        for runner in shoe_speeds.index:
            runner_speeds = shoe_speeds.loc[runner]
            for distance, speed in zip(CHECKPOINT_DISTANCES, runner_speeds):
                ancova_data.append({
                    'Shoe': shoe_name,
                    'Distance': distance,  # Changed from 'Mile' to 'Distance'
                    'Speed': speed,
                    'Runner': runner
                })
    
    # Convert to DataFrame
    ancova_df = pd.DataFrame(ancova_data)
    
    # Get unique shoes from the ANCOVA data
    shoes = ancova_df['Shoe'].unique()
    
    # Update the ANCOVA model to use Distance instead of Mile
    model = sm.OLS.from_formula('Speed ~ C(Shoe) + Distance', data=ancova_df).fit()
    
    # Print ANCOVA results with better formatting
    logger.info("\n" + "="*50)
    logger.info("ANCOVA RESULTS")
    logger.info("="*50)
    logger.info("Reference shoe (baseline): Adios")  # Add this line
    logger.info("Coefficients show differences compared to Adios\n")  # Add this line
    logger.info(model.summary().tables[1])
    
    # Post-hoc analysis with improved formatting
    logger.info("\n" + "="*50)
    logger.info("POST-HOC ANALYSIS (TUKEY HSD)")
    logger.info("="*50)
    
    # Calculate adjusted means for each shoe
    adjusted_means = {}
    for shoe in shoes:  # Now shoes is defined
        shoe_data = ancova_df[ancova_df['Shoe'] == shoe]
        adjusted_means[shoe] = model.predict({
            'Shoe': [shoe] * len(shoe_data),
            'Distance': shoe_data['Distance']
        }).mean()
    
    # Pairwise comparisons with improved formatting
    for i, shoe1 in enumerate(shoes[:-1]):
        for shoe2 in shoes[i+1:]:
            diff = adjusted_means[shoe1] - adjusted_means[shoe2]
            t_stat, p_val = stats.ttest_ind(
                ancova_df[ancova_df['Shoe'] == shoe1]['Speed'],
                ancova_df[ancova_df['Shoe'] == shoe2]['Speed']
            )
            
            significance = "✓ SIGNIFICANT" if p_val < SIGNIFICANCE_LEVEL else "✗ NOT SIGNIFICANT"
            
            result = (
                f"\n╔{'═'*58}╗\n"
                f"║ {shoe1.upper()} vs {shoe2.upper():<{47-len(shoe1)}}║\n"
                f"╠{'═'*58}╣\n"
                f"║ Adjusted Mean Difference:  {diff:>8.3f} MPH{' '*13}║\n"
                f"║ T-statistic:               {t_stat:>8.3f}{' '*17}║\n"
                f"║ P-value:                   {p_val:>8.4f}{' '*17}║\n"
                f"║ Result:                    {significance:<20}{' '*5}║\n"
                f"╚{'═'*58}╝"
            )
            logger.info(result)

def main():
    """Main execution function."""
    try:
        shoe_choice = load_data(r'D:\BAAFootwear\data\Raw\ShoeChoices.csv')
        speed = load_data(r'D:\BAAFootwear\data\Raw\MilesPerHour.csv')
        
        shoe_choice = fix_shoe_choices(shoe_choice)
        data = merge_data(shoe_choice, speed)
        shoe_choices = get_shoe_choices(data)
        
        trendline_data = analyze_data(data, shoe_choices)
        perform_ancova(trendline_data, data)  # Replace compare_trendlines with perform_ancova
        
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        raise

if __name__ == "__main__":
    main()