import pandas as pd
from rocket_optimizer.DynamicDatabase import AstosOutput, DatabaseOutput, Masses, Results


def loadCaseInputGenerator(i):

    # Load the Excel file
    file_path = "./.loadCaseData/input_template.xlsx"
    excel_data = pd.ExcelFile(file_path)

    # Load and update the 'General' sheet
    df_general = excel_data.parse("General")
    column_b_name = df_general.columns[1]
    column_d_name = df_general.columns[3]

    # Mapping for 'General' sheet
    mapping_general = {
        "q_alpha": AstosOutput.q_alpha,
        "L_n_core": AstosOutput.length_conical_section,
        "omega_core": AstosOutput.nosecone_semivertex_angle,
        "D": AstosOutput.rocket_diameter,
        "L_s1": AstosOutput.stage1_length,
        "L_s2": AstosOutput.stage2_length,
        "L_s3": AstosOutput.stage3_length,
        "L_f": AstosOutput.fairing_length,
        "GP": AstosOutput.d_n_gimbal_point,
        "L_s1_blk_bot": AstosOutput.d_n_stage1_bottom_tank_head,
        "L_s1_blk_mid": AstosOutput.d_n_stage1_bulkhead,
        "L_s1_blk_top": AstosOutput.d_n_stage1_top_tank_head,
        "L_s2_blk_bot": AstosOutput.d_n_stage2_bottom_tank_head,
        "L_s2_blk_mid": AstosOutput.d_n_stage2_bulkhead,
        "L_s2_blk_top": AstosOutput.d_n_stage2_top_tank_head,
        "m_s1_bot": AstosOutput.tlo_stage1_bottom_tank,
        "m_s1_top": AstosOutput.tlo_stage1_top_tank,
        "m_s2_bot": AstosOutput.tlo_stage2_bottom_tank,
        "m_s2_top": AstosOutput.tlo_stage2_top_tank,
        "p_s1": AstosOutput.stage1_tank_pressure,
        "p_s2": AstosOutput.stage2_tank_pressure,
        "n_b": DatabaseOutput.number_boosters,
        "m_b": DatabaseOutput.mass_boster,
        "CoG_b": DatabaseOutput.cog_booster,
        "T_b": DatabaseOutput.thrust_booster,
        "D_b": DatabaseOutput.booster_diameter,
        "L_b": DatabaseOutput.booster_length,
        "L_n_b": DatabaseOutput.booster_cone_length,
        "omega_b": DatabaseOutput.booster_nosecone_vertexangle,
        "x_fwd": DatabaseOutput.booster_forward_attach_point,
        "x_aft": DatabaseOutput.booster_aft_attach_point,
        "alt_min": AstosOutput.altitude_at_condition_min,
        "alt_nom": AstosOutput.altitude_at_condition_nominal,
        "alt_max": AstosOutput.altitude_at_condition_max,
        "machNo_min": AstosOutput.mach_at_condition_min,
        "machNo_nom": AstosOutput.mach_at_condition_nominal,
        "machNo_max": AstosOutput.mach_at_condition_max,
        "t_maxQ_min": AstosOutput.time_to_maxQ_min,
        "t_maxQ_nom": AstosOutput.time_to_maxQ_nominal,
        "t_maxQ_max": AstosOutput.time_to_maxQ_max,
        "t_S1burn": AstosOutput.stage1_burntime,
    }

    # Update 'General' sheet
    for idx, row in df_general.iterrows():
        column_b_value = row[column_b_name]
        if column_b_value in mapping_general:
            df_general.at[idx, column_d_name] = mapping_general[column_b_value]

    # Load and update the 'Inert mass' sheet
    df_inert_mass = excel_data.parse("Inert Mass")
    # inert_mass_a_name = df_inert_mass.columns[0]
    # inert_mass_b_name = df_inert_mass.columns[1]
    column_c_name = df_inert_mass.columns[2]

    # Mapping for 'Inert mass' sheet
    mapping_inert_mass = {
        'Stage 1 Common Main Stage Engine, Design "E02", Staged Combustion Engine': [
            Masses.mass_stage1_common_main_stage,
            AstosOutput.d_n_stage1_common_main_stage,
        ],
        "Stage 1 First Stage Thrust Frame Module": [
            Masses.mass_stage1_thrust_module,
            AstosOutput.d_n_stage1_thrust_module,
        ],
        "Unaccounted mass":
            [Masses.mass_unaccounted,
             AstosOutput.d_n_unaccounted_S1
        ],
        "Stage 1 Unburnt RP1": [
            Masses.mass_stage1_unburned_RP1,
            AstosOutput.d_n_stage1_unburned_RP1
        ],
        "Stage 1 Unburnt LOX": [
            Masses.mass_stage1_unburned_LOX
            , AstosOutput.d_n_stage1_unburned_LOX
        ],
        "Stage 1 Tank System Main Propellants/Cryogens": [
            Masses.mass_stage1_tank_system,
            AstosOutput.d_n_stage1_tank_system,
        ],
        "Stage 1 Gas Pressurization and Vent System": [
            Masses.mass_stage1_pressurization,
            AstosOutput.d_n_stage1_pressurization,
        ],
        "S2-Propulsion System": [
            Masses.mass_stage2_propulsion_system,
            AstosOutput.d_n_stage2_propulsion_system
        ],
        "Stage 2 Reaction Control System": [
            Masses.mass_stage2_reaction_control_system,
            AstosOutput.d_n_stage2_reaction_control_system,
        ],
        "Stage 2 Propellant Loading and Distribution System ": [
            Masses.mass_stage2_prop_distribution_system,
            AstosOutput.d_n_stage2_prop_distribution_system,
        ],
        "Stage 2 Gas Pressurization and Vent System": [
            Masses.mass_stage2_pressurization,
            AstosOutput.d_n_stage2_pressurization,
        ],
        "Stage 2 Unburnt RP1": [
            Masses.mass_stage2_unburned_RP1,
            AstosOutput.d_n_stage2_unburned_RP1
        ],
        "Stage 2 Unburnt LOX": [
            Masses.mass_stage2_unburned_LOX,
            AstosOutput.d_n_stage2_unburned_LOX
        ],
        "Stage 2 Tank System Main Propellants/Cryogens": [
            Masses.mass_stage2_tank_system,
            AstosOutput.d_n_stage2_tank_system,
        ],
        "Stage 3 Dry mass": [
            Masses.mass_stage3_dry,
            AstosOutput.d_n_S3_dry
        ],
        "Stage 3 Propellant": [
            Masses.mass_stage3_prop,
            AstosOutput.d_n_S3_prop
        ],
        "Payload": [
            Masses.mass_payload,
            AstosOutput.d_n_payload
        ],
        "Fairing": [
            Masses.mass_fairing,
            AstosOutput.d_n_fairing
        ],
    }

    # Update 'Inert mass' sheet
    for idx, row in df_inert_mass.iterrows():
        column_c_value = row[column_c_name]
        if column_c_value in mapping_inert_mass:
            df_inert_mass.at[idx, df_inert_mass.columns[0]] = mapping_inert_mass[column_c_value][1]
            df_inert_mass.at[idx, df_inert_mass.columns[1]] = mapping_inert_mass[column_c_value][0]

    # Load and update 'Printout Locations'
    df_Printout_Locations = excel_data.parse("Printout Locations")
    column_d_name_Printout_Locations = df_Printout_Locations.columns[0]

    # Mapping for 'Printout Locations'
    mapping_Printout_Locations = {
        "A": AstosOutput.d_n_stage1_bottom_tank_head,
        "B": AstosOutput.d_n_stage1_bulkhead,
        "C": AstosOutput.d_n_stage1__stage2_interstage_bottom,
        "D": AstosOutput.d_n_stage1_top_tank_head,
        "E": AstosOutput.d_n_stage1__stage2_interstage_flange,
        "F": AstosOutput.d_n_stage2_bottom_tank_head,
        "G": AstosOutput.d_n_stage2_bulkhead,
        "H": AstosOutput.d_n_stage2_top_tank_head,
        "I": AstosOutput.d_n_stage2__fairing_interstage_flange,
    }

    # Update 'Printout Locations'
    for idx, row in df_Printout_Locations.iterrows():
        current_label = row[df_Printout_Locations.columns[1]]
        if current_label in mapping_Printout_Locations:
            df_Printout_Locations.at[idx, df_Printout_Locations.columns[0]] = mapping_Printout_Locations[current_label]

    df_Rocket_Configuration = excel_data.parse("Rocket Configuration")
    if i > 0:
        sections_mapping = {
            0: [
                AstosOutput.s1_tank_material,
                Results.get_value_at("wall_thickness_s1_lox_cylinder", i - 1),
                AstosOutput.stage1_tank_pressure - 1,
            ],
            AstosOutput.d_n_stage1__stage2_interstage_bottom: [
                AstosOutput.interstage1_material,
                Results.get_value_at("s1_interstage_thickness", i - 1),
                0,
            ],
            AstosOutput.d_n_stage1__stage2_interstage_flange: [
                AstosOutput.s2_tank_material,
                Results.get_value_at("wall_thickness_s2_lox_cylinder", i - 1),
                AstosOutput.stage2_tank_pressure - 1,
            ],
            AstosOutput.d_n_stage2__fairing_interstage_bottom: [
                AstosOutput.interstage2_material,
                Results.get_value_at("s2_interstage_thickness", i - 1),
                0,
            ],
            # AstosOutput.d_n_stage2__fairing_interstage_flange: [AstosOutput.s3_tank_material, Results.get_value_at("wall_thickness_s3_lox_cylinder", i - 1)],
        }  # TODO: add differenciation between LOX and RP1 tanks and tank bulkheads/domes
    else:
        sections_mapping = {
            0: [
                AstosOutput.s1_tank_material,
                1,
                AstosOutput.stage1_tank_pressure - 1,
            ],
            AstosOutput.d_n_stage1__stage2_interstage_bottom: [
                AstosOutput.interstage1_material,
                1,
                0,
            ],
            AstosOutput.d_n_stage1__stage2_interstage_flange: [
                AstosOutput.s2_tank_material,
                1,
                AstosOutput.stage2_tank_pressure - 1,
            ],
            AstosOutput.d_n_stage2__fairing_interstage_bottom: [
                AstosOutput.interstage2_material,
                1,
                0,
            ],
            # AstosOutput.d_n_stage2__fairing_interstage_flange: [AstosOutput.s3_tank_material, 1],
        }  # TODO: add differenciation between LOX and RP1 tanks and tank bulkheads/domes

    # Update 'Rocket Configuration'
    for idx, row in df_Rocket_Configuration.iterrows():
        current_position = list(sections_mapping.keys())[idx]
        current_material = sections_mapping[current_position][0]
        current_thickness = sections_mapping[current_position][1]
        current_pressure = sections_mapping[current_position][2]
        current_properties = DatabaseOutput().materials[current_material]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[0]] = current_position
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[1]] = 1075  # TODO: add when adding modifiable radius
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[2]] = current_thickness
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[3]] = current_pressure
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[4]] = current_properties["MorC"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[5]] = current_properties["Young's modulus"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[6]] = current_properties["Young's modulus"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[7]] = current_properties["Young's modulus"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[8]] = current_properties["Poisson's ratio"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[9]] = current_properties["Poisson's ratio"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[10]] = current_properties["Poisson's ratio"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[11]] = current_properties["Shear modulus"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[12]] = current_properties["Shear modulus"]
        df_Rocket_Configuration.at[idx, df_Rocket_Configuration.columns[13]] = current_properties["Shear modulus"]

    # Load the original sheets that are not updated
    sheets_to_preserve = {
        sheet: excel_data.parse(sheet)
        for sheet in excel_data.sheet_names
        if sheet not in ["General", "Inert Mass", "Printout Locations", "Rocket Configuration"]
    }

    # Save the updated DataFrames back to the Excel file
    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        df_general.to_excel(writer, sheet_name="General", index=False)
        df_inert_mass.to_excel(writer, sheet_name="Inert Mass", index=False)
        df_Printout_Locations.to_excel(writer, sheet_name="Printout Locations", index=False)
        df_Rocket_Configuration.to_excel(writer, sheet_name="Rocket Configuration", index=False)

        # Write back the preserved sheets
        for sheet_name, df in sheets_to_preserve.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # TODO: add update of Rocket Configuration sheet


if __name__ == "__main__":
    print("Columns updated successfully.")
    loadCaseInputGenerator()
