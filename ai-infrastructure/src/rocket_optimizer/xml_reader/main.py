import os
import xml.etree.ElementTree as ET
import numpy as np


# Function to read the homotopy.xml files in the last three folders
def xml_reader():

    # Path to the base directory
    base_dir = "./.astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/outFiles/"

    # Step 1: List and sort the folders by modification time
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    folders_sorted = sorted(folders, key=lambda x: os.path.getmtime(os.path.join(base_dir, x)), reverse=True)

    # Step 2: Check if there are at least 3 folders
    if len(folders_sorted) < 3:
        print("Warning: Less than 3 folders found. Exiting.")
        exit()

    # Get the last three folders
    last_three_folders = folders_sorted[:3]

    # Variables to hold the values
    s1_values = []
    s2_values = []

    # Step 3: Parse the homotopy.xml file in each folder and extract floating point values
    for folder in last_three_folders:
        # Construct the path to the batch folder
        batch_folder = os.path.join(base_dir, folder, 'batch')
        homotopy_path = os.path.join(batch_folder, 'homotopy.xml')

        if os.path.exists(homotopy_path):
            print(f"Parsing XML in folder: {folder}")

            tree = ET.parse(homotopy_path)
            root = tree.getroot()

            # Define the namespace to avoid issues
            ns = {'astos': 'http://www.astos.de/schema/astos/9.10/scenario'}

            # Extract the floating point values
            for variable in root.findall("astos:Variable", ns):
                name = variable.attrib['name']
                value = float(variable.text.strip())

                if name == "S1_dry_prop_ratio":
                    s1_values.append(value)
                elif name == "S2_dry_prop_ratio":
                    s2_values.append(value)
                print(f"Variable: {name}, Value: {value}")
        else:
            print(f"homotopy.xml not found in {folder}/batch")

    print("s1_values: ", s1_values)
    print("s2_values: ", s2_values)

    return np.array([s1_values, s2_values])


# test usage:
if __name__ == "__main__":

    try:
        simplex = xml_reader()
        print("Simplex: ", simplex)
    except ValueError as e:
        print(e)
