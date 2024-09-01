# WCC 
# Functions:
# - tree_statistics
# - calculate_tariff_numbers_and_volume
# - calculate_biomass
# - calculate_carbon_and_co2_for_trees_and_saplings
# - print_tree_statistics

import numpy as np  
import math         
import pandas as pd 

def tree_statistics(df, percentages, planting_mix, year=1):
    """
    Calculate tree statistics including numbers, height averages, saplings, large trees,
    DBH, mean quadratic DBH, basal area, and species distribution.

    Parameters:
        df (DataFrame): The DataFrame containing tree data.
        percentages (dict): A dictionary with species names as keys and their percentages as values.
        planting_mix (str): The type of planting mix (e.g., 'Mixed Wood').
        year (int): The planting phase number. Default is 1.

    Returns:
        dict: A dictionary containing all the calculated statistics.
    """

    # Filter the data for trees, saplings, and large trees
    filtered_df_trees = df[(df['Type'] == planting_mix) & 
                          (df['Year'] == year) &  
                          (df['DBH'] > 7)]
                           
    filtered_df_saplings = df[(df['Type'] == planting_mix) & 
                              (df['Year'] == year) &  
                              (df['DBH'] <= 7)]
    
    filtered_df_largetrees = df[(df['Type'] == planting_mix) & 
                                (df['Year'] == year) &  
                                (df['DBH'] > 50)]

   # Count the total number of trees, saplings, and large trees
    number_of_trees = len(filtered_df_trees)
    number_of_saplings = len(filtered_df_saplings)
    number_of_largetrees = len(filtered_df_largetrees)
    
    
    # Calculate the number of trees and saplings for each species based on the given percentages
    species_distribution = {}
    total_trees_allocated = 0
    total_saplings_allocated = 0
    total_large_trees_allocated = 0
    
    # Initial allocation based on percentage
    for species, percentage in percentages.items():
        num_trees = int(number_of_trees * percentage)
        num_saplings = int(number_of_saplings * percentage)
        num_large_trees = int(number_of_largetrees * percentage)

        species_distribution[species] = {
            'trees': num_trees,
            'saplings': num_saplings,
            'largetrees': num_large_trees
        }

        total_trees_allocated += num_trees
        total_saplings_allocated += num_saplings
        total_large_trees_allocated += num_large_trees

    # Distribute remaining trees
    remaining_trees = number_of_trees - total_trees_allocated
    remaining_saplings = number_of_saplings - total_saplings_allocated
    remaining_large_trees = number_of_largetrees - total_large_trees_allocated

    species_list = list(percentages.keys())
    index = 0

    while remaining_trees > 0:
        species_distribution[species_list[index % len(species_list)]]['trees'] += 1
        remaining_trees -= 1
        index += 1

    index = 0
    while remaining_saplings > 0:
        species_distribution[species_list[index % len(species_list)]]['saplings'] += 1
        remaining_saplings -= 1
        index += 1

    index = 0
    while remaining_large_trees > 0:
        species_distribution[species_list[index % len(species_list)]]['largetrees'] += 1
        remaining_large_trees -= 1
        index += 1

    # Calculate the mean tree height and mean DBH one for all trees 
    mean_tree_height = filtered_df_trees['top_height'].mean()
    mean_dbh_trees = filtered_df_trees['DBH'].mean()

    # Calculate the mean tree height and mean DBH for all saplings
    mean_sapling_height = filtered_df_saplings['top_height'].mean()
    mean_dbh_saplings = filtered_df_saplings['DBH'].mean()

    # Calculate the mean tree height and mean DBH one for large trees, if any
    if number_of_largetrees > 0:
        mean_largetree_height = filtered_df_largetrees['top_height'].mean()
        mean_dbh_largetrees = filtered_df_largetrees['DBH'].mean()
    else:
        mean_largetree_height = None
        mean_dbh_largetrees = None

    # Calculate the quadratic mean DBH one for all trees 
    squared_dbh = filtered_df_trees['DBH'] ** 2
    mean_squared_dbh = squared_dbh.mean()
    quadratic_mean_dbh = np.sqrt(mean_squared_dbh)
    quadratic_mean_dbh = round(quadratic_mean_dbh, 1) # rounded to the nearest 0.1cm

    # Calculate mean tree basal area (ba) one for all trees 
    mean_basal_area = (np.pi * (quadratic_mean_dbh / 200)**2) # to meters squared

    # Return all the calculated statistics
    return {
        'number_of_trees': number_of_trees,
        'number_of_saplings': number_of_saplings,
        'number_of_largetrees': number_of_largetrees,
        'mean_tree_height': mean_tree_height,
        'mean_dbh_trees': mean_dbh_trees,
        'mean_sapling_height': mean_sapling_height,
        'mean_dbh_saplings': mean_dbh_saplings,
        'mean_largetree_height': mean_largetree_height,
        'mean_dbh_largetrees': mean_dbh_largetrees,
        'quadratic_mean_dbh': quadratic_mean_dbh,
        'mean_basal_area': mean_basal_area,
        'species_distribution': species_distribution
    }


