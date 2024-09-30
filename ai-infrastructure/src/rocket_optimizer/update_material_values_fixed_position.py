def update_mat_values_in_file(filename, material_stage1, material_stage2, material_stage3, material_interstage1,
                              material_interstage2):
    in_component_section = False
    updated_lines = []

    # Define a mapping of component names to their respective new material values
    material_updates = {
        'Stage1': material_stage1,
        'Stage2': material_stage2,
        'Stage3': material_stage3,
        'Interstage1': material_interstage1,
        'Interstage2': material_interstage2
    }

    change_parts_map = {
        'S1_fdDome': "Stage1",
        'S1_cylinder': "Stage1",
        'S1_aftDome': "Stage1",
        'S1_cylinder_2': "Stage1",
        'S1_bulkhead': "Stage1",
        'S2_fdDome': "Stage2",
        'S2_cylinder': "Stage2",
        'S2_aftDome': "Stage2",
        'S2_cylinder_2': "Stage2",
        'S2_bulkhead': "Stage2",
        'S3_fdDome': "Stage3",
        'S3_aftDome': "Stage3",
        'S3_lowerCyl': "Stage3",
        'S3_commonBulk': "Stage3",
        'S1_Interstage': "Interstage1",
        'S2_Interstage': "Interstage2"
    }

    # Define the column index for the 'Mat' column and expected widths for each column
    mat_column_index = 6  # Mat is the 7th column
    column_widths = [16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17]

    with open(filename, 'r') as file:
        lines = file.readlines()

        for j, line in enumerate(lines):
            stripped_line = line.strip()
            leading_whitespace = line[:len(line) - len(stripped_line) - 1]

            # Check for the start of the component section
            if "Component start" in stripped_line:
                in_component_section = True
                updated_lines.append(line)  # Keep the original line
                continue

            # Check for the end of the component section
            if "Component end" in stripped_line:
                in_component_section = False
                updated_lines.append(line)  # Keep the original line
                continue

            # If we are inside the component section
            if in_component_section and ";" in line:
                # Split the line by semicolons to get the individual fields
                fields = line.split(';')
                # fields = [f.strip() for f in line.split(';')]
                parts_name = fields[1].strip()

                if parts_name in change_parts_map:
                    stage_name = change_parts_map[parts_name]
                    material_value = material_updates.get(stage_name)

                    # Switch-case logic to determine the value for the Mat column
                    if material_value == "Steel":
                        modified_line = line[:114] + '100' + line[117:]
                    elif material_value == "CFK":
                        modified_line = line[:114] + '  1' + line[117:]
                    elif material_value == "Al":
                        modified_line = line[:114] + '  2' + line[117:]
                    else:
                        # Handle unknown material values
                        print(f"Warning: Unrecognized material value for {parts_name}.")

                    # Add the final field without the extra semicolon
                    lines[j] = modified_line

    # Write the updated content back to the file
    with open(filename, 'w') as file:
        file.writelines(lines)
