from lxml import etree as ET
import os
import re
from rocket_optimizer.DynamicDatabase import Results
from rocket_optimizer.DynamicDatabase import AstosOutput
from rocket_optimizer.DynamicDatabase import DatabaseOutput

# Define the namespace
# ET.register_namespace('ns', 'http://www.astos.de/schema/astos/9.10/scenario')
# NSMAP = {'ns': 'http://www.astos.de/schema/astos/9.10/scenario'}
ns = {"ns": "http://www.astos.de/schema/astos/9.10/scenario"}


# Function to update the float values
def update_xml_file(file_path: str, updates: dict, new_path: str | None = None):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    for var in root.findall("ns:Variable", ns):
        name = var.get("name")
        if name in updates:
            var.text = str(updates[name])

    # Save the updated XML to a file (can overwrite the original file or save to a new one)
    if not new_path:
        new_path = file_path
    tree.write(new_path, xml_declaration=True, encoding="ISO-8859-1", pretty_print=True)


def get_highest_numbered_file(directory):
    # Regular expression to match files with the core name and an optional number at the end
    pattern = re.compile(r"homotopy_(\d+)\.xml$")

    highest_number = -1
    highest_file = None

    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if match:
            number = int(match.group(1))
            if number > highest_number:
                highest_number = number
                highest_file = filename

    return highest_file


def calc_prop_ratio(dry_mass, prop_mass):
    return dry_mass / prop_mass


def extract_component_data(filename, component_name):
    # Read the file
    with open(filename, "r") as file:
        data = file.read()
    # Define regex pattern for extracting the entire component section
    component_pattern = re.compile(
        rf"Name={component_name}.*?Units: \[kg\],\[mm\], \[mm\^3\], \[N\], \[Nmm\], \[MPa\], \[%\]", re.DOTALL
    )
    component_data = component_pattern.search(data)
    if component_data:
        component_text = component_data.group()

        # Extract wall thickness for cylinders
        thickness_match = re.search(r"wall thickness t=([\d\.]+)", component_text)
        if not thickness_match:
            # Extract mean wall thickness for domes
            thickness_match = re.search(r"mean wall thickness tmean = ([\d\.]+)", component_text)
        if thickness_match:
            thickness = float(thickness_match.group(1)) + 0.2 # 0.2mm scratch wall thickness margin
        else:
            thickness = None

        # Extract mass
        mass_match = re.search(r"Mass=([\d\.]+)", component_text)
        if mass_match:
            mass = float(mass_match.group(1)) + 0.2/thickness*float(mass_match.group(1)) # scratch wall thickness margin
        else:
            mass = None

        print(f"compenent: {component_name}, mass: {mass}, thickness: {thickness}")
        return mass, thickness
    else:
        return None, None


# Example usage
directory_path = r".\.astos-batch-script\V20_NOM_long_lat_inc_iter\batchmaster\inFiles"
highest_numbered_file = get_highest_numbered_file(directory_path)

if highest_numbered_file:
    print(f"The file with the highest number is: {highest_numbered_file}")
else:
    print("No files matching the pattern were found.")


