import numpy as np
import pandas as pd
import os
from tqdm import tqdm
import natsort
from ambiance import Atmosphere
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


def loadCaseGenerator2(main_path):

    # paths
    # main_path = os.getcwd()  # find current location
    # main_path = (
    #     r"S:\PROJECT_MANAGEMENT\Mission_analysis\students\05_Jan"
    #     r"\RFA_One"
    # )
    print(main_path)

    # gtp files
    def find_gtp_files_in_subdirs(parent_directory):
        gtp_files = []  # List to hold the paths of .gtp files
        for item in os.listdir(parent_directory):
            # Construct the full path
            item_path = os.path.join(parent_directory, item)
            print(item_path)
            if os.path.isdir(item_path):  # Check if it's a directory
                # List the contents and filter for .gtp files
                gtp_files_in_subdir = [
                    os.path.join(item_path, file)
                    for file in os.listdir(item_path)
                    if file.endswith(".gtp")
                ]
                gtp_files.extend(gtp_files_in_subdir)  # Add them to the list
        return natsort.natsorted(gtp_files)  # Optionally, sort the files

    gtp_files = find_gtp_files_in_subdirs(main_path)
    print(gtp_files)
    main_dirs_filter = natsort.natsorted(gtp_files)

    folder_count_2 = 0  # type: int
    for items in main_dirs_filter:
        folder_count_2 += 1  # increment counter

    print("There are {} main folders".format(folder_count_2))
    print(main_dirs_filter)

    export_path = "exports"
    model_path = "model\\astos"

    # function to extract data from gtp files
    def extract_gtp(n, column_name: str):
        # path to output files
        some_path_end = "{}\\{}".format(main_dirs_filter[n], export_path)
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

    def extract_structural_mass(file_path, stage_id):
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Define the namespace if necessary
        ns = {'asto': 'http://www.astos.de/schema/astos/9.10/scenario'}

        # Find the Component with the specified ID
        stage = root.find(
            f".//asto:Component[asto:ID='{stage_id}']", ns)
        if stage is None:
            return None  # Return None if the stage is not found

        # Extract Total Mass value
        total_mass_value = float(
            stage.find(".//asto:Total_Mass/asto:Value", ns).text)

        return total_mass_value

    def find_dimensions_by_id(file_path, component_id, debug=False):
        with open(file_path, 'r') as file:
            xml_data = file.read()

        root = ET.fromstring(xml_data)

        namespaces = {'ns0': 'http://www.astos.de/schema/astos/9.10/scenario'}

        # Try to find the Component with the given ID, considering namespaces
        component = root.find(f".//ns0:Component[ns0:ID='{component_id}']",
                              namespaces)

        if component is not None:
            dimensions = component.find(".//ns0:Auxiliary/ns0:Dimensions",
                                        namespaces)

            if dimensions is not None:
                x_value = float(dimensions.find(
                    "ns0:X/ns0:Value", namespaces).text)
                x_unit = dimensions.find("ns0:X/ns0:Unit", namespaces).text
                y_value = float(dimensions.find(
                    "ns0:Y/ns0:Value", namespaces).text)
                y_unit = dimensions.find("ns0:Y/ns0:Unit", namespaces).text
                return (x_value, x_unit), (y_value, y_unit)
            else:
                return ("Dimensions not found",
                        ""), ("Dimensions not found", "")
        else:
            return ("Component not found", ""), ("Component not found", "")

    def find_mass_and_x_dimension_by_id(file_path, component_id, debug=False):
        with open(file_path, 'r') as file:
            xml_data = file.read()

        root = ET.fromstring(xml_data)
        namespaces = {'ns0': 'http://www.astos.de/schema/astos/9.10/scenario'}
        component = root.find(f".//ns0:Component[ns0:ID='{component_id}']",
                              namespaces)

        # Debug output if enabled
        if debug:
            print(f"Component found: {ET.tostring(component)}"
                  if component is not None else "Component not found")

        # If the Component is found,
        # search for the Total Mass and X Dimension considering namespaces
        if component is not None:
            total_mass = component.find(".//ns0:Auxiliary/ns0:Total_Mass",
                                        namespaces)
            dimensions = component.find(
                ".//ns0:Auxiliary/ns0:Dimensions/ns0:X", namespaces)

            mass_value = (float(total_mass.find("ns0:Value", namespaces).text)
                          if total_mass is not None else None)
            mass_unit = (total_mass.find("ns0:Unit", namespaces).text
                         if total_mass is not None else None)
            x_value = (float(dimensions.find("ns0:Value", namespaces).text)
                       if dimensions is not None else None)
            x_unit = (dimensions.find("ns0:Unit", namespaces).text
                      if dimensions is not None else None)

            return (mass_value, mass_unit), (x_value, x_unit)
        else:
            return (None, None), (None, None)

    def extract_engine_values(file_path, engine_id):
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Define the namespace
        ns = {'asto': 'http://www.astos.de/schema/astos/9.10/scenario'}

        # Find the Actuator with the specified ID
        engine = root.find(f".//asto:Actuator[asto:ID='{engine_id}']", ns)
        if engine is None:
            return None, None  # Return None if the engine is not found

        # Extract Vacuum Thrust value
        vacuum_thrust_value = float(
            engine.find(".//asto:Vacuum_Thrust/asto:Value/asto:Value",
                        ns).text)

        # Extract Engine Mass to Thrust Ratio value
        mass_thrust_ratio_value = float(
            engine.find(".//asto:Engine_Mass_to_Thrust_Ratio/asto:Value",
                        ns).text)

        return vacuum_thrust_value, mass_thrust_ratio_value

    # initilazed values
    maxQ = 0
    maxExternalPressure = 0

    # values based on RFA One
    fuel_density = 1100.98  # kg/m^3
    engine_s1_height = 1.8  # m
    # s2_interstage_height = 3  # m
    # tank_s1_height = 26  # m
    # tank_s2_height = 2.34  # m
    # tank_s3_height = 0.6  # m
    # tank_radius = 2.155  # m
    # %%
    for n in tqdm(range(0, folder_count_2)):

        # check amount of stages

        # Dictionary to hold variable names and corresponding query strings
        queries = {
            "burn_time_S1": "burn_time~Engine_1",
            "burn_time_S2": "burn_time~Engine_2",
            "burn_time_S3": "burn_time~Engine_3",
            "vx_j": "vx~Rocket#J2000@Earth",
            "vy_j": "vy~Rocket#J2000@Earth",
            "vz_j": "vz~Rocket#J2000@Earth",
            "acc": "acceleration_without_gravity~Rocket",
            "altitude": "atmos_density~Rocket",
            "dens": "atmos_density~Rocket",
            "prop_mass_S1": "PROP_MASS~Stage_1",
            "prop_mass_S2": "PROP_MASS~Stage_2",
            "prop_mass_S3": "PROP_MASS~Stage_3",
        }

        # Loop through the dictionary to assign results to variables
        results = {key: extract_gtp(n,
                                    value) for key, value in queries.items()}

        # You can now access the results via the results dictionary,
        # like results['burn_time_S1']

        filename = '{}\\{}'.format(main_dirs_filter[n], model_path)
        xml_filename = 'Model_Data.xml'
        full_path33 = '{}\\{}'.format(filename, xml_filename)

        (tank_s1_height, tank_s1_height_unit), (
            tank_s1_radius, tank_s1_radius_unit) = find_dimensions_by_id(
            full_path33, 'Inert_Mass_Stage_1', debug=True)

        (tank_s2_height, tank_s2_height_unit), (
            tank_s2_radius, tank_s2_radius_unit) = find_dimensions_by_id(
            full_path33, 'Inert_Mass_Stage_2', debug=True)

        (tank_s3_height, tank_s3_height_unit), (
            tank_s3_radius, tank_s3_radius_unit) = find_dimensions_by_id(
            full_path33, 'Inert_Mass_Stage_3', debug=True)
        (fairing_mass, fairing_mass_unit), (
            fairing_heigth, fairing_heigth_unit
            ) = find_mass_and_x_dimension_by_id(
                full_path33, 'Fairing', debug=True)

        vacuum_thrust_1, mass_thrust_ratio_1 = extract_engine_values(
            full_path33, 'Engine_1_Linear')

        vacuum_thrust_2, mass_thrust_ratio_2 = extract_engine_values(
            full_path33, 'Engine_2_Linear')

        vacuum_thrust_3, mass_thrust_ratio_3 = extract_engine_values(
            full_path33, 'Engine_3_Linear')

        structural_mass_1 = extract_structural_mass(
            full_path33, 'Inert_Mass_Stage_1')
        structural_mass_2 = extract_structural_mass(
            full_path33, 'Inert_Mass_Stage_2')
        structural_mass_3 = extract_structural_mass(
            full_path33, 'Inert_Mass_Stage_3')

        stage_s1_drymass = (
            mass_thrust_ratio_1 * vacuum_thrust_1 + structural_mass_1)
        stage_s2_drymass = (
            mass_thrust_ratio_2 * vacuum_thrust_2 + structural_mass_2)
        stage_s3_drymass = (
            mass_thrust_ratio_3 * vacuum_thrust_3 + structural_mass_3)

        # calc max q and max external pressure
        for i, value in enumerate(results["dens"][:-1]):
            if results["altitude"][i+3] < 80:

                v_tot = np.sqrt(
                    (results["vx_j"][i+3] * 1000) ** 2
                    + (results["vy_j"][i+3] * 1000) ** 2
                    + (results["vz_j"][i+3] * 1000) ** 2
                )

                cur_q = 0.5 * v_tot**2 * results["dens"][i+3]

                current = Atmosphere(results["altitude"][i+3] * 1000)

                currentPressure = current.pressure

                cur_externalPressure = cur_q + currentPressure

                if cur_q > maxQ:
                    maxQ = cur_q

                if cur_externalPressure > maxExternalPressure:
                    maxExternalPressure = cur_externalPressure

        # calc CoG
        # prop_s1_max = results["prop_mass_S1"].max()
        prop_s2_max = results["prop_mass_S2"].max()
        prop_s3_max = results["prop_mass_S3"].max()

        s2_max_weight = prop_s2_max + stage_s2_drymass
        s3_max_weight = prop_s3_max + stage_s3_drymass

        current_fuel_CoG_s1 = np.zeros(len(results["prop_mass_S1"]))
        stage1_CoG = np.zeros(len(results["prop_mass_S1"]))
        current_fuel_CoG_s2 = np.zeros(len(results["prop_mass_S2"]))
        stage2_CoG = np.zeros(len(results["prop_mass_S2"]))
        current_fuel_CoG_s3 = np.zeros(len(results["prop_mass_S3"]))
        stage3_CoG = np.zeros(len(results["prop_mass_S3"]))

        # mass of rocket withouth fuel in tank 1
        mass1 = (stage_s1_drymass + s2_max_weight +
                 s3_max_weight)

        # center of gravity withouth fuel in tank 1
        CoG1 = (s2_max_weight * (tank_s2_height/2 + tank_s1_height) +
                s3_max_weight * (tank_s3_height/2 +
                                 tank_s1_height + tank_s2_height)
                + tank_s1_height/2 * stage_s1_drymass) / (
                stage_s1_drymass + s2_max_weight + s3_max_weight
                        )

        # mass of rocket withouth fuel in tank 2 after MECO stage 1
        mass2 = (stage_s2_drymass + s3_max_weight)

        # center of gravity withouth fuel in tank 2 after MECO stage 1
        CoG2 = (s3_max_weight * (tank_s3_height/2 +
                                 tank_s1_height + tank_s2_height)
                + (tank_s2_height/2 + tank_s1_height) * stage_s2_drymass) / (
                stage_s2_drymass + s3_max_weight
                        )

        for i in range(len(results["prop_mass_S1"])):

            # stage 1
            if results["prop_mass_S1"][i+3] != 0:

                # current_fuel_CoG_s1[i] = (((results["prop_mass_S1"][i+3]
                #                           / fuel_density)
                #                           / (np.pi * tank_s1_radius ** 2))
                #                           / 2) + engine_s1_height

                # Calculate the volume of the fuel based on its mass and dens
                volume = results["prop_mass_S1"][i+3] / fuel_density

                print("Volume: ")
                print(volume)

                # Calculate the area of the circular tank base.
                area = np.pi * tank_s1_radius ** 2

                print("Area: ")
                print(area)

                # Calculate the fuel height in the tank by
                # dividing the volume by the area and then by 2.
                # (This assumes that you're considering the fuel
                # to only fill half the tank's height for some reason.)
                fuel_height = (volume / area) / 2

                print("Fuel height: ")
                print(fuel_height)

                # Finally, add the engine height to the fuel height
                # to get the current fuel CoG.
                current_fuel_CoG_s1[i] = fuel_height + engine_s1_height

                print("Current fuel CoG: ")
                print(current_fuel_CoG_s1[i])

                stage1_CoG[i] = ((results["prop_mass_S1"][i+3]
                                 * current_fuel_CoG_s1[i] + mass1 * CoG1) /
                                 (results["prop_mass_S1"][i+3] + mass1))
                print("Stage 1 CoG: ")
                print(stage1_CoG[i])

            else:
                stage1_CoG[i] = 0

            # stage 2
            if results["prop_mass_S2"][i+3] != 0:

                current_fuel_CoG_s2[i] = ((results["prop_mass_S2"][i+3]
                                          / fuel_density)
                                          / (np.pi * tank_s2_radius ** 2)
                                          / 2) + tank_s1_height
                print("Current fuel CoG: ")
                print(current_fuel_CoG_s2[i])

                stage2_CoG[i] = ((results["prop_mass_S2"][i+3]
                                 * current_fuel_CoG_s2[i]) +
                                 mass2 * CoG2) / (
                                 results["prop_mass_S2"][i+3] + mass2)
                print("Stage 2 CoG: ")
                print(stage2_CoG[i])
            else:
                stage2_CoG[i] = 0

            # stage 3
            if results["prop_mass_S3"][i+3] != 0:

                current_fuel_CoG_s3[i] = ((((results["prop_mass_S3"][i+3]
                                          / fuel_density)
                                          / np.pi * tank_s3_radius ** 2))
                                          / 2
                                          ) + tank_s1_height + tank_s2_height
                print("Current fuel CoG: ")
                print(current_fuel_CoG_s3[i])

                stage3_CoG[i] = ((results["prop_mass_S3"][i+3]
                                  * current_fuel_CoG_s3[i]) +
                                 stage_s3_drymass * (tank_s3_height/2 +
                                 tank_s1_height + tank_s2_height)) / (
                                  results["prop_mass_S3"][i+3] +
                                  stage_s3_drymass)
                print("Stage 3 CoG: ")
                print(stage3_CoG[i])
            else:
                stage3_CoG[i] = 0

    def plot_multiple_arrays(*arrays):
        # Number of entries (assuming all arrays have the same length)
        n = len(arrays[0])

        # Create an x-axis with integers representing time steps
        time_steps = np.arange(n)

        # Create the plot
        plt.figure(figsize=(10, 6))

        # Colors for the lines
        colors = ['blue', 'green', 'red', 'purple',
                  'orange', 'black', 'brown', 'magenta', 'cyan', 'yellow']

        # Plot each array, filtering out zero values
        for idx, array in enumerate(arrays):
            # Filter to include only non-zero values
            nonzero_indices = array != 0
            filtered_time_steps = time_steps[nonzero_indices]
            filtered_array = array[nonzero_indices]

            plt.plot(filtered_time_steps, filtered_array, label=f'Array {
                idx+1}',
                    color=colors[idx % len(colors)])

        plt.xlabel('Time')
        plt.ylabel('Values')
        plt.title('Multiple Arrays Over Time (Non-zero values)')
        plt.legend()
        plt.xticks(rotation=45)  # Optional: Adjust if necessary
        plt.tight_layout()  # Adjust layout to prevent cut-off
        plt.show()

    plot_multiple_arrays(stage1_CoG, stage2_CoG, stage3_CoG)