def calculate_tariff_numbers_and_volume(tree_stats, species):
    """
    Calculate the tariff numbers and tree volume using the provided tree statistics.

    Parameters:
        tree_stats (dict): A dictionary containing tree statistics.
        species (str): The species for which to calculate the tariff number and volume.

    Returns:
        dict: A dictionary containing the tariff number and tree volume for the species.
    """
    mean_tree_height = tree_stats['mean_tree_height']
    quadratic_mean_dbh = tree_stats['quadratic_mean_dbh']
    mean_basal_area = tree_stats['mean_basal_area']
    species_distribution = tree_stats['species_distribution']
    mean_dbh_trees= tree_stats['mean_dbh_trees']
    
    
    # Define species-specific constants for broadleaf species 
    broadleaf_constants = {
        'oak': (5.88300, 2.01230, -0.0054780, -0.0057397),
        'beech': (7.48490, 1.92620, -0.0037881, -0.0082745),
        'sycamore': (9.76130, 1.58670, -0.0569660, -0.0033867),
        'ash': (9.16050, 2.02560, -0.0668420, -0.0044172),
        'birch': (5.62370, 2.23800, 0.0871700, -0.0332620),
        'elm': (6.28870, 1.69950, 0.0285120, -0.0069294),
        'poplar': (10.90625, 1.05327, 0.0, 0.0)  
    }

    # Define species-specific constants for conifer species 
    conifer_constants = {
        'Scots pine': (9.817387, 1.177486, -0.114174),
        'Corsican pine': (5.070842, 1.754053, -0.193834),
        'lodgepole pine': (8.855292, 1.951643, -0.689619),
        'Sitka spruce': (8.292030, 1.771173, -0.416509),
        'Norway spruce': (9.939311, 1.985697, -0.650625),
        'European larch': (5.562167, 1.908473, -0.426567),
        'Japanese larch': (8.478127, 1.788768, -0.449816),
        'Douglas fir': (10.397480, 1.477313, -0.325653),
        'western hemlock': (8.762511, 1.959230, -0.586275),
        'western red cedar': (10.637312, 1.735383, -0.630551),
        'grand fir': (6.565630, 2.043490, -0.591550),
        'noble fir': (7.028548, 1.930016, -0.373808)
        }
    
    # Calculate tariff number for the species
    if species in conifer_constants:
        # Get conifer constants
        a1, a2, a3 = conifer_constants[species]
        # Equation 3: Single tree tariff number for conifers
        tariff_number = a1 + (a2 * mean_tree_height) + (a3 * mean_dbh_trees)
    elif species in broadleaf_constants:
        # Get broadleaf constants
        a1, a2, a3, a4 = broadleaf_constants[species]
        # Equation 3: Single tree tariff number for broadleaves 
        tariff_number = a1 + (a2 * mean_tree_height) + (a3 * mean_dbh_trees) + (a4 * mean_dbh_trees * mean_tree_height)
    else:
        raise ValueError(f"Species '{species}' not found in either conifer or broadleaf constants.")
    
    
    # Round down the tariff number to the nearest whole number
    tariff_number = math.floor(tariff_number)
    
    
    # Calculate a2
    a2 = 0.315049301 * (tariff_number - 0.138763302)
    
    # Calculate a1
    a1 = (0.0360541 * tariff_number) - (a2 * 0.118288)

    # Calculate tree volume (v)
    mean_tree_volume = a1 + (a2 * mean_basal_area)

    # Calculate total estimated stem volume for the species
    total_volume = mean_tree_volume * species_distribution[species]['trees']
    
    # Determine the multiplication factor based on mean DBH
    mean_dbh_trees = tree_stats['mean_dbh_trees']
    if mean_dbh_trees >= 33:
        multiplication_factor = 1.00
    elif mean_dbh_trees >= 32:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 31:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 30:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 29:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 28:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 27:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 26:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 25:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 24:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 23:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 22:
        multiplication_factor = 1.01
    elif mean_dbh_trees >= 21:
        multiplication_factor = 1.02
    elif mean_dbh_trees >= 20:
        multiplication_factor = 1.02
    elif mean_dbh_trees >= 19:
        multiplication_factor = 1.02
    elif mean_dbh_trees >= 18:
        multiplication_factor = 1.02
    elif mean_dbh_trees >= 17:
        multiplication_factor = 1.03
    elif mean_dbh_trees >= 16:
        multiplication_factor = 1.03
    elif mean_dbh_trees >= 15:
        multiplication_factor = 1.04
    elif mean_dbh_trees >= 14:
        multiplication_factor = 1.05
    elif mean_dbh_trees >= 13:
        multiplication_factor = 1.06
    elif mean_dbh_trees >= 12:
        multiplication_factor = 1.07
    elif mean_dbh_trees >= 11:
        multiplication_factor = 1.09
    elif mean_dbh_trees >= 10:
        multiplication_factor = 1.12
    elif mean_dbh_trees >= 9:
        multiplication_factor = 1.15
    elif mean_dbh_trees >= 8:
        multiplication_factor = 1.19
    else:
        multiplication_factor = 1.30  # Mean DBH = 7 cm

    # Adjust total volume using the multiplication factor
    total_stem_volume = total_volume * multiplication_factor
    

    # Return the calculated tariff number and volume
    return {
        'tariff_number': tariff_number,
        'mean_tree_volume': mean_tree_volume,
        'total_stem_volume': total_stem_volume
    }



