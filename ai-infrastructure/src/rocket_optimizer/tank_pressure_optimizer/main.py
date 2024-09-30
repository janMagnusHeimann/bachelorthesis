import warnings

import pandas as pd
import numpy as np
from rocket_optimizer.loadCaseGenerator import loadCaseGenerator
from rocket_optimizer.DynamicDatabase import Results, DatabaseOutput, AstosOutput

pd.set_option('display.max_rows', None)


# Function to find the minimum value in the Margin_of_Safety column for a given range of Distance
def find_min_margin_of_safety(data, lower_bound, upper_bound):
    filtered_data = data[(data['Distance'] > lower_bound) & (data['Distance'] < upper_bound)]

    valid_data = filtered_data[
        (filtered_data['Margin_of_Safety'] != 0) &
        (~np.isinf(filtered_data['Margin_of_Safety'])) &
        (~filtered_data['Margin_of_Safety'].isna())
    ]

    # Calculate the minimum absolute value
    min_value = abs(valid_data['Margin_of_Safety']).min()

    return min_value


def loadFactorFromOutput():
    # tank measueres
    lower_bound_s1 = AstosOutput.d_n_stage1_bottom_tank_head
    upper_bound_s1 = AstosOutput.d_n_stage1_top_tank_head
    lower_bound_s2 = AstosOutput.d_n_stage2_bottom_tank_head
    upper_bound_s2 = AstosOutput.d_n_stage2_top_tank_head

    # Load the Excel file
    file_path = "./.loadCaseData/Output_Report.xlsx"

    # Load the data with correct header row and skip irrelevant rows
    data = pd.read_excel(file_path, sheet_name='Margin_of_Safety_Data', header=3)

    # Rename columns for clarity
    data.columns = ['Distance', 'Margin_of_Safety', 'Unnamed_2', 'Unnamed_3']

    # Calculate the minimum values for the specified ranges
    stage1 = find_min_margin_of_safety(data, lower_bound_s1, upper_bound_s1)
    stage2 = find_min_margin_of_safety(data, lower_bound_s2, upper_bound_s2)

    # print(f"Stage 1 load factor: {stage1}")
    # print(f"Stage 2 load factor: {stage2}")
    return stage1, stage2


def tankPressureFromOutput():
    file_path = "./.loadCaseData/input_template.xlsx"

    # Load the 'General' sheet into a DataFrame
    general_df = pd.read_excel(file_path, sheet_name='General')

    # Locate the rows for 'Stage 1 Tank Pressure' and 'Stage 2 Tank Pressure'
    stage_1_row = general_df[general_df['Parameter'].str.contains('Stage 1 tank pressure', na=False)].index
    stage_2_row = general_df[general_df['Parameter'].str.contains('Stage 2 tank pressure', na=False)].index

    # Get the values
    stage_1_pressure = general_df.loc[stage_1_row, 'Value'].values[0] if not stage_1_row.empty else None
    stage_2_pressure = general_df.loc[stage_2_row, 'Value'].values[0] if not stage_2_row.empty else None

    return stage_1_pressure, stage_2_pressure


def loadCaseEditInput(p_s1, p_s2):

    file_path = "./.loadCaseData/input_template.xlsx"
    # Load the Excel file
    # excel_data = pd.ExcelFile(file_path)

    # Load the 'General' sheet into a DataFrame
    general_df = pd.read_excel(file_path, sheet_name='General')

    # Locate the rows for 'Stage 1 Tank Pressure' and 'Stage 2 Tank Pressure'
    stage_1_row = general_df[general_df['Parameter'].str.contains('Stage 1 tank pressure', na=False)].index
    stage_2_row = general_df[general_df['Parameter'].str.contains('Stage 2 tank pressure', na=False)].index

    # Debugging: Print the rows and the DataFrame before modification

    # Update the values
    general_df.loc[stage_1_row, 'Value'] = p_s1
    general_df.loc[stage_2_row, 'Value'] = p_s2

    # Save the updated DataFrame back to the 'General' sheet in the Excel file
    with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        general_df.to_excel(writer, sheet_name='General', index=False)


