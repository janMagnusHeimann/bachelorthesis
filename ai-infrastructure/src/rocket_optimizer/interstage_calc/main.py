import pandas as pd
import numpy as np
from rocket_optimizer.DynamicDatabase import AstosOutput


def interstage_calc():
    # Use a raw string for the file path
    file_path = r".\.loadCaseData\Output_Report.xlsx"
    xls = pd.ExcelFile(file_path)

    # Function to process a specific sheet and find the closest value to a given distance
    def find_closest_value(sheet_name, value_column, distance_value):
        # Load the sheet
        data = pd.read_excel(xls, sheet_name)

        # Clean the data by skipping the initial metadata rows and resetting the index
        cleaned_data = data.iloc[3:].reset_index(drop=True)

        # Rename columns for easier access
        cleaned_data.columns = ['Distance [m]', value_column, 'Unnamed: 2', 'Unnamed: 3']

        # Convert relevant columns to numeric
        cleaned_data['Distance [m]'] = pd.to_numeric(cleaned_data['Distance [m]'], errors='coerce')
        cleaned_data[value_column] = pd.to_numeric(cleaned_data[value_column], errors='coerce')

        # Drop rows with NaN values in 'Distance [m]'
        cleaned_data = cleaned_data.dropna(subset=['Distance [m]'])

        # Find the closest distance to the specified value
        closest_distance_index = (cleaned_data['Distance [m]'] - distance_value).abs().idxmin()
        closest_distance = cleaned_data.iloc[closest_distance_index]

        return closest_distance

    # Find the closest values for axial load and bending moment at distance 15 meters
    axial_load_closest = find_closest_value('Axial_Load_Data', 'Axial Load [kN]', AstosOutput.d_n_stage1__stage2_interstage_bottom)
    bending_moment_closest = find_closest_value('Bending_Mom_Data', 'Bending Moment [kN-m]', AstosOutput.d_n_stage1__stage2_interstage_bottom)

    # Output the results
    a = axial_load_closest.iloc[1]
    print("Axial Load at closest distance to interstage1 bottom:", a)
    b = bending_moment_closest.iloc[1]
    print("\nBending Moment at closest distance to interstage1 bottom:", b)

    radius = AstosOutput.rocket_diameter / 2

    x = (((a+(b/radius))*1000.0) / (2.0 * (radius * 1000.0) * np.pi)
         ) / (AstosOutput.thrust*1000.0)

    print(x)
    AstosOutput.interstage1_flux = x*1e8

    # Find the closest values for axial load and bending moment at distance 15 meters
    axial_load_closest = find_closest_value('Axial_Load_Data', 'Axial Load [kN]', AstosOutput.d_n_stage2__fairing_interstage_flange)
    bending_moment_closest = find_closest_value('Bending_Mom_Data', 'Bending Moment [kN-m]', AstosOutput.d_n_stage2__fairing_interstage_flange)

    # Output the results
    a = axial_load_closest.iloc[1]
    print("Axial Load at closest distance to interstage2 bottom:", a)
    b = bending_moment_closest.iloc[1]
    print("\nBending Moment at closest distance to interstage2 bottom:", b)

    radius = AstosOutput.rocket_diameter / 2

    x = (((a+(b/radius))*1000.0) / (2.0 * (radius * 1000.0) * np.pi)
         ) / (AstosOutput.thrust*1000.0)

    print(x)  # 1e7 is the conversion factor to make the reult actually have influence on the optimization
    AstosOutput.interstage2_flux = x*1e8
