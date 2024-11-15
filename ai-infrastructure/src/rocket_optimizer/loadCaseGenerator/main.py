import math
import warnings
from pathlib import Path
from tkinter import Tk

import numpy as np
import pandas as pd
import xlsxwriter


def loadCaseGenerator(s1_tank_diameter):
    loadCaseCalculator()  # bendingMoment = extract_bending_Moment()  # p_int_m = (bendingMoment.at[6, "Bending Moment Data"] * 1000) / (2 * math.pi * s1TankRadius)

    # return p_int_m * 1e-6


def extract_bending_Moment():
    # Specify your local file path
    file_path = "./.loadCaseData/Output_Report.xlsx"
    sheet_name = "Stations"

    # Load the Excel file and the specific sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Create a new DataFrame with the bending moment data including accurate descriptions
    bending_moment_df = pd.DataFrame(
        {"Description": df["Unnamed: 2"],  # Replace 'Station Description' with the correct column name
         "Bending Moment Data": df["Unnamed: 11"],  # Bending Moment values
         })
    # Specify the output path on your local machine
    output_path = "./.loadCaseData/Bending_Moment_Data.xlsx"

    # Save the new DataFrame to an Excel file
    bending_moment_df.to_excel(output_path, index=False)

    print(f"Bending moment data saved to {output_path}")

    return bending_moment_df


def apply_safety_factors(sf_axial, sf_shear, sf_bm, axial_loads, shear_loads, bending_moments):
    axial_loads_sf = []
    shear_loads_sf = []
    bending_moments_sf = []
    for i in range(0, len(axial_loads)):
        x = axial_loads[i][0]
        y = sf_axial * axial_loads[i][1]
        axial_loads_sf.append([x, y])
    for i in range(0, len(shear_loads)):
        x = shear_loads[i][0]
        y = sf_shear * shear_loads[i][1]
        shear_loads_sf.append([x, y])
    for i in range(0, len(bending_moments)):
        x = bending_moments[i][0]
        y = sf_bm * bending_moments[i][1]
        bending_moments_sf.append([x, y])
    return axial_loads_sf, shear_loads_sf, bending_moments_sf


def calculate_axial_loads(axial_forces, L_tot):
    axial_loads = [[0.0, 0.0]]
    force_sum = 0.0

    for force in axial_forces:
        force_sum += force[1]
        axial_loads.append([force[0], force_sum])

    axial_loads.append([L_tot - 0.001, force_sum])
    axial_loads.append([L_tot, 0.0])

    return axial_loads


def calculate_bending_moments(shear_loads):
    bending_moments = [[0.0, 0.0]]
    prev_bm = 0
    for i in range(1, len(shear_loads)):
        dx = shear_loads[i][0] - shear_loads[i - 1][0]
        bm = prev_bm + shear_loads[i - 1][1] * dx
        bending_moments.append([shear_loads[i][0], bm])
        prev_bm = bm

    return bending_moments


def calculate_buckling_margin(F_axial, M_bending, r, t, v, p, E):
    # Moment of inertia
    Inertia = math.pi * t * r ** 3  # Intertia of a thin walled cylinder

    # Operating Stresses
    S_bm = M_bending * r / Inertia  # bending moments
    S_ax = F_axial / (2 * math.pi * r * t)  # axial forces

    # gamma calculation
    theta = 1 / 16 * math.sqrt(r / t)  # (NASA SP-8007, p.7 Eq. 10), for r/t < 1500
    gamma_bm = 1 - 0.731 * (1 - math.exp(-theta))  # bending moments (NASA SP-8007, p.7 Eq. 9)
    gamma_ax = 1 - 0.901 * (1 - math.exp(-theta))  # axial forces (NASA SP-8007, p.5 Eq. 5)

    # d_gamma calculation (NASA SP-8007, p.15, Fig. 6, buckling stress coefficient)
    par = p / E * (r / t) ** 2
    if par == 0:
        d_gamma = 0
    elif par > 10:
        warnings.warn("d_gamma X axis out of bounds. Please refer to NASA SP-8007, p.15, Fig. 6. Performing an extrapolation", Warning)
        d_gamma = 10 ** (0.01412 * math.log10(par) ** 3 - 0.17213 * math.log10(par) ** 2 + 0.20776 * math.log10(
            par) - 0.63008)
        # raise ValueError("d_gamma X axis out of bounds. Please refer to NASA SP-8007, p.15, Fig. 6")
    else:
        d_gamma = 10 ** (0.01412 * math.log10(par) ** 3 - 0.17213 * math.log10(par) ** 2 + 0.20776 * math.log10(
            par) - 0.63008)



    # Critical Bending stress with internal pressure (p.15)
    arg3 = math.pi * r * E * t ** 2 * (
            gamma_bm / math.sqrt(3 * (1 - v ** 2)) + d_gamma)  # (NASA SP-8007 2020rev2FINAl, p.33 Eq. 50)
    arg4 = 0.8 * p * math.pi * r ** 3
    M_press = arg3 + arg4
    S_bm_crit = M_press * r / Inertia  # critical bending stress as above
    R_bm = S_bm / S_bm_crit  # bending stress ratio

    # Critical axial stress with internal pressure
    if F_axial >= 0:  # axial load is positive for compression and negative for traction
        # critical buckling load (p.14)
        arg1 = 2 * math.pi * E * t ** 2 * (
                gamma_ax / math.sqrt(3 * (1 - v ** 2)) + d_gamma)  # (NASA SP-8007 2020rev2FINAl, p.32 Eq. 48)
        arg2 = p * math.pi * r ** 2
        P_press = arg1 + arg2
        S_ax_crit = P_press / (2 * math.pi * r * t)  # axial forces as above
        R_ax = S_ax / S_ax_crit  # axial stress ratio
    else:
        # Critical yield stress
        S_ax_crit = 870e+6  # value for half-hard 316L stainless steel, TODO: remove hardcoded value
        R_ax = -S_ax / S_ax_crit

    # Interaction equation
    # R = S_ax / S_ax_crit + S_bm / S_bm_crit # safety factor
    FS = 1 / (R_ax + R_bm)  # (NASA/TM—2019-220153 p.25 Eq. B3), (https://pure.tue.nl/ws/portalfiles/portal/108240893/Hamidi_0785449.pdf, p.31)

    # print('\n======Stress ratios check======')
    # print(f'axial stress ratio: {R_ax}')
    # print(f'bending stress ratio: {R_bm}\n')
    # print(f'axial load: {S_ax}')
    # print(f'bending load: {S_bm}\n')
    # print(f'axial critical load: {S_ax_crit}')
    # print(f'bending critical load: {S_bm_crit}\n')

    # Margin of safety
    # if FS < 1e-6:
    #    FS = 1e-6
    # MoS = FS - 1
    # return MoS
    return FS


def calculate_CoG(mass_table):
    nom = 0
    denom = 0

    for elem in mass_table:
        nom += elem[0] * elem[1]
        denom += elem[1]

    CoG = nom / denom
    return CoG, denom


def calculate_shear_loads(lateral_forces):
    shear_loads = [[0.0, 0.0]]
    prev_shear = 0.0

    for force in lateral_forces:
        shear = prev_shear + force[1]
        shear_loads.append([force[0], -shear])
        prev_shear = shear

    return shear_loads