def calculate_load_factor_difference(p_s1, p_s2, tar_lf):
    loadCaseEditInput(p_s1, p_s2)
    loadCaseGenerator(AstosOutput.rocket_diameter)
    loadFactor_s1, loadFactor_s2 = loadFactorFromOutput()
    delta_S1 = abs(loadFactor_s1) - abs(tar_lf)
    delta_S2 = abs(loadFactor_s2) - abs(tar_lf)
    return delta_S1, delta_S2


# def tank_pressure_optimizer(p_s1_lower, p_s1_upper, p_s2_lower, p_s2_upper, tar_lf, max_iter, tol):
#     """
#     Hybrid Bisection-Newton method to find internal pressures of rocket tanks.
#
#     Parameters:
#     p_s1_lower : float
#         Lower bound of internal pressure of stage 1.
#     p_s1_upper : float
#         Upper bound of internal pressure of stage 1.
#     p_s2_lower : float
#         Lower bound of internal pressure of stage 2.
#     p_s2_upper : float
#         Upper bound of internal pressure of stage 2.
#     tar_lf : float
#         Target loadfactor (empirically determined 1.2).
#     tol : float
#         Tolerance for stopping the algorithm.
#     max_iter : int
#         Maximum number of iterations.
#
#     Returns:
#     p_s1 : float
#         Internal pressure of stage 1.
#     p_s2 : float
#         Internal pressure of stage 2.
#     """
#
#     def newton_raphson_step(p_s, delta_s, derivative):
#         if derivative == 0:
#             return p_s  # Avoid division by zero
#         new_p_s = p_s - (delta_s / derivative)
#         return new_p_s
#
#     def numerical_derivative(p_s1, p_s2, delta=1e-6):
#         delta_S1, delta_S2 = calculate_load_factor_difference(p_s1, p_s2)
#         delta_S1_delta, _ = calculate_load_factor_difference(p_s1 + delta, p_s2)
#         _, delta_S2_delta = calculate_load_factor_difference(p_s1, p_s2 + delta)
#
#         derivative_S1 = (delta_S1_delta - delta_S1) / delta
#         derivative_S2 = (delta_S2_delta - delta_S2) / delta
#
#         return derivative_S1, derivative_S2
#
#     for i in range(max_iter):
#         p_s1_mid = (p_s1_lower + p_s1_upper) / 2.0
#         p_s2_mid = (p_s2_lower + p_s2_upper) / 2.0
#
#         delta_S1, delta_S2 = calculate_load_factor_difference(p_s1_mid, p_s2_mid, tar_lf)
#
#         if abs(delta_S1) < tol and abs(delta_S2) < tol:
#             # TODO: check if atmospheric pressure plays a role or if s1 and s2 startup pressures are different
#             if p_s1_mid < DatabaseOutput.s1_engine_startup_pressure:
#                 p_s1_mid = DatabaseOutput.s1_engine_startup_pressure
#             if p_s2_mid < DatabaseOutput.s2_engine_startup_pressure:
#                 p_s2_mid = DatabaseOutput.s2_engine_startup_pressure
#             loadCaseEditInput(p_s1_mid, p_s2_mid)
#             loadCaseGenerator(AstosOutput.rocket_diameter)
#             loadFactor_s1, loadFactor_s2 = loadFactorFromOutput()
#             if loadFactor_s1 < 1.2 or loadFactor_s2 < 1.2:
#                 warnings.warn("Conflict between minimum safety factor and minimum tank pressure, continuing with "
#                               "minimum tank pressure and lower than minimum safety factor. Check the safety factor "
#                               "after the Odin run.")
#             print(f"Solution found after {i+1} iterations: p_s1 = {p_s1_mid}, p_s2 = {p_s2_mid}")
#             print(f"Final safety factors: {loadFactor_s1}, {loadFactor_s2}")
#             Results.append_value('p1', p_s1_mid)
#             Results.append_value('p2', p_s2_mid)
#
#             # TODO add ullage pressure
#             return p_s1_mid, p_s2_mid
#
#         if i >= max_iter / 2:  # Switch to Newton-Raphson for faster convergence
#             derivative_S1, derivative_S2 = numerical_derivative(p_s1_mid, p_s2_mid)
#             p_s1_mid = newton_raphson_step(p_s1_mid, delta_S1, derivative_S1)
#             p_s2_mid = newton_raphson_step(p_s2_mid, delta_S2, derivative_S2)
#
#             # Constrain pressures within bounds
#             p_s1_mid = max(min(p_s1_mid, p_s1_upper), p_s1_lower)
#             p_s2_mid = max(min(p_s2_mid, p_s2_upper), p_s2_lower)
#
#         if i < max_iter / 2:  # Bisection method
#             if delta_S1 > 0:
#                 p_s1_upper = p_s1_mid
#             else:
#                 p_s1_lower = p_s1_mid
#
#             if delta_S2 > 0:
#                 p_s2_upper = p_s2_mid
#             else:
#                 p_s2_lower = p_s2_mid
#
#     # TODO: check if atmospheric pressure plays a role or if s1 and s2 startup pressures are different
#
#     if p_s1_mid < DatabaseOutput.s1_engine_startup_pressure:
#         p_s1_mid = DatabaseOutput.s1_engine_startup_pressure
#     if p_s2_mid < DatabaseOutput.s2_engine_startup_pressure:
#         p_s2_mid = DatabaseOutput.s2_engine_startup_pressure
#     loadCaseEditInput(p_s1_mid, p_s2_mid)
#     loadCaseGenerator(AstosOutput.rocket_diameter)
#     loadFactor_s1, loadFactor_s2 = loadFactorFromOutput()
#     if loadFactor_s1 < 1.2 or loadFactor_s2 < 1.2:
#         warnings.warn("Conflict between minimum safety factor and minimum tank pressure, continuing with "
#                       "minimum tank pressure and lower than minimum safety factor. Check the safety factor "
#                       "after the Odin run.")
#     print(f"Maximum number of iterations reached. Last pressures: p_s1 = {p_s1_mid}, p_s2 = {p_s2_mid}")
#     print(f"Last safety factors: {loadFactor_s1}, {loadFactor_s2}")
#     Results.append_value('p1', p_s1_mid)
#     Results.append_value('p2', p_s2_mid)
#     return p_s1_mid, p_s2_mid


def tank_pressure_optimizer(p_s1_lower, p_s1_upper, p_s2_lower, p_s2_upper, tar_lf, max_iter, tol):
    p1_list = np.linspace(p_s1_lower, p_s1_upper, 30)
    p2_list = np.linspace(p_s2_lower, p_s2_upper, 30)

    fos_1 = np.empty((30, 30))
    fos_2 = np.empty((30, 30))

    for i, p1 in enumerate(p1_list):
        for j, p2 in enumerate(p2_list):
            fos_1[i, j], fos_2[i, j] = calculate_load_factor_difference(p1, p2, 0)

    import matplotlib.pyplot as plt


    pass


# Example usage:
if __name__ == "__main__":
    # Adjust these bounds based on the expected range of pressures
    p_s1_lower = -7.0
    p_s1_upper = 7.0
    p_s2_lower = -7.0
    p_s2_upper = 7.0
    tar_lf = 1.2  # empirically determined

    try:
        p_s1, p_s2 = tank_pressure_optimizer(p_s1_lower, p_s1_upper, p_s2_lower, p_s2_upper, tar_lf, 10, 0.01)
        print(f"Optimized pressures: p_s1 = {p_s1}, p_s2 = {p_s2}")
    except ValueError as e:
        print(e)
