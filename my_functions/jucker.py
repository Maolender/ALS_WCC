import numpy as np 
import pandas as pd


# Define the main function to calculate all biomass and carbon content statistics
def calculate_biomass_summary(df, ratio_bgb_to_agb, species_mix_proportions):
    """
    Calculate the AGB, BGB, Carbon Content, and CO2 equivalents for each planting type and year,
    as well as the overall totals.

    Parameters:
        df (pd.DataFrame): DataFrame containing tree data.
        ratio_bgb_to_agb (float): Ratio of Below-Ground Biomass (BGB) to Above-Ground Biomass (AGB).
        species_mix_proportions (dict): Dictionary with species mix proportions for each planting type.

    Returns:
        pd.DataFrame: Summary DataFrame with total AGB, mean AGB, number of trees, total BGB,
                      carbon content, and CO2 content for each planting type and year.
    """
    # Parameters for AGB calculation
    exp_factor_agb = np.exp(0.204**2 / 2)

    # Calculate AGB for angiosperms and gymnosperms
    df['AGB_angiosperm'] = 0.016 * (df['top_height'] * df['diameter'])**2.013 * exp_factor_agb
    df['AGB_gymnosperm'] = 0.109 * (df['top_height'] * df['diameter'])**1.790 * exp_factor_agb

    # Function to calculate the weighted AGB based on the species mix
    def calculate_agb_weighted(row):
        mix = row['Type']
        angiosperm_weight, gymnosperm_weight = species_mix_proportions.get(mix, (0, 0))
        return angiosperm_weight * row['AGB_angiosperm'] + gymnosperm_weight * row['AGB_gymnosperm']

    # Apply the weighted AGB calculation to each row
    df['AGB_total'] = df.apply(calculate_agb_weighted, axis=1)

    # Convert AGB from kilograms to tonnes (1 tonne = 1000 kg)
    df['AGB_total_tonnes'] = df['AGB_total'] / 1000

    # Group by planting type and year, then calculate the total AGB, mean AGB, and count of trees
    agb_summary = df.groupby(['Type', 'Year']).agg(
        Total_AGB=('AGB_total_tonnes', 'sum'),
        Mean_AGB=('AGB_total_tonnes', 'mean'),
        Number_of_Trees=('AGB_total_tonnes', 'size')
    ).reset_index()

   # Calculate BGB, Carbon Content, and CO2 equivalents for each group
    agb_summary['Total_BGB'] = agb_summary['Total_AGB'] * ratio_bgb_to_agb
    agb_summary['Carbon_Content'] = (agb_summary['Total_AGB'] + agb_summary['Total_BGB']) * 0.5
    agb_summary['CO2_Content'] = agb_summary['Carbon_Content'] * (44 / 12)

    return agb_summary