def calculate_standard_atmosphere_conditions(h):
    h_std = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 15000, 20000, 25000, 30000, 40000, 50000,
             60000, 70000, 80000, ]

    # Standard temperature in deg C
    temp_std = [15.00, 8.50, 2.00, -4.49, -10.98, -17.47, -23.96, -30.45, -36.94, -43.42, -49.90, -56.50, -56.50,
                -51.60, -46.64, -22.80, -2.5, -26.13, -53.57, -74.51, ]

    # Standard pressure in 10kPa
    p_std = [10.130, 8.988, 7.950, 7.012, 6.166, 5.405, 4.722, 4.111, 3.565, 3.080, 2.650, 1.211, 0.5529, 0.2549,
             0.1197, 0.0287, 0.007978, 0.002196, 0.00052, 0.00011, ]

    # Standard density in kg/m3
    rho_std = [1.2250, 1.1120, 1.0070, 0.9093, 0.8194, 0.7364, 0.6601, 0.5900, 0.5258, 0.4671, 0.4135, 0.1948, 0.08891,
               0.04008, 0.01841, 0.003996, 0.001027, 0.0003097, 0.00008283, 0.00001846, ]

    if 0 <= h <= 80000:
        temp = np.interp(h, h_std, temp_std) + 273.15
        p = np.interp(h, h_std, p_std) * 1e4
        rho = np.interp(h, h_std, rho_std)
    elif h < 0:
        raise ValueError("Flight altitude below 0m")
    else:
        print(
            "WARNING: Altitude above the implemented standard atmosphere altitude " + "range (0 - 80,000m). Values at h=80,000 are assumed above this range.")
        temp = -74.51 + 273.15
        p = 0.00011 * 1e4
        rho = 0.00001846
    return temp, p, rho


def calculate_inertial_forces(mass_table, axial_accel, lateral_accel):
    forces = []

    for mass in mass_table:
        forces.append([mass[0], mass[1] * -axial_accel, mass[1] * -lateral_accel])
    return forces


def combine_core_and_booster_aero_forces(aero_forces_core, aero_forces_b, n_b):
    aero_forces_c_b = []

    for row in aero_forces_core:
        aero_forces_c_b.append([row[0], row[1]])
    for row in aero_forces_b:
        aero_forces_c_b.append([row[0], row[1] * n_b])
    aero_forces_c_b.sort(key=lambda x: x[0])
    return aero_forces_c_b


def combine_inert_and_propellant_masses(inert_table, propellant_table):
    mass_table = []

    for elem in inert_table:
        mass_table.append(elem)
    for elem in propellant_table:
        mass_table.append(elem)
    mass_table.sort(key=lambda x: x[0])
    return mass_table


def combine_inertial_and_aero_forces(GP, T_x, T_z, x_aft, I_aft_z, x_fwd, I_fwd_x, I_fwd_z, aero_forces, inertial_forces):
    axial_forces = [[GP, T_x], [x_fwd, I_fwd_x]]
    lateral_forces = [[GP, T_z], [x_aft, I_aft_z], [x_fwd, I_fwd_z]]
    for force in aero_forces:
        axial_forces.append([force[0], 0.0])
        lateral_forces.append([force[0], force[1]])
    for force in inertial_forces:
        axial_forces.append([force[0], force[1]])
        lateral_forces.append([force[0], force[2]])
    axial_forces.sort(key=lambda x: x[0])
    lateral_forces.sort(key=lambda x: x[0])

    return axial_forces, lateral_forces


def distribute_propellant_masses(no_of_sections, D, L_s1_blk_bot, L_s1_blk_mid, L_s1_blk_top, L_s2_blk_bot,
                                 L_s2_blk_mid, L_s2_blk_top, m_s1_bot, m_s1_top, m_s2_bot, m_s2_top, t_maxQ, t_S1burn):
    L_s1_bot = L_s1_blk_mid - L_s1_blk_bot
    L_s1_top = L_s1_blk_top - L_s1_blk_mid
    L_s2_bot = L_s2_blk_mid - L_s2_blk_bot
    L_s2_top = L_s2_blk_top - L_s2_blk_mid

    burn_factor = (t_S1burn - t_maxQ) / t_S1burn

    L_s1_bot_scaled = L_s1_bot * burn_factor
    L_s1_top_scaled = L_s1_top * burn_factor

    m_s1_bot_scaled = m_s1_bot * burn_factor
    m_s1_top_scaled = m_s1_top * burn_factor

    dL_s1_bot = L_s1_bot_scaled / no_of_sections
    dL_s1_top = L_s1_top_scaled / no_of_sections
    dL_s2_bot = L_s2_bot / no_of_sections
    dL_s2_top = L_s2_top / no_of_sections

    dm_s1_bot = m_s1_bot_scaled / no_of_sections
    dm_s1_top = m_s1_top_scaled / no_of_sections
    dm_s2_bot = m_s2_bot / no_of_sections
    dm_s2_top = m_s2_top / no_of_sections

    mass_table = []
    for i in range(0, no_of_sections):
        mass_table.append([L_s1_blk_bot + i * dL_s1_bot, dm_s1_bot])
    for i in range(0, no_of_sections):
        mass_table.append([L_s1_blk_mid + i * dL_s1_top, dm_s1_top])
    for i in range(0, no_of_sections):
        mass_table.append([L_s2_blk_bot + i * dL_s2_bot, dm_s2_bot])
    for i in range(0, no_of_sections):
        mass_table.append([L_s2_blk_mid + i * dL_s2_top, dm_s2_top])

    return mass_table


def excel_create_chart(sheet_name, chart_title, x_axis_name, y_axis_name, L, workbook, data):

    y_data = np.array(data)
    filtered_y_values = y_data[(y_data[:, 0] <= L), 1:]
    y_max = np.max(filtered_y_values)
    y_min = np.min(filtered_y_values)
    x_max = (int(L / 5) + 1) * 5
    y_max = (int(1.05*y_max / 5) + 1) * 5
    y_min = (int(1.05*y_min / 5) + 1) * 5

    chart = workbook.add_chart({"type": "scatter", "subtype": "straight"})

    chart.set_legend({"position": "bottom"})

    chart.add_series({"name": "Nominal", "categories": "=" + sheet_name + "!$A$5:$A$1004",
                      "values": "=" + sheet_name + "!$B$5:$B$1004", })

    chart.add_series({"name": "Best", "categories": "=" + sheet_name + "!$A$5:$A$1004",
                      "values": "=" + sheet_name + "!$AC$5:$AC$1004", })

    chart.add_series({"name": "Worst", "categories": "=" + sheet_name + "!$A$5:$A$1004",
                      "values": "=" + sheet_name + "!$AD$5:$AD$1004", })

    chart.set_title({"name": chart_title})

    chart.set_x_axis({"name": x_axis_name, "minor_gridlines": {"visible": True}, "num_format": "0", "max": x_max, })

    chart.set_y_axis({"name": y_axis_name, "minor_gridlines": {"visible": True}, "num_format": "0", "min": y_min, "max": y_max, })
    return chart


