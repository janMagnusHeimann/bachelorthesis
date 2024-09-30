import re
from rocket_optimizer.DynamicDatabase import Results


def odinOutInterstage():

    filename = r".\.output_interstage_only\odin_out.txt"
    # Open the file and read its content
    with open(filename, 'r') as file:
        content = file.read()

    # Create a dictionary to store the results for both s1 and s2 interstages
    results = {}

    # Search for s1_interstage and s2_interstage blocks using specific patterns
    # Using non-greedy matching to capture the relevant data for each interstage
    s1_interstage_section = re.search(r'(Name=s1_interstage[\s\S]+?)(?=Name=|$)', content)
    s2_interstage_section = re.search(r'(Name=s2_interstage[\s\S]+?)(?=Name=|$)', content)

    # Helper function to extract wall thickness and mass from a section
    def extract_values(section):
        wall_thickness_match = re.search(r'wall thickness t=([0-9.]+)', section)
        mass_match = re.search(r'Mass=([0-9.]+)', section)
        if wall_thickness_match and mass_match:
            wall_thickness = float(wall_thickness_match.group(1))
            mass = float(mass_match.group(1))
            return wall_thickness, mass
        return None, None

    # Extract data for s1_interstage if the section is found
    if s1_interstage_section:
        s1_wall_thickness, s1_mass = extract_values(s1_interstage_section.group(0))
        results['s1_interstage'] = {'wall_thickness': s1_wall_thickness, 'mass': s1_mass}

    # Extract data for s2_interstage if the section is found
    if s2_interstage_section:
        s2_wall_thickness, s2_mass = extract_values(s2_interstage_section.group(0))
        results['s2_interstage'] = {'wall_thickness': s2_wall_thickness, 'mass': s2_mass}

    Results.append_value("s1_interstage_thickness", results['s1_interstage']['wall_thickness'])
    Results.append_value("s2_interstage_thickness", results['s2_interstage']['wall_thickness'])
    Results.append_value("s1_interstage_mass", results['s1_interstage']['mass'])
    Results.append_value("s2_interstage_mass", results['s2_interstage']['mass'])


if __name__ == "__main__":
    odinOutInterstage()
    print(Results.get_value_at("s1_interstage_mass", -1))
    print(Results.get_value_at("s2_interstage_mass", -1))
    print(Results.get_value_at("s1_interstage_thickness", -1))
    print(Results.get_value_at("s2_interstage_thickness", -1))
