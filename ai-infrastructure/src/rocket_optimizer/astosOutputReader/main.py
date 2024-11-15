import os
import natsort
import numpy as np
import pandas as pd
# import xml.etree.ElementTree as ET

from rocket_optimizer.DynamicDatabase import AstosOutput
from rocket_optimizer.DynamicDatabase import DatabaseOutput


# function to extract data from gtp files
def extract_gtp(gtp_file, column_name: str):
    # path to output files
    some_path_end = "{}\\{}".format(gtp_file, 'exports')
    subdirs = os.listdir(some_path_end)
    subdirs_filter = [item for item in subdirs if item.count(".txt") > 0]

    # path to count case folders
    full_path = "{}\\{}".format(some_path_end, subdirs_filter[0])

    # reading file and make float values
    df = np.array(
        pd.read_csv(
            full_path,
            sep="\t",
            header=None,
            low_memory=False,
            encoding="unicode_escape",
        )
    )  # dtype = object

    df[3:, :] = df[3:, :].astype("float64")

    df_total_dataframe = pd.DataFrame(df[:, :])
    column_idx = None
    for col in df_total_dataframe:
        if column_name in df_total_dataframe[col][0]:
            column_idx = col
            break
    if column_idx is None:
        raise Exception(f"Column '{column_name}' not found")

    column_data = df_total_dataframe[column_idx][3:].astype("float64")
    return column_data


def find_gtp_files_in_dir(directory):
    # List the contents of the directory and filter for .gtp files
    gtp_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".gtp")]
    return natsort.natsorted(gtp_files)  # Optionally, sort the files


def find_lowest_nonzero(arr):
    # Filter out zero values
    non_zero_values = [value for value in arr if value != 0]
    # Check if there are any non-zero values left
    if not non_zero_values:
        return None  # or any other value indicating no non-zero values

    # Find the minimum value of the non-zero values
    lowest_nonzero = min(non_zero_values)

    return lowest_nonzero


