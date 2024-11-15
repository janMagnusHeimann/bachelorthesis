import pandas as pd
import numpy as np
from rocket_optimizer.DynamicDatabase import AstosOutput


def max_flux_calc(position_1, position_2):
    start_position = min(position_1, position_2)
    end_position = max(position_1, position_2)
    # Use a raw string for the file path
    file_path = r".\.loadCaseData\Output_Report.xlsx"
    xls = pd.ExcelFile(file_path)

    # Load the sheet
    data_axial = pd.read_excel(xls, 'Axial_Load_Data')
    data_bending = pd.read_excel(xls, 'Bending_Mom_Data')

    # Clean the data by skipping the initial metadata rows and resetting the index
    cleaned_data_axial = data_axial.iloc[3:].reset_index(drop=True)
    cleaned_data_bending = data_bending.iloc[3:].reset_index(drop=True)

    # Rename columns for easier access
    cleaned_data_axial.columns = ['Distance [m]', 'Axial Load [kN]', 'Unnamed: 2', 'Unnamed: 3']
    cleaned_data_bending.columns = ['Distance [m]', 'Bending Moment [kN-m]', 'Unnamed: 2', 'Unnamed: 3']

    # Convert relevant columns to numeric
    cleaned_data_axial['Distance [m]'] = pd.to_numeric(cleaned_data_axial['Distance [m]'], errors='coerce')
    cleaned_data_bending['Distance [m]'] = pd.to_numeric(cleaned_data_bending['Distance [m]'], errors='coerce')
    cleaned_data_axial['Axial Load [kN]'] = pd.to_numeric(cleaned_data_axial['Axial Load [kN]'], errors='coerce')
    cleaned_data_bending['Bending Moment [kN-m]'] = pd.to_numeric(cleaned_data_bending['Bending Moment [kN-m]'], errors='coerce')

    # Ensure both sheets have data for the same distances (if not, you could interpolate or handle differently)
    merged_data = pd.merge(cleaned_data_axial[['Distance [m]', 'Axial Load [kN]']],
                           cleaned_data_bending[['Distance [m]', 'Bending Moment [kN-m]']],
                           on='Distance [m]', suffixes=(None, None))

    # Drop rows with NaN values
    merged_data = merged_data.dropna(subset=['Distance [m]', 'Axial Load [kN]', 'Bending Moment [kN-m]'])

    # Filter data between position_1 and position_2
    filtered_data = merged_data[(merged_data['Distance [m]'] >= start_position) &
                                (merged_data['Distance [m]'] <= end_position)].copy()

    radius = AstosOutput.rocket_diameter / 2

    filtered_data['Flux'] = 1000.0 * (
                filtered_data['Axial Load [kN]'].abs() + (filtered_data['Bending Moment [kN-m]'].abs() / radius)) * \
                            filtered_data['Axial Load [kN]'].apply(lambda x: 1 if x < 0 else -1) / (
                                        2.0 * np.pi * (1000.0 * radius))

    # TODO: still not exactly right, if axial load is positive but very small we might still want to consider the
    #  compression component of bending and not the traction component, depending on how small it is (don't know if doable and how)
    # maybe use the ratio between critical traction load and Euler's buckling load?

    # Find the row with the maximum value in the specified column within the interval
    if not filtered_data.empty:
        max_abs_idx = filtered_data['Flux'].abs().idxmax()
        max_value = filtered_data.loc[max_abs_idx, 'Flux']
    else:
        return None  # If no data is found in the interval, return None

    return max_value
