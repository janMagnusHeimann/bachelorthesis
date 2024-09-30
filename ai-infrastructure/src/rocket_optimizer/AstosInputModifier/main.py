import os
import re
import shutil
import xml.etree.ElementTree as ET


def AstosInputModifier(input1, input2, folder_path='.'):
    """
    Copies the homotopy XML file with the highest index, increments the index for the new file,
    and updates the existing float values in the new file with the provided inputs, removing
    namespace prefixes in the output.

    Parameters:
    - input1 (float): The first float value to insert into the XML file.
    - input2 (float): The second float value to insert into the XML file.
    - folder_path (str): The path to the folder containing homotopy XML files. Defaults to the current directory.

    Returns:
    - None
    """
    # Find all homotopy files in the given folder
    homotopy_files = []
    for filename in os.listdir(folder_path):
        match = re.match(r'homotopy_(\d+)\.xml$', filename)
        if match:
            index = int(match.group(1))
            homotopy_files.append((index, filename))

    if not homotopy_files:
        print("No homotopy files found in the folder.")
        return

    # Find the homotopy file with the highest index
    highest_index, highest_file = max(homotopy_files, key=lambda x: x[0])
    new_index = highest_index + 1
    new_file = f'homotopy_{new_index}.xml'
    highest_file_path = os.path.join(folder_path, highest_file)
    new_file_path = os.path.join(folder_path, new_file)

    # Copy the highest index file to the new file
    shutil.copy2(highest_file_path, new_file_path)
    print(f"Copied {highest_file} to {new_file}")

    # Parse the new XML file
    tree = ET.parse(new_file_path)
    root = tree.getroot()

    # Define the namespace used in your XML file
    namespace = 'http://www.astos.de/schema/astos/9.10/scenario'

    # Register the default namespace to remove 'ns0' prefix in the output
    ET.register_namespace('', namespace)

    # Update the existing float values in the XML
    # Use the namespace in element tags directly
    variable_tag = f'{{{namespace}}}Variable'

    # Find the Variable elements with the specific name attributes
    float_value1_element = root.find(f'.//{variable_tag}[@name="S1_dry_prop_ratio"]')
    float_value2_element = root.find(f'.//{variable_tag}[@name="S2_dry_prop_ratio"]')

    if float_value1_element is not None:
        old_value1 = float_value1_element.text
        float_value1_element.text = str(input1)
        print(f"Updated '{float_value1_element.attrib['name']}' from {old_value1} to {input1}")
    else:
        print("Variable with name 'S1_dry_prop_ratio' not found in the XML.")

    if float_value2_element is not None:
        old_value2 = float_value2_element.text
        float_value2_element.text = str(input2)
        print(f"Updated '{float_value2_element.attrib['name']}' from {old_value2} to {input2}")
    else:
        print("Variable with name 'S2_dry_prop_ratio' not found in the XML.")

    # Write back the updated XML to the new file
    tree.write(new_file_path, encoding='UTF-8', xml_declaration=True)

    print(f"Successfully updated {new_file} with new float values.")


# Example usage
if __name__ == "__main__":
    # Set the base directory where the folders are located
    base_directory = "./.astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/inFiles/"

    # Define the new values for the homotopy file
    new_s1_value = 0.045  # Replace with your desired value
    new_s2_value = 0.035  # Replace with your desired value

    # Call the function to update homotopy files
    AstosInputModifier(new_s1_value, new_s2_value, base_directory)