def excel_create_stations_sheet(worksheet, case, axial_loads, shear_loads, bending_moments, stations_table,
                                format_output_3dig, format_output_str, format_output_int):
    # Separate output vectors
    x = []
    y_al = []
    y_sl = []
    y_bm = []
    for row in axial_loads:
        x.append(row[0])
        y_al.append(row[1])

    for row in shear_loads:
        y_sl.append(row[1])

    for row in bending_moments:
        y_bm.append(row[1])

    for i, row in enumerate(stations_table):
        x_print = row[0]
        label = row[1]
        description = row[2]

        axial_station = None
        shear_station = None
        bend_station = None
        for j in range(0, len(x)):
            if x[j] > x_print:
                axial_station = 0.001 * max(y_al[j - 1], y_al[j])

                shear_station = 0.001 * y_sl[j] if abs(y_sl[j]) > abs(y_sl[j - 1]) else 0.001 * y_sl[j]
                bend_station = 0.001 * max(y_bm[j - 1], y_bm[j])
                break
        if axial_station is None:
            raise ValueError(f'Variable axial_station is empty at iteration {i}')
        if shear_station is None:
            raise ValueError(f'Variable shear_station is empty at iteration {i}')
        if bend_station is None:
            raise ValueError(f'Variable bend_station is empty at iteration {i}')

        if case == "Best":
            worksheet.write_number(2 + i, 0, float(x_print), format_output_3dig)
            worksheet.write_string(2 + i, 1, label, format_output_str)
            worksheet.write_string(2 + i, 2, description, format_output_str)
            if is_valid_number(axial_station, "axial_station"):
                worksheet.write_number(2 + i, 3, float(axial_station), format_output_int)
            if is_valid_number(shear_station, "shear_station"):
                worksheet.write_number(2 + i, 4, float(shear_station), format_output_int)
            if is_valid_number(bend_station, "bend_station"):
                worksheet.write_number(2 + i, 5, float(bend_station), format_output_int)
        elif case == "Nominal":
            if is_valid_number(axial_station, "axial_station"):
                worksheet.write_number(2 + i, 6, float(axial_station), format_output_int)
            if is_valid_number(shear_station, "shear_station"):
                worksheet.write_number(2 + i, 7, float(shear_station), format_output_int)
            if is_valid_number(bend_station, "bend_station"):
                worksheet.write_number(2 + i, 8, float(bend_station), format_output_int)
        elif case == "Worst":
            if is_valid_number(axial_station, "axial_station"):
                worksheet.write_number(2 + i, 9, float(axial_station), format_output_int)
            if is_valid_number(shear_station, "shear_station"):
                worksheet.write_number(2 + i, 10, float(shear_station), format_output_int)
            if is_valid_number(bend_station, "bend_station"):
                worksheet.write_number(2 + i, 11, float(bend_station), format_output_int)


def excel_export_data(workbook, i, alt, machNo, t_maxQ, axial_loads, shear_loads, bending_moments, margins_of_safety,
                      format_output_3dig):
    # Separate output vectors
    x = []
    y_al = []
    y_sl = []
    y_bm = []
    y_mos = []
    for row in axial_loads:
        x.append(row[0])
        y_al.append(row[1])

    for row in shear_loads:
        y_sl.append(row[1])

    for row in bending_moments:
        y_bm.append(row[1])

    for row in margins_of_safety:
        if row[1] < 10:
            y_mos.append(row[1])
        else:
            y_mos.append(10)

    wkst1 = workbook.get_worksheet_by_name("Axial_Load_Data")
    wkst2 = workbook.get_worksheet_by_name("Shear_Load_Data")
    wkst3 = workbook.get_worksheet_by_name("Bending_Mom_Data")
    wkst4 = workbook.get_worksheet_by_name("Margin_of_Safety_Data")
    if i == 0:
        for j, row in enumerate(x):
            wkst1.write_number(4 + j, 0, row, format_output_3dig)
            wkst2.write_number(4 + j, 0, row, format_output_3dig)
            wkst3.write_number(4 + j, 0, row, format_output_3dig)
            wkst4.write_number(4 + j, 0, row, format_output_3dig)
    format1 = workbook.add_format(
        {"bg_color": "#2F75B5", "bold": True, "top": 1, "right": 1, "bottom": 2, "left": 1, "align": "center",
         "valign": "vcenter", "num_format": "0", })
    format2 = workbook.add_format(
        {"bg_color": "#2F75B5", "bold": True, "top": 1, "right": 1, "bottom": 2, "left": 1, "align": "center",
         "valign": "vcenter", "num_format": "0.000", })

    for wkst in [wkst1, wkst2, wkst3, wkst4]:
        if is_valid_number(alt, "altitude"):
            wkst.write_number(1, i + 1, float(alt), format1)
        if is_valid_number(machNo, "mach noumber"):
            wkst.write_number(2, i + 1, float(machNo), format2)
        if is_valid_number(t_maxQ, "t_maxQ"):
            wkst.write_number(3, i + 1, float(t_maxQ), format1)

    for j in range(0, len(x)):
        if is_valid_number(axial_loads[j][1], "axial_loads"):
            wkst1.write_number(4 + j, 1 + i, float(axial_loads[j][1]) / 1e3, format_output_3dig)
        if is_valid_number(shear_loads[j][1], "shear_loads"):
            wkst2.write_number(4 + j, 1 + i, float(shear_loads[j][1]) / 1e3, format_output_3dig)
        if is_valid_number(bending_moments[j][1], "bending_moments"):
            wkst3.write_number(4 + j, 1 + i, float(bending_moments[j][1]) / 1e3, format_output_3dig)
        if is_valid_number(margins_of_safety[j][1], "margins_of_safety"):
            wkst4.write_number(4 + j, 1 + i, float(margins_of_safety[j][1]), format_output_3dig)

    return 1


def excel_export_data_min_max(workbook, i, label, axial_loads, shear_loads, bending_moments, margins_of_safety,
                              format_output_3dig):
    # Separate output vectors
    x = []
    y_al = []
    y_sl = []
    y_bm = []
    y_mos = []
    for row in axial_loads:
        x.append(row[0])
        y_al.append(row[1])

    for row in shear_loads:
        y_sl.append(row[1])

    for row in bending_moments:
        y_bm.append(row[1])

    for row in margins_of_safety:
        if row[1] < 10:
            y_mos.append(row[1])
        else:
            y_mos.append(10)

    wkst1 = workbook.get_worksheet_by_name("Axial_Load_Data")
    wkst2 = workbook.get_worksheet_by_name("Shear_Load_Data")
    wkst3 = workbook.get_worksheet_by_name("Bending_Mom_Data")
    wkst4 = workbook.get_worksheet_by_name("Margin_of_Safety_Data")
    format1 = workbook.add_format(
        {"bg_color": "#2F75B5", "bold": True, "top": 1, "right": 1, "bottom": 2, "left": 1, "align": "center",
         "valign": "vcenter", "num_format": "0", })
    # format2 = workbook.add_format(
    #     {
    #         "bg_color": "#2F75B5",
    #         "bold": True,
    #         "top": 1,
    #         "right": 1,
    #         "bottom": 2,
    #         "left": 1,
    #         "align": "center",
    #         "valign": "vcenter",
    #         "num_format": "0.000",
    #     }
    # )
    for wkst in [wkst1, wkst2, wkst3, wkst4]:
        wkst.merge_range(1, i + 1, 3, i + 1, label, format1)

    for j in range(0, len(x)):
        wkst1.write_number(4 + j, 1 + i, axial_loads[j][1] * 1e-3, format_output_3dig)
        wkst2.write_number(4 + j, 1 + i, shear_loads[j][1] * 1e-3, format_output_3dig)
        wkst3.write_number(4 + j, 1 + i, bending_moments[j][1] * 1e-3, format_output_3dig)
        wkst4.write_number(4 + j, 1 + i, margins_of_safety[j][1], format_output_3dig)
    return 1