def astosOutputReader(main_path, n=-1):

    aoa = 10
    safety_factor_bending_loads = 1.2  # this safety_factor decreases wall thickness (counterintuitive)

    # Function to find .gtp files in a single .gpt directory

    gtp_files = find_gtp_files_in_dir(main_path)

    if not gtp_files:
        print("No .gtp files found")
        return

    # model_path = "model\\astos"

    # filename = os.path.join(gtp_files[n], model_path)
    # xml_filename = 'Model_Data.xml'
    # full_path = os.path.join(filename, xml_filename)

    # .txt file

    queries = {
        "burn_time_S1": "burn_time~Engine_1",
        "burn_time_S2": "burn_time~Engine_2",
        "burn_time_S3": "burn_time~Engine_3",
        "vx_j": "vx~Rocket#J2000@Earth",
        "vy_j": "vy~Rocket#J2000@Earth",
        "vz_j": "vz~Rocket#J2000@Earth",
        "acc": "acceleration_without_gravity~Rocket",
        "altitude": "altitude~Rocket",
        "dens": "atmos_density~Rocket",
        "prop_mass_S1": "PROP_MASS~Stage1_LinearDesign:Rocket",
        "prop_mass_S2": "PROP_MASS~Stage2_LinearDesign:Rocket",
        "prop_mass_S3": "PROP_MASS~Stage3_BasicVehicleStage:Rocket",
        "mach_number": "mach",
        "dynamic_pressure": "dynamic_pressure~Rocket",
        "thrust": "thrust~Engine_1:Rocket",
        "vacuum_thrust_1": "thrust_vacuum~Engine_1:Rocket",
        "vacuum_thrust_2": "thrust_vacuum~Engine_2:Rocket",
        "vacuum_thrust_3": "thrust_vacuum~Engine_3:Rocket",
        "vacuum_isp_s1": "isp_vacuum~Engine_1:Rocket",
        "vacuum_isp_s2": "isp_vacuum~Engine_2:Rocket",
        "vacuum_isp_s3": "isp_vacuum~Engine_3:Rocket",
        "engine_nozzle_exit_area_S1": "nozzle_area~Engine_1:Rocket",
        "engine_nozzle_exit_area_S2": "nozzle_area~Engine_2:Rocket",
        "engine_nozzle_exit_area_S3": "nozzle_area~Engine_3:Rocket",
        "total_mass_rocket": "mass_total~Rocket",
        "nozzle_exit_area_S1": "nozzle_area~Engine_1:Rocket",
        "nozzle_exit_area_S2": "nozzle_area~Engine_2:Rocket",
    }

    # Loop through the dictionary to assign results to variables
    results = {key: extract_gtp(gtp_files[n], value) for key, value in queries.items()}

    # You can now access the results via the results dictionary,

    fuel_mass_S1 = results['prop_mass_S1'].max()
    fuel_mass_S2 = results['prop_mass_S2'].max()
    fuel_mass_S3 = results['prop_mass_S3'].max()
    # dynamicPressure = results
    maxQ = max(results['dynamic_pressure'])
    altitude = results["altitude"]
    mach_number = results["mach_number"]
    s1_burntime = results["burn_time_S1"]

    AstosOutput.engine_sealevel_thrust = results['thrust'][4]
    AstosOutput.engine_vacuum_thrust_s1 = results['vacuum_thrust_1'].max()
    AstosOutput.engine_vacuum_thrust_s2 = results['vacuum_thrust_2'].max()
    AstosOutput.engine_vacuum_isp_s1 = results['vacuum_isp_s1'].max()
    AstosOutput.engine_vacuum_isp_s2 = results['vacuum_isp_s2'].max()
    AstosOutput.engine_nozzle_area_s1 = results['nozzle_exit_area_S1'].max()
    AstosOutput.engine_nozzle_area_s2 = results['nozzle_exit_area_S2'].max()

    AstosOutput.payload_mass = min(results['total_mass_rocket'])*1e3 - DatabaseOutput.s3_dry_mass

    AstosOutput.residual_prop_s1 = find_lowest_nonzero(results['prop_mass_S1'])
    AstosOutput.residual_prop_s2 = find_lowest_nonzero(results['prop_mass_S2'])
    AstosOutput.residual_prop_s3 = find_lowest_nonzero(results['prop_mass_S3'])
    AstosOutput.vacuum_isp_s1 = results["vacuum_isp_s1"].max()
    AstosOutput.vacuum_isp_s2 = results["vacuum_isp_s2"].max()
    AstosOutput.vacuum_isp_s3 = results["vacuum_isp_s3"].max()
    AstosOutput.vacuum_thrust_s1 = results["vacuum_thrust_1"].max()
    AstosOutput.vacuum_thrust_s2 = results["vacuum_thrust_2"].max()
    AstosOutput.vacuum_thrust_s3 = results["vacuum_thrust_3"].max()

    AstosOutput.engine_nozzle_exit_s1 = results["engine_nozzle_exit_area_S1"].max()
    AstosOutput.engine_nozzle_exit_s2 = results["engine_nozzle_exit_area_S2"].max()
    AstosOutput.engine_nozzle_exit_s3 = results["engine_nozzle_exit_area_S3"].max()

    # AstosOutput.sealevel_thrust_s1 = results['thrust'][4]
    AstosOutput.thrust = results['thrust'][4]

    burn_time_S1 = -1
    for i in range(1, len(results['burn_time_S1'])):
        if results['burn_time_S1'][i+3] == 0:
            burn_time_S1 = results['burn_time_S1'][i+2]
            break

    # # .xml files
    # def extract_structural_mass(file_path, stage_id):
    #     # Parse the XML file
    #     tree = ET.parse(file_path)
    #     root = tree.getroot()
    #
    #     # Define the namespace if necessary
    #     ns = {'asto': 'http://www.astos.de/schema/astos/9.10/scenario'}
    #
    #     # Find the Component with the specified ID
    #     stage = root.find(
    #         f".//asto:Component[asto:ID='{stage_id}']", ns)
    #     if stage is None:
    #         return None  # Return None if the stage is not found
    #
    #     # Extract Total Mass value
    #     total_mass_value = float(
    #         stage.find(".//asto:Total_Mass/asto:Value", ns).text)
    #
    #     return total_mass_value
    #
    # def find_dimensions_by_id(file_path, component_id, debug=False):
    #     with open(file_path, 'r') as file:
    #         xml_data = file.read()
    #
    #     root = ET.fromstring(xml_data)
    #
    #     namespaces = {'ns0': 'http://www.astos.de/schema/astos/9.10/scenario'}
    #
    #     # Try to find the Component with the given ID, considering namespaces
    #     component = root.find(f".//ns0:Component[ns0:ID='{component_id}']",
    #                           namespaces)
    #
    #     if component is not None:
    #         dimensions = component.find(".//ns0:Auxiliary/ns0:Dimensions",
    #                                     namespaces)
    #
    #         if dimensions is not None:
    #             x_value = float(dimensions.find(
    #                 "ns0:X/ns0:Value", namespaces).text)
    #             x_unit = dimensions.find("ns0:X/ns0:Unit", namespaces).text
    #             y_value = float(dimensions.find(
    #                 "ns0:Y/ns0:Value", namespaces).text)
    #             y_unit = dimensions.find("ns0:Y/ns0:Unit", namespaces).text
    #             return (x_value, x_unit), (y_value, y_unit)
    #         else:
    #             return ("Dimensions not found",
    #                     ""), ("Dimensions not found", "")
    #     else:
    #         return ("Component not found", ""), ("Component not found", "")
    #
    # def find_mass_and_x_dimension_by_id(file_path, component_id, debug=False):
    #     with open(file_path, 'r') as file:
    #         xml_data = file.read()
    #
    #     root = ET.fromstring(xml_data)
    #     namespaces = {'ns0': 'http://www.astos.de/schema/astos/9.10/scenario'}
    #     component = root.find(f".//ns0:Component[ns0:ID='{component_id}']",
    #                           namespaces)
    #
    #     # Debug output if enabled
    #     if debug:
    #         print(f"Component found: {ET.tostring(component)}"
    #               if component is not None else "Component not found")
    #
    #     # If the Component is found,
    #     # search for the Total Mass and X Dimension considering namespaces
    #     if component is not None:
    #         total_mass = component.find(".//ns0:Auxiliary/ns0:Total_Mass",
    #                                     namespaces)
    #         dimensions = component.find(
    #             ".//ns0:Auxiliary/ns0:Dimensions/ns0:X", namespaces)
    #
    #         mass_value = (float(total_mass.find("ns0:Value", namespaces).text)
    #                       if total_mass is not None else None)
    #         mass_unit = (total_mass.find("ns0:Unit", namespaces).text
    #                      if total_mass is not None else None)
    #         x_value = (float(dimensions.find("ns0:Value", namespaces).text)
    #                    if dimensions is not None else None)
    #         x_unit = (dimensions.find("ns0:Unit", namespaces).text
    #                   if dimensions is not None else None)
    #
    #         return (mass_value, mass_unit), (x_value, x_unit)
    #     else:
    #         return (None, None), (None, None)

    # def extract_engine_values(file_path, engine_id):
    #     # Parse the XML file
    #     tree = ET.parse(file_path)
    #     root = tree.getroot()
    #
    #     # Define the namespace
    #     ns = {'asto': 'http://www.astos.de/schema/astos/9.10/scenario'}
    #
    #     # Find the Actuator with the specified ID
    #     engine = root.find(f".//asto:Actuator[asto:ID='{engine_id}']", ns)
    #     if engine is None:
    #         return None, None  # Return None if the engine is not found
    #
    #     # Extract Vacuum Thrust value
    #     vacuum_thrust_value = float(
    #         engine.find(".//asto:Vacuum_Thrust/asto:Value/asto:Value",
    #                     ns).text)
    #
    #     # Extract Engine Mass to Thrust Ratio value
    #     mass_thrust_ratio_value = float(
    #         engine.find(".//asto:Engine_Mass_to_Thrust_Ratio/asto:Value",
    #                     ns).text)
    #
    #     return vacuum_thrust_value, mass_thrust_ratio_value
    #
    # vacuum_thrust_1, mass_thrust_ratio_1 = extract_engine_values(
    #         full_path, 'Engine_1_Linear')
    #
    # vacuum_thrust_2, mass_thrust_ratio_2 = extract_engine_values(
    #         full_path, 'Engine_2_Linear')
    #
    # vacuum_thrust_3, mass_thrust_ratio_3 = extract_engine_values(
    #         full_path, 'Engine_3_Linear')

    AstosOutput.rocket_diameter = 2.15  # TODO
    AstosOutput.fairing_length = 4.3  # TODO: hardcoded, take length from gtp or homotopy
    AstosOutput.length_conical_section = 2.9
    AstosOutput.nosecone_semivertex_angle = 20.46
    AstosOutput.stage1_burntime = burn_time_S1
    AstosOutput.q_alpha = (maxQ/1000) * aoa * safety_factor_bending_loads

    i_maxQ = np.array(results['dynamic_pressure']).argmax()  # TODO: add liftoff, MECO, SECO, etc.

    AstosOutput.altitude_at_condition_min = altitude[i_maxQ]
    AstosOutput.altitude_at_condition_nominal = altitude[i_maxQ]
    AstosOutput.altitude_at_condition_max = altitude[i_maxQ]

    AstosOutput.mach_at_condition_min = mach_number[i_maxQ]
    AstosOutput.mach_at_condition_nominal = mach_number[i_maxQ]
    AstosOutput.mach_at_condition_max = mach_number[i_maxQ]

    AstosOutput.time_to_maxQ_min = s1_burntime[i_maxQ]
    AstosOutput.time_to_maxQ_nominal = s1_burntime[i_maxQ]
    AstosOutput.time_to_maxQ_max = s1_burntime[i_maxQ]

    AstosOutput.thrust = max(results['thrust'])

    print(f"Mach at condition: {AstosOutput.mach_at_condition_nominal}")
    print(f"maxQ in Pa: {maxQ} Pa")
    print(f"Angle of attack: {aoa} °")
    print(f"maxQ alpha: {AstosOutput.q_alpha} kPa°")
    print(f"thrust: {AstosOutput.thrust} kN")

    # AstosOutput.mass_stage3_dry = structural_mass_3
    # AstosOutput.mass_fairing = fairing_mass

    print(f"fuel_mass_S1: {fuel_mass_S1} kg")
    print(f"fuel_mass_S2: {fuel_mass_S2} kg")
    print(f"fuel_mass_S3: {fuel_mass_S3} kg")
    AstosOutput.mass_stage1_prop = fuel_mass_S1
    AstosOutput.mass_stage2_prop = fuel_mass_S2
    AstosOutput.mass_stage3_prop = fuel_mass_S3