def calculate_biomass(tree_stats, species, volume_stats):
    """
    Calculate the stem biomass, crown biomass, root biomass, above-ground biomass (AGB),
    and total biomass for a given species using the provided tree statistics and volume.

    Parameters:
        tree_stats (dict): A dictionary containing tree statistics.
        species (str): The species for which to calculate biomass.
        volume_stats (dict): A dictionary containing the volume statistics for the species.

    Returns:
        dict: A dictionary containing the stem biomass, crown biomass, root biomass,
              above-ground biomass (AGB), and total biomass.
    """

    # Table 5.2.1: Nominal Specific Gravity (NSG) for different species
    nominal_specific_gravity = {
        'Scots pine': 0.42,
        'Corsican pine': 0.40,
        'lodgepole pine': 0.39,
        'maritime pine': 0.41,
        'Weymouth pine': 0.29,
        'Sitka spruce': 0.33,
        'Norway spruce': 0.33,
        'Omorika spruce': 0.33,
        'European larch': 0.45,
        'Japanese larch': 0.41,
        'hybrid larch': 0.38,
        'Douglas fir': 0.41,
        'western hemlock': 0.36,
        'western red cedar': 0.31,
        'Lawson cypress': 0.33,
        'Leyland cypress': 0.38,
        'grand fir': 0.30,
        'noble fir': 0.31,
        'silver fir': 0.38,
        'oak': 0.56,
        'red oak': 0.57,
        'beech': 0.55,
        'sycamore': 0.49,
        'ash': 0.53,
        'birch': 0.53,
        'poplar': 0.35,
        'sweet chestnut': 0.44,
        'horse chestnut': 0.44,
        'alder': 0.42,
        'lime': 0.44,
        'elm': 0.43,
        'wych elm': 0.50,
        'wild cherry': 0.50,
        'hornbeam': 0.57
    }

    # Table 5.2.2: Coefficients for Equation 6 (Crown Biomass for trees with DBH between 7 cm and 50 cm)
    crown_biomass_coefficients_7_to_50 = {
        'European larch': (0.0000438717, 2.0291),
        'Corsican pine': (0.0000122645, 2.4767),
        'lodgepole pine': (0.0000176287, 2.4767),
        'Scots pine': (0.0000161411, 2.4767),
        'firs, spruces, cedars, hemlocks': (0.0000144620, 2.4767),
        'Douglas fir': (0.0000168602, 2.4767),
        'Beech': (0.0000188154, 2.4767),
        'oak': (0.0000168513, 2.4767)
    }

    # Table 5.2.3: Coefficients for Crown Biomass for trees with DBH greater than 50 cm)
    crown_biomass_coefficients_above_50 = {
        'European larch': (-0.129046967, 0.005039011),
        'Corsican pine': (-0.299529453, 0.009948982),
        'lodgepole pine': (-0.430536496, 0.014300429),
        'Scots pine': (-0.394205622, 0.013093685),
        'firs, spruces, cedars, hemlocks': (-0.353197843, 0.011731597),
        'Douglas fir': (-0.411767824, 0.013677021),
        'Beech': (-0.459518648, 0.015263082),
        'oak': (-0.411550464, 0.013669801)
    }

    
     # Table 5.2.4: Coefficients for Equation 8 (Root Biomass for trees up to and including 30 cm DBH)
    root_biomass_coefficients_8 = {
        'western red cedar': 0.000010722,
        'noble fir': 0.000010722,
        'Corsican pine': 0.000010722,
        'Norway spruce': 0.000011883,
        'grand fir': 0.000015404,
        'Scots pine': 0.000015404,
        'western hemlock': 0.000015404,
        'Douglas fir': 0.000017326,
        'European larch': 0.000017326,
        'lodgepole pine': 0.000017326,
        'Sitka spruce': 0.000020454,
        'red alder': 0.000022700
    }

    # Table 5.2.5: Coefficients for Equation 9 (Root Biomass for trees greater than 30 cm DBH)
    root_biomass_coefficients_9 = {
        'western red cedar': (-0.082602857, 0.004515233),
        'noble fir': (-0.082602857, 0.004515233),
        'Corsican pine': (-0.082602857, 0.004515233),
        'Norway spruce': (-0.091547262, 0.005004152),
        'grand fir': (-0.118673233, 0.006486910),
        'Scots pine': (-0.118673233, 0.006486910),
        'western hemlock': (-0.118673233, 0.006486910),
        'Douglas fir': (-0.133480423, 0.007296300),
        'European larch': (-0.133480423, 0.007296300),
        'lodgepole pine': (-0.133480423, 0.007296300),
        'Sitka spruce': (-0.157578701, 0.008613559),
        'red alder': (-0.174882004, 0.009559391)
    }
    
    
    # Determine the nominal specific gravity for the species
    nsg = nominal_specific_gravity.get(species, 0.0)  # Default to 0.0 if species not found

    # Calculate the per-tree Stem Biomass
    stem_biomass = volume_stats['total_stem_volume'] * nsg  # in oven-dry tonnes per tree
    
    # Determine whether to use Equation 6 or Equation 7 based on DBH
    mean_dbh_trees = tree_stats['mean_dbh_trees']
    if 7 <= mean_dbh_trees  <= 50:
        b, p = crown_biomass_coefficients_7_to_50.get(species, (0, 0))  # Default to 0, 0 if species not found
        crown_biomass = b * (mean_dbh_trees ** p)  # Equation 6
    elif mean_dbh_trees  > 50:
        a, b = crown_biomass_coefficients_above_50.get(species, (0, 0))  # Default to 0, 0 if species not found
        crown_biomass = a + (b * mean_dbh_trees)  # Equation 7
    else:
        crown_biomass = 0  # Default to 0 if DBH is out of expected range

        
    # Calculate Root Biomass
    if mean_dbh_trees <= 30:
        b = root_biomass_coefficients_8.get(species, 0)  # Default to 0 if species not found
        root_biomass = b * (mean_dbh_trees ** 2.5)  # Equation 8
    else:
        a, b = root_biomass_coefficients_9.get(species, (0, 0))  # Default to 0, 0 if species not found
        root_biomass = a + (b * mean_dbh_trees)  # Equation 9
    
    
    # Total number of trees for this species
    num_trees = tree_stats['species_distribution'][species]['trees']

    # Multiply per-tree biomass by the number of trees to get the total biomass
    total_stem_biomass = stem_biomass  # in oven-dry tonnes for all trees
    total_crown_biomass = crown_biomass * num_trees  # in oven-dry
    total_root_biomass = root_biomass * num_trees  # in oven-dry tonnes for all trees
    total_AGB = total_stem_biomass + total_crown_biomass  # in oven-dry tonnes for all trees
    
    # Calculate the total biomass (including root biomass)
    total_biomass = total_AGB + total_root_biomass  # Total biomass in oven-dry tonnes

    # Return the calculated biomass values
    return {
        'total_stem_biomass': total_stem_biomass,
        'total_crown_biomass': total_crown_biomass,
        'total_root_biomass': total_root_biomass,
        'total_AGB': total_AGB,
        'total_biomass': total_biomass
    }