def excel_FBD_data(workbook, i, alt, machNo, t_maxQ, fbd, format_output_3dig):
    format1 = workbook.add_format(
        {"bg_color": "#2F75B5", "bold": True, "top": 1, "right": 1, "bottom": 2, "left": 1, "align": "center",
         "valign": "vcenter", "num_format": "0", })
    format2 = workbook.add_format(
        {"bg_color": "#2F75B5", "bold": True, "top": 1, "right": 1, "bottom": 2, "left": 1, "align": "center",
         "valign": "vcenter", "num_format": "0.000", })

    wkst = workbook.get_worksheet_by_name("Free_Body_Diagram")
    if i == 0:
        wkst.write_string(4, 0, "Longitudinal Thrust, Tx [kN]", format_output_3dig)
        wkst.write_string(5, 0, "Transverse Thrust, Tz [kN]", format_output_3dig)
        wkst.write_string(6, 0, "Transverse Aerodynamic Load, F_aero [kN]", format_output_3dig)
        wkst.write_string(7, 0, "Drag Force, Fd_core [kN]", format_output_3dig)
        wkst.write_string(8, 0, "Longitudinal acceleration, gx [m/s2]", format_output_3dig)
        wkst.write_string(9, 0, "Transverse acceleration, gz [m/s2]", format_output_3dig)
        wkst.write_string(10, 0, "Dynamic pressure, q [kPa]", format_output_3dig)
        wkst.write_string(11, 0, "Angle of attack, AoA, [deg]", format_output_3dig)
        wkst.write_string(12, 0, "Distance to gimbal point, GP, [m]", format_output_3dig)
        wkst.write_string(13, 0, "Distance to centre of gravity, CoG, [m]", format_output_3dig)
        wkst.write_string(14, 0, "Distance to centre of pressure, CoP, [m]", format_output_3dig)

    wkst.write_number(1, i + 1, alt, format1)
    wkst.write_number(2, i + 1, machNo, format2)
    wkst.write_number(3, i + 1, t_maxQ, format1)
    for j in range(0, 11):
        wkst.write_number(j + 4, 1 + i, fbd[j], format_output_3dig)
    return 1


def excel_FBD_data_min_max(workbook, i, alt, machNo, t_maxQ, fbd, format_output_3dig):
    format1 = workbook.add_format(
        {"bg_color": "#2F75B5", "bold": True, "top": 1, "right": 1, "bottom": 2, "left": 1, "align": "center",
         "valign": "vcenter", "num_format": "0", })
    # format2 = workbook.add_format(
    #     {
    #         "bg_color": "#2F75B5",
    #         "bold": True,
    #         "top": 1,
    #         "right": 1,
    #         "bottom": 2,
    #         "left": 1,
    #         "align": "center",
    #         "valign": "vcenter",
    #         "num_format": "0.000",
    #     }
    # )

    wkst = workbook.get_worksheet_by_name("Free_Body_Diagram")
    wkst.merge_range(1, i + 1, 3, i + 1, "Min", format1)
    wkst.merge_range(1, i + 2, 3, i + 2, "Max", format1)
    for j in range(0, 11):
        data_range = "$B$" + str(j + 5) + ":$AB$" + str(j + 5)
        max_str = "=MAX(" + data_range + ")"
        min_str = "=MIN(" + data_range + ")"
        col1 = "AC" + str(j + 5)
        col2 = "AD" + str(j + 5)
        wkst.write_formula(col1, max_str, format_output_3dig)
        wkst.write_formula(col2, min_str, format_output_3dig)
    return 1


def free_body_diagram_core_rocket(mass, CoG, GP, aero_forces, Fd, total_thrust, g_x, g_z, alpha_TVC, x_aft, x_fwd):
    F_aero = 0  # Total aerodynamic force [N]
    M_aero = 0  # Total aerodynamic moment [Nm]
    for force in aero_forces:
        F_aero += force[1]
        M_aero += (force[0] - CoG) * force[1]
    CoP = CoG + M_aero / F_aero  # Rocket center of pressure [m]
    T_z = total_thrust * math.sin(alpha_TVC * math.pi / 180)  # Engine lateral thrust [N]
    T_x = total_thrust * math.cos(alpha_TVC * math.pi / 180)  # Engine axial thrust [N]

    a = mass * g_z - T_z - F_aero
    b = CoG - GP
    c = CoG - CoP
    d = CoG - x_aft
    e = CoG - x_fwd
    I_fwd_z = (b * T_z + c * F_aero + d * a) / (d - e)
    I_aft_z = a - I_fwd_z
    I_fwd_x = mass * g_x - T_x + Fd

    return F_aero, M_aero, T_z, T_x, I_fwd_x, I_fwd_z, I_aft_z, CoP


def free_body_diagram_full_vehicle(mass, CoG, GP, aero_forces, Fd_tot, total_thrust):
    F_aero = 0  # Total aerodynamic force [N]
    M_aero = 0  # Total aerodynamic moment [Nm]
    for force in aero_forces:
        F_aero += force[1]
        M_aero += (force[0] - CoG) * force[1]
    T_z = M_aero / (CoG - GP)  # Engine lateral thrust [N]
    T_x = math.sqrt(total_thrust ** 2 - T_z ** 2)  # Engine axial thrust [N]

    g_x = (T_x - Fd_tot) / mass  # Axial acceleration of the rocket [m/s2]
    g_z = (F_aero + T_z) / mass  # Lateral acceleration of the rocket [m/s2]
    CoP = CoG + M_aero / F_aero  # Rocket center of pressure [m]
    alpha_TVC = math.atan(T_z / T_x) * (180 / math.pi)  # Estimated TVC angle [deg]
    return F_aero, M_aero, T_z, T_x, g_x, g_z, alpha_TVC, CoP