def odinOutToAstosIn(i):
    # Load the XML content from a file
    file_path = rf".\.astos-batch-script\V20_NOM_long_lat_inc_iter\batchmaster\inFiles\homotopy_{i}.xml"

    filename = r".\.output\odin_out.txt"

    # extract s1 data
    s1_lower_dome_weight, s1_lower_dome_thickness = extract_component_data(filename, "s1_aftdome")
    s1_rp1_cylinder_weight, s1_rp1_cylinder_thickness = extract_component_data(filename, "s1_cylinder")
    s1_lox_cylinder_weight, s1_lox_cylinder_thickness = extract_component_data(filename, "s1_cylinder_2")
    s1_upper_dome_weight, s1_upper_dome_thickness = extract_component_data(filename, "s1_fddome")

    # extract s2 data
    s2_lower_dome_weight, s2_lower_dome_thickness = extract_component_data(filename, "s2_aftdome")
    s2_rp1_cylinder_weight, s2_rp1_cylinder_thickness = extract_component_data(filename, "s2_cylinder")
    s2_lox_cylinder_weight, s2_lox_cylinder_thickness = extract_component_data(filename, "s2_cylinder_2")
    s2_upper_dome_weight, s2_upper_dome_thickness = extract_component_data(filename, "s2_fddome")

    s1_interstage_mass, s1_interstage_thickness = extract_component_data(filename, "s1_interstage")
    s2_interstage_mass, s2_interstage_thickness = extract_component_data(filename, "s2_interstage")

    print(f"s1_interstage_mass: {s1_interstage_mass}")
    print(f"s2_interstage_mass: {s2_interstage_mass}")
    print(f"s1_interstage_thickness: {s1_interstage_thickness}")
    print(f"s2_interstage_thickness: {s2_interstage_thickness}")

    Results.append_value("s1_interstage_mass", s1_interstage_mass)
    Results.append_value("s2_interstage_mass", s2_interstage_mass)

    Results.append_value("s1_interstage_thickness", s1_interstage_thickness)
    Results.append_value("s2_interstage_thickness", s2_interstage_thickness)

    Results.append_value("wall_thickness_s1_aftdome", s1_lower_dome_thickness)
    Results.append_value("wall_thickness_s1_lox_cylinder", s1_lox_cylinder_thickness)
    Results.append_value("wall_thickness_s1_rp1_cylinder", s1_rp1_cylinder_thickness)
    Results.append_value("wall_thickness_s1_fddome", s1_upper_dome_thickness)
    Results.append_value("wall_thickness_s2_aftdome", s2_lower_dome_thickness)
    Results.append_value("wall_thickness_s2_lox_cylinder", s2_lox_cylinder_thickness)
    Results.append_value("wall_thickness_s2_rp1_cylinder", s2_rp1_cylinder_thickness)
    Results.append_value("wall_thickness_s2_fddome", s2_upper_dome_thickness)

    print(f"mass_stage1_prop: {AstosOutput.mass_stage1_prop}")
    print(f"mass_stage2_prop: {AstosOutput.mass_stage2_prop}")

    s1_tank_mass = s1_lower_dome_weight + s1_lox_cylinder_weight + s1_rp1_cylinder_weight + s1_upper_dome_weight
    s2_tank_mass = s2_lower_dome_weight + s2_lox_cylinder_weight + s2_rp1_cylinder_weight + s2_upper_dome_weight

    print(f"s1 inert mass due to vehicle tank module: {s1_tank_mass}")
    print(f" s2 inert mass due to vehicle tank module: {s2_tank_mass}")

    Results.append_value("s1_tank_mass", s1_tank_mass)
    Results.append_value("s2_tank_mass", s2_tank_mass)

    # sigma_s1 = []
    # sigma_s2 = []

    sigma_s1 = float(abs(
        (s1_lower_dome_weight + s1_lox_cylinder_weight + s1_rp1_cylinder_weight + s1_upper_dome_weight)
        / AstosOutput.mass_stage1_prop))

    # sigma_s1.append(sigma_s1_0)

    sigma_s2 = float(abs(
        (s2_lower_dome_weight + s2_lox_cylinder_weight + s2_rp1_cylinder_weight + s2_upper_dome_weight)
        / AstosOutput.mass_stage2_prop))

    # sigma_s1 = float(sigma_s1_0)
    # sigma_s2 = float(sigma_s2_0)

    Results.append_value("s1_sigma", sigma_s1)
    Results.append_value("s2_sigma", sigma_s2)

    updates = {
        "S1_dry_prop_ratio": abs(
            calc_prop_ratio(
                (s1_lower_dome_weight + s1_lox_cylinder_weight + s1_rp1_cylinder_weight + s1_upper_dome_weight),
                AstosOutput.mass_stage1_prop,
            )
        ),
        "S2_dry_prop_ratio": abs(
            calc_prop_ratio(
                (s2_lower_dome_weight + s2_lox_cylinder_weight + s2_rp1_cylinder_weight + s2_upper_dome_weight),
                AstosOutput.mass_stage2_prop,
            )
        ),
    }
    print(updates)

    S1_total_dry_mass = (
                s1_lower_dome_weight + s1_lox_cylinder_weight + s1_rp1_cylinder_weight + s1_upper_dome_weight + s1_interstage_mass + (
                 DatabaseOutput.number_engines * DatabaseOutput.mass_engine_s1 + DatabaseOutput.s1_inert_mass))  #TODO #validated
    S2_total_dry_mass = (
                s2_lower_dome_weight + s2_lox_cylinder_weight + s2_rp1_cylinder_weight + s2_upper_dome_weight + s2_interstage_mass + (
                 DatabaseOutput.number_engines_s2 * DatabaseOutput.mass_engine_s2 + DatabaseOutput.s2_inert_mass))  #TODO #validated

    AstosOutput.S1_total_dry_mass = S1_total_dry_mass
    AstosOutput.S2_total_dry_mass = S2_total_dry_mass

    # Update the batch variables
    updated_file_path = rf".\.astos-batch-script\V20_NOM_long_lat_inc_iter\batchmaster\inFiles\homotopy_{i+1}.xml"
    update_xml_file(file_path, updates, updated_file_path)


if __name__ == "__main__":
    # AstosOutput.rocket_diameter = 2.15
    # AstosOutput.mass_stage1_prop = 100000
    # AstosOutput.mass_stage2_prop = 10000
    odinOutToAstosIn(i=0)
    # Example usage