def calculate_carbon_and_co2_for_trees_and_saplings(biomass_stats, species, num_saplings, mean_sapling_height):
    """
    Calculate the total carbon and CO2 content from the biomass values for both trees and saplings.

    Parameters:
        biomass_stats (dict): A dictionary containing the total biomass for each species.
        species (str): The species of the sapling.
        num_saplings (int): The total number of saplings for the species.
        mean_sapling_height (float): The mean height of saplings for the species.

    Returns:
        dict: A dictionary containing the total carbon and CO2 content for trees and saplings.
    """

    # Check if the species is broadleaf or conifer
    broadleaves = {'red alder', 'beech', 'oak'}
    conifers = {'western red cedar', 'noble fir', 'corsican pine', 'norway spruce', 'grand fir', 
                'scots pine', 'western hemlock', 'douglas fir', 'japanese larch', 'lodgepole pine', 
                'sitka spruce', 'european larch'}
    
    
    # Determine if species is broadleaf or conifer
    if species.lower() in broadleaves:
        is_broadleaf = True
    elif species.lower() in conifers:
        is_broadleaf = False
    else:
        raise ValueError(f"Species '{species}' not found in either broadleaf or conifer categories.")

    # Calculate total carbon content for trees
    total_carbon_trees = biomass_stats['total_biomass'] * 0.5  # in tonnes C

    # Convert total carbon for trees to CO2 content
    total_co2_trees = total_carbon_trees * (44 / 12)  # in tonnes CO2
    
        # Determine the mean carbon content per sapling
    if is_broadleaf:
        # Use Table 6.1.3 for broadleaved saplings
        broadleaf_carbon_content_per_stem = {
            0.6: 0.0000182, 0.7: 0.0000250, 0.8: 0.0000328, 0.9: 0.0000418,
            1.0: 0.0000519, 1.1: 0.0000631, 1.2: 0.0000754, 1.3: 0.0000889,
            1.4: 0.0001036, 1.5: 0.0001194, 1.6: 0.0001365, 1.7: 0.0001547,
            1.8: 0.0001742, 1.9: 0.0001949, 2.0: 0.0002168, 2.1: 0.0002400,
            2.2: 0.0002645, 2.3: 0.0002903, 2.4: 0.0003174, 2.5: 0.0003459,
            2.6: 0.0003757, 2.7: 0.0004069, 2.8: 0.0004395, 2.9: 0.0004736,
            3.0: 0.0005090, 3.1: 0.0005460, 3.2: 0.0005845, 3.3: 0.0006245,
            3.4: 0.0006661, 3.5: 0.0007093, 3.6: 0.0007541, 3.7: 0.0008006,
            3.8: 0.0008488, 3.9: 0.0008987, 4.0: 0.0009504, 4.1: 0.0010039,
            4.2: 0.0010593, 4.3: 0.0011166, 4.4: 0.0011759, 4.5: 0.0012372,
            4.6: 0.0013005, 4.7: 0.0013660, 4.8: 0.0014336, 4.9: 0.0015034,
            5.0: 0.0015756, 5.1: 0.0016501, 5.2: 0.0017270, 5.3: 0.0018065,
            5.4: 0.0018885, 5.5: 0.0019732, 5.6: 0.0020606, 5.7: 0.0021509,
            5.8: 0.0022440, 5.9: 0.0023402, 6.0: 0.0024396, 6.1: 0.0025421,
            6.2: 0.0026480, 6.3: 0.0027574, 6.4: 0.0028703, 6.5: 0.0029870,
            6.6: 0.0031076, 6.7: 0.0032321, 6.8: 0.0033608, 6.9: 0.0034939,
            7.0: 0.0036315, 7.1: 0.0037737, 7.2: 0.0039209, 7.3: 0.0040731,
            7.4: 0.0042307, 7.5: 0.0043939, 7.6: 0.0045628, 7.7: 0.0047378,
            7.8: 0.0049192, 7.9: 0.0051072, 8.0: 0.0053023, 8.1: 0.0055046,
            8.2: 0.0057147, 8.3: 0.0059328, 8.4: 0.0061594, 8.5: 0.0063951,
            8.6: 0.0066401, 8.7: 0.0068952, 8.8: 0.0071608, 8.9: 0.0074375,
            9.0: 0.0077260, 9.1: 0.0080271, 9.2: 0.0083414, 9.3: 0.0086699,
            9.4: 0.0090134, 9.5: 0.0093730, 9.6: 0.0097496, 9.7: 0.0101445,
            9.8: 0.0105590, 9.9: 0.0109945, 10.0: 0.0114525
        }
        sapling_carbon_content = broadleaf_carbon_content_per_stem.get(round(mean_sapling_height, 1), 0)
    else:
        # Use Table 6.1.4 for conifer saplings
        conifer_carbon_content_per_stem = {
            0.6: 0.0000222, 0.7: 0.0000304, 0.8: 0.0000400, 0.9: 0.0000509,
            1.0: 0.0000631, 1.1: 0.0000767, 1.2: 0.0000916, 1.3: 0.0001080,
            1.4: 0.0001257, 1.5: 0.0001449, 1.6: 0.0001655, 1.7: 0.0001876,
            1.8: 0.0002111, 1.9: 0.0002361, 2.0: 0.0002626, 2.1: 0.0002906,
            2.2: 0.0003202, 2.3: 0.0003513, 2.4: 0.0003840, 2.5: 0.0004184,
            2.6: 0.0004543, 2.7: 0.0004920, 2.8: 0.0005313, 2.9: 0.0005724,
            3.0: 0.0006152, 3.1: 0.0006598, 3.2: 0.0007062, 3.3: 0.0007545,
            3.4: 0.0008046, 3.5: 0.0008567, 3.6: 0.0009108, 3.7: 0.0009669,
            3.8: 0.0010250, 3.9: 0.0010853, 4.0: 0.0011477, 4.1: 0.0012123,
            4.2: 0.0012792, 4.3: 0.0013484, 4.4: 0.0014200, 4.5: 0.0014940,
            4.6: 0.0015705, 4.7: 0.0016496, 4.8: 0.0017314, 4.9: 0.0018158,
            5.0: 0.0019031, 5.1: 0.0019932, 5.2: 0.0020863, 5.3: 0.0021825,
            5.4: 0.0022819, 5.5: 0.0023845, 5.6: 0.0024904, 5.7: 0.0025998,
            5.8: 0.0027128, 5.9: 0.0028296, 6.0: 0.0029502, 6.1: 0.0030747,
            6.2: 0.0032034, 6.3: 0.0033363, 6.4: 0.0034737, 6.5: 0.0036157,
            6.6: 0.0037625, 6.7: 0.0039143, 6.8: 0.0040712, 6.9: 0.0042336,
            7.0: 0.0044015, 7.1: 0.0045753, 7.2: 0.0047552, 7.3: 0.0049415,
            7.4: 0.0051344, 7.5: 0.0053343, 7.6: 0.0055415, 7.7: 0.0057564,
            7.8: 0.0059792, 7.9: 0.0062105, 8.0: 0.0064505, 8.1: 0.0066999,
            8.2: 0.0069589, 8.3: 0.0072283, 8.4: 0.0075085, 8.5: 0.0078002,
            8.6: 0.0081039, 8.7: 0.0084204, 8.8: 0.0087504, 8.9: 0.0090948,
            9.0: 0.0094544, 9.1: 0.0098301, 9.2: 0.0102231, 9.3: 0.0106345,
            9.4: 0.0110655, 9.5: 0.0115174, 9.6: 0.0119917, 9.7: 0.0124900,
            9.8: 0.0130142, 9.9: 0.0135662, 10.0: 0.0141482
        }
        sapling_carbon_content = conifer_carbon_content_per_stem.get(round(mean_sapling_height), 0)
    
    # Calculate total carbon content for saplings
    total_carbon_saplings = sapling_carbon_content * num_saplings  # in tonnes C

    # Convert total carbon for saplings to CO2 content (tonnes CO2/species)
    total_co2_saplings = total_carbon_saplings * (44 / 12)  # in tonnes CO2

    # Sum up total carbon and CO2 content for trees and saplings
    total_carbon = total_carbon_trees + total_carbon_saplings
    total_co2 = total_co2_trees + total_co2_saplings
    
    
    return {
        'total_carbon_trees': total_carbon_trees,
        'total_co2_trees': total_co2_trees,
        'total_carbon_saplings': total_carbon_saplings,
        'total_co2_saplings': total_co2_saplings,
        'total_carbon': total_carbon,
        'total_co2': total_co2
    }