def import_aerodynamic_forces(cone_angle, cone_length, AoA, rocket_length, rocket_diameter, machNo, dynamic_pressure,
                              n_points):
    # Import external aerodynamic data for the cone
    machNo_cone = [0.70, 0.80, 0.90, 0.95, 1.00, 1.10, 1.20, 1.50, 2.00, ]  # Mach Number data points

    x_pos_cone = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]  # Relative position along the cone x/L

    half_angle_cone = [10, 15, 20, 25, 30, 33, 40]  # Cone half angles [deg]

    aero_coefficients_cone = []
    for i in range(0, 9):
        df_aero_cone = pd.read_excel("./.loadCaseData/aerodynamic_coefficients.xlsx", sheet_name="Cone",
                                     skiprows=1 + 8 * i, nrows=6, usecols=[1, 2, 3, 4, 5, 6, 7], )
        aero_coefficients_cone.append(df_aero_cone.values.tolist())

    # Import external aerodynamic data for the cylinder
    machNo_cyl = [0.70, 0.80, 0.90, 0.95, 1.00, 1.10, 1.20, 1.50, 2.00, ]  # Mach Number data points

    x_pos_cyl = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, ]  # Relative position along the cylinder x/D

    half_angle_cyl = [10, 15, 20, 25, 30, 33, 40]  # Cylinder half angles [deg]

    aero_coefficients_cylinder = []
    for i in range(0, 9):
        df_aero_cylinder = pd.read_excel("./.loadCaseData/aerodynamic_coefficients.xlsx", sheet_name="Cylinder",
                                         skiprows=1 + 13 * i, nrows=11, usecols=[1, 2, 3, 4, 5, 6, 7], )
        aero_coefficients_cylinder.append(df_aero_cylinder.values.tolist())

    # Interpolate coefficient data for the analysed rocket (Cone)
    index_machNo = None
    for i in range(0, len(machNo_cone)):
        if (machNo_cone[i]) > machNo:
            index_machNo = i
            break
    if not index_machNo:
        raise ValueError("Index machNo not found.")

    index_angle = None
    for j in range(0, len(half_angle_cone)):
        if half_angle_cone[j] > cone_angle:
            index_angle = j
            break
    if not index_angle:
        raise ValueError("Index angle not found.")

    interp_cone_machNo = [[-9999 for i in range(len(half_angle_cone))] for j in range(len(x_pos_cone))]
    for i in range(0, len(x_pos_cone)):
        for j in range(0, len(half_angle_cone)):
            x1 = machNo_cone[index_machNo - 1]
            x2 = machNo_cone[index_machNo]
            y1 = aero_coefficients_cone[index_machNo - 1][i][j]
            y2 = aero_coefficients_cone[index_machNo][i][j]
            interp_cone_machNo[i][j] = y1 + (machNo - x1) * (y2 - y1) / (x2 - x1)

    interp_cone_angle = []
    for i in range(0, len(x_pos_cone)):
        x1 = half_angle_cone[index_angle - 1]
        x2 = half_angle_cone[index_angle]
        y1 = interp_cone_machNo[i][index_angle - 1]
        y2 = interp_cone_machNo[i][index_angle]
        interp_cone_angle.append(y1 + (cone_angle - x1) * (y2 - y1) / (x2 - x1))

    # Interpolate coefficient data for the analysed rocket (Cylinder)
    for i in range(0, len(machNo_cyl)):
        if (machNo_cyl[i]) > machNo:
            index_machNo = i
            break
    for j in range(0, len(half_angle_cyl)):
        if half_angle_cyl[j] > cone_angle:
            index_angle = j
            break

    interp_cyl_machNo = [[-9999 for i in range(len(half_angle_cyl))] for j in range(len(x_pos_cyl))]
    for i in range(0, len(x_pos_cyl)):
        for j in range(0, len(half_angle_cyl)):
            x1 = machNo_cyl[index_machNo - 1]
            x2 = machNo_cyl[index_machNo]
            y1 = aero_coefficients_cylinder[index_machNo - 1][i][j]
            y2 = aero_coefficients_cylinder[index_machNo][i][j]
            interp_cyl_machNo[i][j] = y1 + (machNo - x1) * (y2 - y1) / (x2 - x1)

    interp_cyl_angle = []
    for i in range(0, len(x_pos_cyl)):
        x1 = half_angle_cyl[index_angle - 1]
        x2 = half_angle_cyl[index_angle]
        y1 = interp_cyl_machNo[i][index_angle - 1]
        y2 = interp_cyl_machNo[i][index_angle]
        interp_cyl_angle.append(y1 + (cone_angle - x1) * (y2 - y1) / (x2 - x1))

    # Create coefficient table
    coeff_table = []
    force_table = []
    dx_prev = 0
    for i in range(0, n_points, 1):
        dx = i * rocket_length / n_points
        pos_i = rocket_length - dx
        if i == 0:
            aero_coeff = 0.0
            aero_force = 0
        else:
            # Nose cone aerodynamic loads
            if dx < cone_length:
                aero_coeff = np.interp(dx / cone_length, x_pos_cone, interp_cone_angle)
            # Cylinder aerodynamic loads close to the nose cone
            elif (dx - cone_length) / rocket_diameter < 2.0:
                aero_coeff = np.interp((dx - cone_length) / rocket_diameter, x_pos_cyl, interp_cyl_angle)
            # Cylinder aerodynamic loads far from the nose cone
            else:
                aero_coeff = 0.0
            # Calculation of aerodynamic force
            aero_force = (-aero_coeff * (AoA * math.pi / 180) * (dx - dx_prev) / rocket_diameter * dynamic_pressure * (
                    0.25 * math.pi * rocket_diameter ** 2))

        coeff_table.append([pos_i, aero_coeff])
        coeff_table.sort(key=lambda x: x[0])
        force_table.append([pos_i, aero_force])
        force_table.sort(key=lambda x: x[0])
        dx_prev = dx

    return force_table, coeff_table


def import_input_data(input_filename):
    if input_filename == "":
        raise ValueError("No input file selected")

    df = pd.read_excel(input_filename, sheet_name="General")
    tab_general = df.values.tolist()

    inputs = []
    for row in tab_general:
        inputs.append(row[3])

    df_inert = pd.read_excel(input_filename, sheet_name="Inert Mass")
    inert_mass_table = df_inert.values.tolist()
    inert_mass_table.sort(key=lambda x: x[0])

    df_rocket = pd.read_excel(input_filename, sheet_name="Rocket Configuration")
    rocket_conf_table = df_rocket.values.tolist()
    rocket_conf_table.sort(key=lambda x: x[0])

    df_printout = pd.read_excel(input_filename, sheet_name="Printout Locations")
    printout_table = df_printout.values.tolist()
    printout_table.sort(key=lambda x: x[0])

    return inputs, inert_mass_table, rocket_conf_table, printout_table


def linearize_2D_matrix(matrix, starting_length, ending_length, no_of_points):
    # Unified x output vector
    x = []
    y = []
    for row in matrix:
        x.append(row[0])
        y.append(row[1])
    x_u = np.linspace(starting_length, ending_length, no_of_points)
    y_u = np.interp(x_u, x, y)

    output_matrix = []
    for i in range(0, len(x_u)):
        output_matrix.append([x_u[i], y_u[i]])
    return output_matrix


