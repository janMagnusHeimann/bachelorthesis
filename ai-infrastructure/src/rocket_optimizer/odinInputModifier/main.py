def update_section_data(lines, start_marker, end_marker, key_col_name, value_col_name, target_name, new_value):
    # Find the start and end of the data section
    section_start = None
    section_end = None
    for i, line in enumerate(lines):
        if start_marker in line:
            section_start = i
        elif end_marker in line:
            section_end = i
            break

    if section_start is not None and section_end is not None:
        # Extract and clean the header to ensure column names are matched correctly
        header = lines[section_start + 1].strip().split(';')
        header = [h.strip() for h in header]  # Strip any extraneous whitespace from headers

        key_col_index = header.index(key_col_name)
        value_col_index = header.index(value_col_name)

        # Process each line in the section to update the required value
        for i in range(section_start + 2, section_end):  # Start from the next line after the header
            columns = lines[i].strip().split(';')
            columns = [c.strip() for c in columns]  # Clean each column entry

            if columns[key_col_index] == target_name:
                old_value = columns[value_col_index]
                # Adjust the new value to match the old value's length
                new_value_formatted = str(new_value).ljust(len(old_value))
                columns[value_col_index] = new_value_formatted
                lines[i] = '; '.join(columns) + '\n'  # Rebuild the line with updated value


def odinInputModifier(file_path, component_name, new_length, pint_name, new_pint):
    with open(file_path, 'r+') as file:
        lines = file.readlines()

        update_section_data(lines, 'Component start', 'Component end', 'name', 'L', component_name, new_length)
        update_section_data(lines, 'Load start', 'Load end', 'name', 'Pint', pint_name, new_pint)

        # Rewrite the file with the updated lines
        file.seek(0)
        file.writelines(lines)
        file.truncate()


def odinInputModifier_flux(file_path, component_name, new_length, pint_name, new_pint):
    with open(file_path, 'r+') as file:
        lines = file.readlines()

        update_section_data(lines, 'Component start', 'Component end', 'name', 'L', component_name, new_length)
        update_section_data(lines, 'Load start', 'Load end', 'name', 'Flux', pint_name, new_pint)

        # Rewrite the file with the updated lines
        file.seek(0)
        file.writelines(lines)
        file.truncate()


def odinInputModifier2(filename):
    component_columns = [
        ["ID", "name", "type",
         "Mode", "Stiff", "StiffGeo", "Mat", "Load1/L2/../LX", "R", "L", "Dim3", "Dim4", "Dim5", "msf"],
        ["1", "Fairing_ellipt", "bulkhead",
         "1", "1", "1", "1", "3", "1050.0", "1500.0", "0.000", "90.000", "0.0", "1.03"],
        ["2", "Fairing_cyl", "cylinder",
         "1", "1", "2", "1", "7", "1050.0", "2500.0", "0.000", "0.000", "0.0", "1.18"],
        # Add more rows as needed
    ]

    stiffening_geometry_columns = [
        ["ID", "name", "t", "Dim1", "Dim2", "Dim3", "Dim4", "Dim5", "Dim6", "Dim7", "Dim8", "Tol"],
        ["1", "Fairing_ellipt", "0.5", "1.5", "50.0", "0.0", "0.0", "0", "0", "0", "0", "0.2"],
        ["2", "Fairing_cyl", "0.5", "1.5", "50.0", "0.0", "0.0", "0", "0", "0", "0", "0.2"],
        # Add more rows as needed
    ]

    material_columns = [
        ["ID", "name", "Rp02", "Rm", "E", "G", "nu", "dens"],
        ["1", "CFK_1", "754.1", "754.1", "73548.0", "28701.0", "0.3", "1.600E-6"],
        ["2", "Al2219_RT", "352.0", "441.0", "70000.0", "26923.1", "0.3", "2.835e-6"],
        # Add more rows as needed
    ]

    load_columns = [
        ["ID", "name", "Pint", "Pext", "Flux", "Temp", "FOSYield", "FOSUlt", "FOSlB", "FOSgB", "MatID"],
        ["3", "Outer_p_fairing", "0.5", "0.13252", "1.0", "60.0", "1.25", "1.250", "1.500", "1.310", "-1"],
        ["4", "Flux_S3", "0.5", "0.13252", "1.0", "270.0", "1.25", "1.250", "1.500", "1.310", "-1"],
        # Add more rows as needed
    ]

    stagecollector_columns = [
        ["ID", "Name", "CompID", "Orientation", "ParentID", "IFchild", "IFparent", "VolD1/.../VolDX", "Size", "N"],
        ["4", "All", "1", "1", "-1", "0", "0", "0", "100.0", "90"],
        ["4", "All", "2", "1", "1", "2", "1", "0", "200.0", "90"],
        # Add more rows as needed
    ]

    with open(filename, 'w') as file:
        file.write("// Written on: Thu May 02 10:19:31 CEST 2024\n\n")

        write_table_section(file, "Component Section", "Component start", component_columns)
        write_table_section(file, "Stiffening Geometry Section", "StiffGeo start", stiffening_geometry_columns)
        write_table_section(file, "Material Section", "Material start", material_columns)
        write_table_section(file, "Load Section", "Load start", load_columns)
        write_table_section(file, "Stagecollector", "Collector start", stagecollector_columns)


def write_table_section(file, section_name, section_start, columns):
    file.write(f"{section_name}\n")
    file.write(f"{section_start}\n")
    column_headers = columns.pop(0)
    file.write("// " + " ".join([f"{header:>15}" for header in column_headers]) + "\n")

    for row in zip(*columns):
        file.write(" ".join([f"{value:>15}" for value in row]) + "\n")
    file.write(f"{section_name.split()[0]} end\n\n")