def print_tree_statistics(tree_stats):
    """
    Prints the tree statistics from the provided dictionary.

    Parameters:
    tree_stats (dict): A dictionary containing tree statistics.
    """
    
    # Print the calculated statistics
    print("Tree Statistics:")
    print(f"Total number of trees: {tree_stats['number_of_trees']}")
    print(f"Total number of saplings: {tree_stats['number_of_saplings']}")
    print(f"Total number of large trees: {tree_stats['number_of_largetrees']}")
    print(f"Mean Tree Height for Trees: {tree_stats['mean_tree_height']:.2f} meters")
    print(f"Mean DBH for Trees: {tree_stats['mean_dbh_trees']:.2f} cm")
    print(f"Mean Tree Height for Saplings: {tree_stats['mean_sapling_height']:.2f} meters")
    print(f"Mean DBH for Saplings: {tree_stats['mean_dbh_saplings']:.2f} cm")
    
    if tree_stats['mean_largetree_height'] is not None:
        print(f"Mean Tree Height for Large Trees: {tree_stats['mean_largetree_height']:.2f} meters")
        print(f"Mean DBH for Large Trees: {tree_stats['mean_dbh_largetrees']:.2f} cm")
    else:
        print("No large trees identified.")
    
    print(f"Quadratic Mean DBH for Trees: {tree_stats['quadratic_mean_dbh']:.1f} cm")
    print(f"Mean Basal Area for Trees: {tree_stats['mean_basal_area']:.4f} m^2\n")