def vloads(inputs, alt, machNo, t_maxQ, rocket_conf_table, inert_mass_table):
    q_alpha = inputs[1]  # [kPa*deg]
    L_n_core = inputs[2]  # Length of the conical section of the nosecone of
    # the core rocket [m]
    omega_core = inputs[3]  # Nosecone semi-vertex angle of the core rocket [deg]
    D_core = inputs[4]  # Diameter of the core rocket [m]
    L_s1 = inputs[5]  # Stage 1 length [m]
    L_s2 = inputs[6]  # Stage 2 length [m]
    L_s3 = inputs[7]  # Stage 3 length [m]
    L_f = inputs[8]  # Fairing length [m]
    GP = inputs[9]  # Distance from nozzle exit to Stage 1 engine gimbal plane [m]
    L_s1_blk_bot = inputs[10]  # Distance from nozzle exit to Stage 1 bottom tank head [m]
    L_s1_blk_mid = inputs[11]  # Distance from nozzle exit to Stage 1 bulkhead [m]
    L_s1_blk_top = inputs[12]  # Distance from nozzle exit to Stage 1 top tank head [m]
    L_s2_blk_bot = inputs[13]  # Distance from nozzle exit to Stage 2 bottom tank head [m]
    L_s2_blk_mid = inputs[14]  # Distance from nozzle exit to Stage 2 bulkhead [m]
    L_s2_blk_top = inputs[15]  # Distance from nozzle exit to Stage 2 top tank head [m]
    m_s1_bot = inputs[16]  # Total lift-off propellant mass in Stage 1 bottom tank [kg]
    m_s1_top = inputs[17]  # Total lift-off propellant mass in Stage 1 top tank [kg]
    m_s2_bot = inputs[18]  # Total lift-off propellant mass in Stage 2 bottom tank [kg]
    m_s2_top = inputs[19]  # Total lift-off propellant mass in Stage 2 top tank [kg]
    p_s1 = inputs[20] * 1e5  # First stage tank pressurization level [Pa]
    p_s2 = inputs[21] * 1e5  # Second stage tank pressurization level [Pa]

    # inputs[22] is empty
    n_b = int(inputs[23])  # Number of boosters
    m_b = inputs[24]  # Mass of each booster [kg]
    CoG_b = inputs[25]  # Centre of gravity of a booster [m]
    T_b = inputs[26]  # Thrust of each booster [N]
    D_b = inputs[27]  # Diameter of each booster [m]
    L_b = inputs[28]  # Length of each booster [m]
    L_n_b = inputs[29]  # Length of the nosecone of a booster [m]
    omega_b = inputs[30]  # Nosecone semi-vertex angle of a booster [deg]
    x_fwd = inputs[31]  # Location of the foward booster attach point
    # counted from engine gimbal [m]
    x_aft = inputs[32]  # Location of the aft booster attach point
    # counted from engine gimbal [m]
    # inputs[33] is empty
    t_S1burn = inputs[43]  # Time to Stage 1 End of Burn

    # inputs[44] is empty
    n_e = inputs[45]  # Number of engines
    T_e = inputs[46]  # Stage 1 single engine sea-level thrust [N]
    p_e = inputs[47]  # Stage 1 engine nozzle exhaust pressure [Pa]
    A_e = inputs[48]  # Stage 1 single engine nozzle area [m2]

    # Adjust thrust according to altitude and calculate flight speed
    temp_0, p_0, rho_0 = calculate_standard_atmosphere_conditions(0.0)
    m_e = (m_s1_bot + m_s1_top) / t_S1burn
    v_e = (T_e - (p_e - p_0) * A_e) / m_e  # Nozzle exit velocity [m/s]

    temp_air, p_air, rho_air = calculate_standard_atmosphere_conditions(alt)
    speed_of_sound = math.sqrt(1.4 * 287 * temp_air)
    v_air = machNo * speed_of_sound  # Flight speed [m/s]
    T_core = (m_e * v_e + (p_e - p_air) * A_e) * n_e  # Total thrust of the rocket [N]

    propellant_mass_table = distribute_propellant_masses(20, D_core, L_s1_blk_bot, L_s1_blk_mid, L_s1_blk_top,
                                                         L_s2_blk_bot, L_s2_blk_mid, L_s2_blk_top, m_s1_bot, m_s1_top,
                                                         m_s2_bot, m_s2_top, t_maxQ, t_S1burn, )

    # Adjust rocket_conf_table for future interpolation
    row = rocket_conf_table[-1].copy()
    row[0] = L_s1 + L_s2 + L_s3 + L_f + 1.0
    rocket_conf_table.append(row)

    L_core = L_s1 + L_s2 + L_s3 + L_f  # Total length of the core rocket [m]
    T_tot = T_core + T_b * n_b
    q = 0.5 * rho_air * v_air ** 2  # Dynamic pressure [Pa]
    AoA = 1000 * q_alpha / q  # Flight angle of attack [deg]
    Cd_core = 0.0112 * omega_core + 0.162  # Drag coefficient of the nosecone of
    # the core rocket
    Cd_b = 0.0112 * omega_b + 0.162  # Drag coefficient of the nosecone of a
    # booster

    SF_axial = 1  # Axial force safety factor
    SF_shear = 1  # Shear force safety factor
    SF_bending = 1  # Bending moment safety factor

    if machNo < 0.7:
        aero_forces_core, coeff_table_core = import_aerodynamic_forces(omega_core, L_n_core, AoA, L_core, D_core, 0.701,
                                                                       q, 250)
        aero_forces_b, coeff_table_b = import_aerodynamic_forces(omega_b, L_n_b, AoA, L_b, D_b, 0.701, q, 250)

    elif machNo > 2.0:
        aero_forces_core, coeff_table_core = import_aerodynamic_forces(omega_core, L_n_core, AoA, L_core, D_core, 1.99,
                                                                       q, 250)
        aero_forces_b, coeff_table_b = import_aerodynamic_forces(omega_b, L_n_b, AoA, L_b, D_b, 1.99, q, 250)

    else:
        aero_forces_core, coeff_table_core = import_aerodynamic_forces(omega_core, L_n_core, AoA, L_core, D_core,
                                                                       machNo, q, 250)

        aero_forces_b, coeff_table_b = import_aerodynamic_forces(omega_b, L_n_b, AoA, L_b, D_b, machNo, q, 250)

    aero_forces_c_b = combine_core_and_booster_aero_forces(aero_forces_core, aero_forces_b, n_b)

    mass_table_core = combine_inert_and_propellant_masses(inert_mass_table, propellant_mass_table)

    CoG_core, m_core = calculate_CoG(mass_table_core)
    CoG_tot = (n_b * m_b * CoG_b + CoG_core * m_core) / (
            n_b * m_b + m_core)  # Centre of gravity of the full vehicle (core + boosters)
    m_tot = m_core + n_b * m_b  # Total mass of the core rocket and boosters [kg]
    A_core = 0.25 * math.pi * D_core ** 2  # Cross-sectional area of the core rocket [m2]
    A_b = 0.25 * math.pi * D_b ** 2  # Cross-sectional area of a booster [m2]
    Fd_tot = q * (A_core * Cd_core + n_b * A_b * Cd_b)  # Total drag force due to dynamic pressure [N]
    Fd_core = q * A_core * Cd_core  # Drag force due to dynamic pressure acting on the core rocket [N]

    _, _, _, _, g_x, g_z, alpha_TVC, _ = free_body_diagram_full_vehicle(m_tot, CoG_tot, GP, aero_forces_c_b, Fd_tot,
                                                                        T_tot)

    F_aero, M_aero, T_z, T_x, I_fwd_x, I_fwd_z, I_aft_z, CoP = free_body_diagram_core_rocket(m_core, CoG_core, GP,
                                                                                             aero_forces_core, Fd_core,
                                                                                             T_core, g_x, g_z,
                                                                                             alpha_TVC, x_aft, x_fwd, )

    inertial_forces = calculate_inertial_forces(mass_table_core, g_x, g_z)
    axial_forces, lateral_forces = combine_inertial_and_aero_forces(GP, T_x, T_z, x_aft, I_aft_z, x_fwd, I_fwd_x,
                                                                    I_fwd_z, aero_forces_core, inertial_forces, )
    axial_loads = calculate_axial_loads(axial_forces, L_core)
    shear_loads = calculate_shear_loads(lateral_forces)
    bending_moments = calculate_bending_moments(shear_loads)

    axial_loads_sf, shear_loads_sf, bending_moments_sf = apply_safety_factors(SF_axial, SF_shear, SF_bending,
                                                                              axial_loads, shear_loads, bending_moments)

    # Linearize all loads matrices to the same axial positions
    x_lin = np.linspace(0.0, L_core, 1000)
    axial_loads_sf_lin = linearize_2D_matrix(axial_loads_sf, 0.0, L_core, 1000)
    shear_loads_sf_lin = linearize_2D_matrix(shear_loads_sf, 0.0, L_core, 1000)
    bending_moments_sf_lin = linearize_2D_matrix(bending_moments_sf, 0.0, L_core, 1000)

    # Buckling margin of safety calculations
    margins_of_safety = []
    rocket_conf_table2 = []
    for i in range(0, len(x_lin)):
        x_target = x_lin[i]
        x_next = -9999
        # x = rocket_conf_table[0][0]
        radius = rocket_conf_table[0][1] * 1e-3
        wall_thickness = rocket_conf_table[0][2] * 1e-3  # TODO: either update the excel with real thickness or get rid of it

        if L_s1_blk_bot < x_target < L_s1_blk_top:
            p_internal = rocket_conf_table[0][3] * 1e5  # TODO: either update the excel with real pressure or get rid of it
        elif L_s2_blk_bot < x_target < L_s2_blk_top:
            p_internal = rocket_conf_table[0][3] * 1e5  # TODO: either update the excel with real pressure or get rid of it
        else:
            p_internal = 0.0

        metal_bool = rocket_conf_table[0][4]
        Exx = rocket_conf_table[0][5] * 1e6  # MPA *1e6
        Eyy = rocket_conf_table[0][6] * 1e6  # MPA *1e6
        Ezz = rocket_conf_table[0][7] * 1e6  # MPA *1e6
        vxx = rocket_conf_table[0][8]
        vyy = rocket_conf_table[0][9]
        vzz = rocket_conf_table[0][10]
        Gxx = rocket_conf_table[0][11] * 1e6  # MPA *1e6
        Gyy = rocket_conf_table[0][12] * 1e6  # MPA *1e6
        Gzz = rocket_conf_table[0][13] * 1e6  # MPA *1e6
        for j in range(1, len(rocket_conf_table)):
            x_next = rocket_conf_table[j][0]
            if x_next < x_target:
                # x = rocket_conf_table[j][0]
                radius = rocket_conf_table[j][1] * 1e-3
                wall_thickness = rocket_conf_table[j][2] * 1e-3
                p_internal = rocket_conf_table[j][3] * 1e5
                metal_bool = rocket_conf_table[j][4]
                Exx = rocket_conf_table[j][5] * 1e6  # MPA *1e6
                Eyy = rocket_conf_table[j][6] * 1e6  # MPA *1e6
                Ezz = rocket_conf_table[j][7] * 1e6  # MPA *1e6
                vxx = rocket_conf_table[j][8]
                vyy = rocket_conf_table[j][9]
                vzz = rocket_conf_table[j][10]
                Gxx = rocket_conf_table[j][11] * 1e6  # MPA *1e6
                Gyy = rocket_conf_table[j][12] * 1e6  # MPA *1e6
                Gzz = rocket_conf_table[j][13] * 1e6  # MPA *1e6

        rocket_conf_table2.append(
            [x_target, radius, wall_thickness, p_internal, metal_bool, Exx, Eyy, Ezz, vxx, vyy, vzz, Gxx, Gyy, Gzz, ])

        F_axial = axial_loads_sf_lin[i][1]
        M_bending = bending_moments_sf_lin[i][1]

        if x_target <= GP:
            MoS_section = 0.0  # safety margin is set to zero in the nozzle area
        elif metal_bool == "M":
            # Calculate buckling margin for metals
            MoS_section = calculate_buckling_margin(F_axial, M_bending, radius, wall_thickness, vxx, p_internal, Exx)
        else:
            MoS_section = calculate_buckling_margin(F_axial, M_bending, radius, wall_thickness, vxx, p_internal, Exx)
            # TODO add buckling margin calculation for orthotropic materials (refer to NASA SP-8007 p.16)

        margins_of_safety.append([x_target, MoS_section])

    fbd = [T_x / 1000, T_z / 1000, F_aero / 1000, Fd_core / 1000, g_x, g_z, q / 1000, AoA, GP, CoG_core, CoP, ]

    return [axial_loads_sf_lin, shear_loads_sf_lin, bending_moments_sf_lin, margins_of_safety, rocket_conf_table2,
            fbd, ]


