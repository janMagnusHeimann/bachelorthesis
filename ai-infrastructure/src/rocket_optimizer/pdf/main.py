import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from rocket_optimizer.DynamicDatabase import AstosOutput, DatabaseOutput, Results


def pdf(fold, i, material_stage1, material_stage2, material_stage3, material_interstage1, material_interstage2):
    # Helper function to format floats to two decimal places

    # Mapping of materials to labels
    material_mapping = {
        "CFK": "CC",
        "Al": "Al",
        "Steel": "SS"
    }

    # Get the corresponding labels for each stage
    label_stage1 = material_mapping[material_stage1]
    label_stage2 = material_mapping[material_stage2]
    label_stage3 = material_mapping[material_stage3]
    label_interstage1 = material_mapping[material_interstage1]
    label_interstage2 = material_mapping[material_interstage2]

    # Format the column name dynamically
    column_name = (
        f"S1:{label_stage1}, S2:{label_stage2}, S3:{label_stage3}, "
        f"IS1:{label_interstage1}, IS2:{label_interstage2}"
    )

    def format_float_zero_digit(value):
        return f"{value:.0f}" if isinstance(value, float) else value

    def format_float_one_digit(value):
        return f"{value:.1f}" if isinstance(value, float) else value

    def format_float_two_digit(value):
        return f"{value:.2f}" if isinstance(value, float) else value

    def format_float_three_digit(value):
        return f"{value:.3f}" if isinstance(value, float) else value

    def format_float_four_digit(value):
        return f"{value:.4f}" if isinstance(value, float) else value

    # Create the data for the table
    data = {
        "Parameter": [
            "STAGE 1",
            "stage length [m]",
            "dry mass [kg]",
            "filled propellant [kg]",
            "unuseable propellant [kg]",
            "vacuum Isp [s]",
            "vacuum thrust [kN]",
            "sea level thrust at takeoff [kN]",
            "engine nozzle exit area [m^2]",
            "wall thickness [mm]",
            "sigma [-]",
            "tank pressure [bara]",
            "interstage mass [kg]",
            "interstage thickness [mm]",
            "STAGE 2",
            "stage length [m]",
            "dry mass [kg]",
            "filled propellant [kg]",
            "unuseable propellant [kg]",
            "vacuum Isp [s]",
            "vacuum thrust [kN]",
            "engine nozzle exit area [m^2]",
            "wall thickness [mm]",
            "sigma [-]",
            "tank pressure [bara]",
            "interstage mass [kg]",
            "interstage thickness [mm]",
            "STAGE 3",
            "stage length [m]",
            "fairing length [m]",
            "dry mass [kg]",
            "filled propellant [kg]",
            "unusable propellant [kg]",
            "vacuum Isp [s]",
            "vacuum thrust [kN]",
            "engine nozzle exit area [m^2]",
            "aspect ratio whole rocket [-]",
            "payload mass [kg]",
        ],
        column_name: [
            "STAGE 1",
            format_float_one_digit(Results.get_value_at("complete_length_s1", i - 1)),
            format_float_zero_digit(AstosOutput.S1_total_dry_mass),
            format_float_zero_digit(AstosOutput.mass_stage1_prop),
            format_float_zero_digit(AstosOutput.residual_prop_s1),
            format_float_zero_digit(AstosOutput.vacuum_isp_s1),
            format_float_zero_digit(AstosOutput.vacuum_thrust_s1),
            format_float_zero_digit(AstosOutput.engine_sealevel_thrust),
            format_float_two_digit(AstosOutput.engine_nozzle_exit_s1),
            format_float_two_digit(Results.get_value_at("wall_thickness_s1_lox_cylinder", i - 1)),
            format_float_four_digit(Results.get_value_at("s1_sigma", i - 1)),
            format_float_one_digit(AstosOutput.stage1_tank_pressure),
            format_float_zero_digit(Results.get_value_at("s1_interstage_mass", i - 1)),
            format_float_one_digit(Results.get_value_at("s1_interstage_thickness", i - 1)),
            "STAGE 2",
            format_float_one_digit(Results.get_value_at("complete_length_s2", i - 1)),
            format_float_zero_digit(AstosOutput.S2_total_dry_mass),
            format_float_zero_digit(AstosOutput.mass_stage2_prop),
            format_float_zero_digit(AstosOutput.residual_prop_s2),
            format_float_zero_digit(AstosOutput.vacuum_isp_s2),
            format_float_zero_digit(AstosOutput.vacuum_thrust_s2),
            format_float_two_digit(AstosOutput.engine_nozzle_exit_s2),
            format_float_two_digit(Results.get_value_at("wall_thickness_s2_lox_cylinder", i - 1)),
            format_float_four_digit(Results.get_value_at("s2_sigma", i - 1)),
            format_float_one_digit(AstosOutput.stage2_tank_pressure),
            format_float_zero_digit(Results.get_value_at("s2_interstage_mass", i - 1)),
            format_float_one_digit(Results.get_value_at("s2_interstage_thickness", i - 1)),
            "STAGE 3",
            format_float_one_digit(AstosOutput.stage3_length),
            format_float_one_digit(AstosOutput.fairing_length),
            format_float_zero_digit(DatabaseOutput.s3_dry_mass),
            format_float_zero_digit(AstosOutput.mass_stage3_prop),
            format_float_zero_digit(AstosOutput.residual_prop_s3),
            format_float_zero_digit(AstosOutput.vacuum_isp_s3),
            format_float_one_digit(AstosOutput.vacuum_thrust_s3),
            format_float_three_digit(AstosOutput.engine_nozzle_exit_s3),
            format_float_one_digit(Results.get_value_at("aspect_ratio", i - 1)),
            format_float_two_digit(AstosOutput.payload_mass),
        ],
    }

    # Convert the data to a DataFrame
    df = pd.DataFrame(data)

    # Create a PDF file and a plot for the table
    pdf_path = fold + "/Rocket_Parameters.pdf"
    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(12, 8))  # Create a figure for the table

        # Hide the axes
        ax.axis("tight")
        ax.axis("off")

        # Create the table
        table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center")

        # Colorize specific rows
        row_colors = {
            0: "lightblue",  # (STAGE 1 header)
            14: "lightblue",  # (STAGE 2 header)
            27: "lightblue",  # (STAGE 3 header)
        }
        for row, color in row_colors.items():
            for col_idx in range(len(df.columns)):
                cell = table[(row + 1, col_idx)]
                cell.set_facecolor(color)

        # Adjust the table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)

        # Save the figure to the PDF
        pdf.savefig(fig)

    # Display the path to the PDF file
    print(f"The PDF has been saved to: {pdf_path}")


# Example usage:
if __name__ == "__main__":
    pass
    # try:
    #     pdf()
    # except ValueError as e:
    #     print(e)