# Example usage:
# print_tree_statistics(tree_stats)

def calculate_and_print_species_biomass_and_carbon(tree_stats, species_percentages):
    """
    Calculates and prints biomass, carbon, and CO2 content for each species, and updates total aggregates.

    Parameters:
    tree_stats (dict): A dictionary containing tree statistics, including species distribution and mean sapling height.
    species_percentages (dict): A dictionary containing the species percentages in the forest.

    Returns:
    dict: A dictionary containing total biomass, carbon, and CO2 aggregates for all species.
    """
    
    total_biomass_all_species = 0.0
    total_carbon_all_species = 0.0
    total_co2_all_species = 0.0
    total_co2_trees_all_species = 0.0
    total_co2_saplings_all_species = 0.0
    
    for species in species_percentages.keys():
        # Get the number of trees and saplings for the species
        num_trees = tree_stats['species_distribution'][species]['trees']
        num_saplings = tree_stats['species_distribution'][species]['saplings']

        # Calculate volume, biomass, and carbon/CO2 stats
        volume_stats = calculate_tariff_numbers_and_volume(tree_stats, species)
        biomass_stats = calculate_biomass(tree_stats, species, volume_stats)
        carbon_co2_stats = calculate_carbon_and_co2_for_trees_and_saplings(
            biomass_stats, species, num_saplings, tree_stats['mean_sapling_height']
        )

        # Print the results for the species
        print(f"Species: {species.capitalize()}")
        print(f"Number of Trees: {num_trees}")
        print(f"Number of Saplings: {num_saplings}")
        print(f"Tariff Number: {volume_stats['tariff_number']}")
        print(f"Mean Tree Volume: {volume_stats['mean_tree_volume']:.4f} m^3")
        print(f"Total Stem Volume: {volume_stats['total_stem_volume']:.4f} m^3")
        print(f"Total Stem Biomass: {biomass_stats['total_stem_biomass']:.4f} oven-dry tonnes")
        print(f"Total Crown Biomass: {biomass_stats['total_crown_biomass']:.4f} oven-dry tonnes")
        print(f"Total Root Biomass: {biomass_stats['total_root_biomass']:.4f} oven-dry tonnes")
        print(f"Total Above-Ground Biomass (AGB): {biomass_stats['total_AGB']:.4f} oven-dry tonnes")
        print(f"Total Biomass: {biomass_stats['total_biomass']:.4f} oven-dry tonnes")
        print(f"Total Carbon Content: {carbon_co2_stats['total_carbon']:.4f} tonnes C")
        print(f"Total CO2 Content for Trees: {carbon_co2_stats['total_co2_trees']:.4f} tonnes CO2")
        print(f"Total CO2 Content for Saplings: {carbon_co2_stats['total_co2_saplings']:.4f} tonnes CO2")
        print("-" * 50, "\n")

        # Update total aggregates
        total_biomass_all_species += biomass_stats['total_biomass']
        total_carbon_all_species += carbon_co2_stats['total_carbon']
        total_co2_all_species += carbon_co2_stats['total_co2']
        total_co2_trees_all_species += carbon_co2_stats['total_co2_trees']
        total_co2_saplings_all_species += carbon_co2_stats['total_co2_saplings']

    return {
        'total_biomass_all_species': total_biomass_all_species,
        'total_carbon_all_species': total_carbon_all_species,
        'total_co2_all_species': total_co2_all_species,
        'total_co2_trees_all_species': total_co2_trees_all_species,
        'total_co2_saplings_all_species': total_co2_saplings_all_species
    }