# program by Tomasz Witkowski
def loadCaseCalculator():
    root = Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)
    input_filename = "./.loadCaseData/input_template.xlsx"
    input_folder = Path(input_filename).parents[0]

    inputs, inert_mass_table, rocket_conf_table, printout_table = import_input_data(input_filename)

    L_s1 = inputs[5]  # Stage 1 length [m]
    L_s2 = inputs[6]  # Stage 2 length [m]
    L_s3 = inputs[7]  # Stage 3 length [m]
    L_f = inputs[8]  # Fairing length [m]
    # L_launcher = L_s1 + L_s2 + L_s3 + L_f
    L_launcher = L_s1 + L_s2 # excluded stage 3 and fairing from excel charts

    # alt_min = inputs[34]
    alt_nom = inputs[35]
    # alt_max = inputs[36]
    machNo_min = inputs[37]
    machNo_nom = inputs[38]
    machNo_max = inputs[39]
    # t_maxQ_min = inputs[40]
    t_maxQ_nom = inputs[41]
    # t_maxQ_max = inputs[42]

    if machNo_min < 0.7:
        warnings.warn("Mach Number below the available data range (0.7 - 2.0). " +
                      "Aerodynamic data at machNo 0.7 are used instead. Please verify carefully!.")
    elif machNo_max > 2.0:
        warnings.warn("Mach Number above the available data range (0.7 - 2.0). " +
                      "Aerodynamic data at machNo 2.0 are used instead. Please verify carefully!.")

    path = input_folder / "Output_Report.xlsx"
    workbook = xlsxwriter.Workbook(path)

    # Create format types for Ouput Excel file
    format_background = workbook.add_format({"bg_color": "#D9D9D9"})
    format_header = workbook.add_format(
        {"bg_color": "#2F75B5", "bold": True, "top": 1, "right": 1, "bottom": 2, "left": 1, "align": "center",
         "valign": "vcenter", "text_wrap": True, })
    format_output_3dig = workbook.add_format(
        {"bg_color": "#FFFF00", "bold": True, "top": 1, "right": 1, "bottom": 1, "left": 1, "align": "center",
         "valign": "vcenter", "num_format": "0.000", })
    # format_output_1dig = workbook.add_format(
    #     {
    #         "bg_color": "#FFFF00",
    #         "bold": True,
    #         "top": 1,
    #         "right": 1,
    #         "bottom": 1,
    #         "left": 1,
    #         "align": "center",
    #         "valign": "vcenter",
    #         "num_format": "0.0",
    #     }
    # )
    format_output_int = workbook.add_format(
        {"bg_color": "#FFFF00", "bold": True, "top": 1, "right": 1, "bottom": 1, "left": 1, "align": "center",
         "valign": "vcenter", "num_format": "0", })
    # format_output_exp = workbook.add_format(
    #     {
    #         "bg_color": "#FFFF00",
    #         "bold": True,
    #         "top": 1,
    #         "right": 1,
    #         "bottom": 1,
    #         "left": 1,
    #         "align": "center",
    #         "valign": "vcenter",
    #         "num_format": "0.00E+00",
    #     }
    # )
    format_output_str = workbook.add_format(
        {"bg_color": "#FFFF00", "bold": True, "top": 1, "right": 1, "bottom": 1, "left": 1, "align": "center",
         "valign": "vcenter", })
    # Create Excel tabs
    wkst9 = workbook.add_worksheet("Free_Body_Diagram")
    wkst8 = workbook.add_worksheet("Stations")
    wkst5 = workbook.add_chartsheet("Axial_Load_Graph")
    wkst6 = workbook.add_chartsheet("Shear_Load_Graph")
    wkst7 = workbook.add_chartsheet("Bending_Mom_Graph")
    wkst10 = workbook.add_chartsheet("Margin_Of_Safety_Graph")
    wkst1 = workbook.add_worksheet("Axial_Load_Data")
    wkst2 = workbook.add_worksheet("Shear_Load_Data")
    wkst3 = workbook.add_worksheet("Bending_Mom_Data")
    wkst4 = workbook.add_worksheet("Margin_of_Safety_Data")

    # Prepare FBD tab
    wkst9.merge_range("B1:AD1", "Free Body Diagram (before safety factors)", format_header)
    wkst9.set_column(0, 0, 38.86, format_background, {})
    wkst9.set_column(1, 40, 8.46, format_background, {})
    wkst9.write_string(0, 0, "Distance from nozzle exit plane [m]", format_header)
    wkst9.write_string(1, 0, "Altitude [m]", format_header)
    wkst9.write_string(2, 0, "Mach Number", format_header)
    wkst9.write_string(3, 0, "Time to MaxQ [s]", format_header)

    # Prepare Data tabs
    wkst1.merge_range("B1:AD1", "Axial Load Data [kN]", format_header)
    wkst2.merge_range("B1:AD1", "Shear Load Data [kN]", format_header)
    wkst3.merge_range("B1:AD1", "Bending Moment Data [kNm]", format_header)
    wkst4.merge_range("B1:AD1", "Margin of Safety Data [-]", format_header)

    for wkst in [wkst1, wkst2, wkst3, wkst4]:
        wkst.set_column(0, 0, 27.86, format_background, {})
        wkst.set_column(1, 40, 8.46, format_background, {})
        wkst.write_string(0, 0, "Distance from nozzle exit plane [m]", format_header)
        wkst.write_string(1, 0, "Altitude [m]", format_header)
        wkst.write_string(2, 0, "Mach Number", format_header)
        wkst.write_string(3, 0, "Time to MaxQ [s]", format_header)

    # Prepare Summary tab
    wkst8.set_column(0, 1, 8.43, format_background, {})
    wkst8.set_column(2, 2, 25.0, format_background, {})
    wkst8.set_column(3, 40, 10.29, format_background, {})
    wkst8.merge_range("A1:C1", "Station", format_header)
    wkst8.merge_range("D1:F1", "Best", format_header)
    wkst8.merge_range("G1:I1", "Nominal", format_header)
    wkst8.merge_range("J1:L1", "Worst", format_header)
    wkst8.write_string(1, 0, "Position [m]", format_header)
    wkst8.write_string(1, 1, "Label", format_header)
    wkst8.write_string(1, 2, "Description", format_header)
    for i in range(0, 3):
        wkst8.write_string(1, 3 + 3 * i, "Axial Load [kN]", format_header)
        wkst8.write_string(1, 4 + 3 * i, "Shear Load [kN]", format_header)
        wkst8.write_string(1, 5 + 3 * i, "Bending Moment [kNm]", format_header)

    # Run VLOADS for each case and put output of each calculations in appropriate Data tab
    axial_loads_worst = []
    shear_loads_worst = []
    bending_moments_worst = []
    margins_of_safety_worst = []
    axial_loads_best = []
    shear_loads_best = []
    bending_moments_best = []
    margins_of_safety_best = []
    for i in range(0, 1000):
        axial_loads_worst.append([0.0, 0.0])
        shear_loads_worst.append([0.0, 0.0])
        bending_moments_worst.append([0.0, 0.0])
        margins_of_safety_worst.append([0.0, 0.0])

        axial_loads_best.append([0.0, 999999999.0])
        shear_loads_best.append([0.0, 999999999.0])
        bending_moments_best.append([0.0, 999999999.0])
        margins_of_safety_best.append([0.0, 999999999.0])

    i = 0
    # for alt in [alt_nom, alt_min, alt_max]:
    #     for machNo in [machNo_nom, machNo_min, machNo_max]:
    #         for t_maxQ in [t_maxQ_nom, t_maxQ_min, t_maxQ_max]:
    for alt in [alt_nom]:
        for machNo in [machNo_nom]:
            for t_maxQ in [t_maxQ_nom]:
                output_table = vloads(inputs, alt, machNo, t_maxQ, rocket_conf_table, inert_mass_table)

                axial_loads = output_table[0]
                shear_loads = output_table[1]
                bending_moments = output_table[2]
                margins_of_safety = output_table[3]
                # rocket_configuration = output_table[4]
                fbd = output_table[5]

                # import matplotlib.pyplot as plt
                # plt.figure()
                # plt.plot([FS[0] for FS in margins_of_safety[:-1]], [FS[1] for FS in margins_of_safety[:-1]])
                # # plt.plot(margins_of_safety[:, 0], margins_of_safety[:, 1])
                # plt.show()

                if i == 0:
                    axial_loads_nom = axial_loads
                    shear_loads_nom = shear_loads
                    bending_moments_nom = bending_moments

                for j in range(0, 1000):
                    if abs(axial_loads[j][1]) >= abs(axial_loads_worst[j][1]):
                        axial_loads_worst[j] = axial_loads[j]
                    if abs(shear_loads[j][1]) >= abs(shear_loads_worst[j][1]):
                        shear_loads_worst[j] = shear_loads[j]
                    if abs(bending_moments[j][1]) >= abs(bending_moments_worst[j][1]):
                        bending_moments_worst[j] = bending_moments[j]
                    if abs(margins_of_safety[j][1]) > abs(margins_of_safety_worst[j][1]):
                        margins_of_safety_worst[j] = margins_of_safety[j]

                    if abs(axial_loads[j][1]) <= abs(axial_loads_best[j][1]):
                        axial_loads_best[j] = axial_loads[j]
                    if abs(shear_loads[j][1]) <= abs(shear_loads_best[j][1]):
                        shear_loads_best[j] = shear_loads[j]
                    if abs(bending_moments[j][1]) <= abs(bending_moments_best[j][1]):
                        bending_moments_best[j] = bending_moments[j]
                    if abs(margins_of_safety[j][1]) < abs(margins_of_safety_best[j][1]):
                        margins_of_safety_best[j] = margins_of_safety[j]

                excel_export_data(workbook, i, alt, machNo, t_maxQ, axial_loads, shear_loads, bending_moments,
                                  margins_of_safety, format_output_3dig)

                excel_FBD_data(workbook, i, alt, machNo, t_maxQ, fbd, format_output_3dig)
                i += 1

    excel_export_data_min_max(workbook, i, "Best", axial_loads_best, shear_loads_best, bending_moments_best,
                              margins_of_safety_best, format_output_3dig)

    excel_export_data_min_max(workbook, i + 1, "Worst", axial_loads_worst, shear_loads_worst, bending_moments_worst,
                              margins_of_safety_worst, format_output_3dig)

    excel_FBD_data_min_max(workbook, i, alt, machNo, t_maxQ, fbd, format_output_3dig)

    excel_create_stations_sheet(wkst8, "Best", axial_loads_best, shear_loads_best, bending_moments_best, printout_table,
                                format_output_3dig, format_output_str, format_output_int)
    excel_create_stations_sheet(wkst8, "Nominal", axial_loads_nom, shear_loads_nom, bending_moments_nom, printout_table,
                                format_output_3dig, format_output_str, format_output_int)
    excel_create_stations_sheet(wkst8, "Worst", axial_loads_worst, shear_loads_worst, bending_moments_worst,
                                printout_table, format_output_3dig, format_output_str, format_output_int)

    # Create charts
    # TODO fix the ylimits of the excel charts
    chart_ax = excel_create_chart("Axial_Load_Data", "Distribution of axial load along the rocket",
                                  "Distance from Stage 1 nozzle exit plane [m]", "Section Axial Load [kN]", L_launcher,
                                  workbook, [[x, y*1e-3] for x, y in axial_loads_worst])
    wkst5.set_chart(chart_ax)

    chart_shear = excel_create_chart("Shear_Load_Data", "Distribution of shear load along the rocket",
                                     "Distance from Stage 1 nozzle exit plane [m]", "Section Shear Load [kN]",
                                     L_launcher, workbook, [[x, y*1e-3] for x, y in shear_loads_worst])
    wkst6.set_chart(chart_shear)

    chart_bend = excel_create_chart("Bending_Mom_Data", "Distribution of bending moment along the rocket",
                                    "Distance from Stage 1 nozzle exit plane [m]", "Section Bending Moment [kNm]",
                                    L_launcher, workbook, [[x, y*1e-3] for x, y in bending_moments_worst])
    wkst7.set_chart(chart_bend)

    chart_mos = excel_create_chart("Margin_of_Safety_Data", "Distribution of margin of safety along the rocket",
                                   "Distance from Stage 1 nozzle exit plane [m]", "Margin of Safety", L_launcher,
                                   workbook, margins_of_safety_worst)
    wkst10.set_chart(chart_mos)

    workbook.close()


def is_valid_number(value, name):
    if math.isnan(value) or math.isinf(value):
        print(f"Invalid number encountered for {name}: {value}")
        return False
    return True

# loadCaseGenerator(1.075)