# Example usage:
# species_percentages = {
#     'oak': 0.5,
#     'pine': 0.3,
#     'maple': 0.2
# }
# tree_stats = {
#     'species_distribution': {
#         'oak': {'trees': 100, 'saplings': 50},
#         'pine': {'trees': 80, 'saplings': 40},
#         'maple': {'trees': 60, 'saplings': 30}
#     },
#     'mean_sapling_height': 3.5
# }

# total_aggregates = calculate_and_print_species_biomass_and_carbon(tree_stats, species_percentages)

def print_overall_totals(total_biomass_all_species, total_carbon_all_species, total_co2_all_species, total_co2_trees_all_species, total_co2_saplings_all_species):
    """
    Prints the overall totals for biomass, carbon, and CO2 content.

    Parameters:
    total_biomass_all_species (float): Total biomass for all species in oven-dry tonnes.
    total_carbon_all_species (float): Total carbon content for all species in tonnes C.
    total_co2_all_species (float): Total CO2 content for all species in tonnes CO2.
    total_co2_trees_all_species (float): Total CO2 content for trees of all species in tonnes CO2.
    total_co2_saplings_all_species (float): Total CO2 content for saplings of all species in tonnes CO2.
    """
    
    print("Overall Totals:")
    print(f"Total Biomass for All Species: {total_biomass_all_species:.4f} oven-dry tonnes")
    print(f"Total Carbon Content for All Species: {total_carbon_all_species:.4f} tonnes C")
    print(f"Total CO2 Content for All Species: {total_co2_all_species:.4f} tonnes CO2")
    print(f"Total CO2 Content for Trees (All Species): {total_co2_trees_all_species:.4f} tonnes CO2")
    print(f"Total CO2 Content for Saplings (All Species): {total_co2_saplings_all_species:.4f} tonnes CO2")

# Example usage:
# print_overall_totals(total_biomass_all_species, total_carbon_all_species, total_co2_all_species, total_co2_trees_all_species, total_co2_saplings_all_species)