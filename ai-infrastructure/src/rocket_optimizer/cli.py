import typer
import os
import shutil
from pathlib import Path
from typing import Annotated, Optional

from rocket_optimizer.astosOutputReader import astosOutputReader
from rocket_optimizer.optimizingLoop import optimizingLoop
from rocket_optimizer.optimizingLoop_neadmead import optimizingLoop_neadmead
from rocket_optimizer.costCalculation import costCalculation
from rocket_optimizer.pdf import pdf
from rocket_optimizer.plot import plot
from rocket_optimizer.create_csv import create_csv
from rocket_optimizer.DynamicDatabase import AstosOutput
from rocket_optimizer.update_material_values_fixed_position import update_mat_values_in_file
from rocket_optimizer.odinOutToAstosIn import odinOutToAstosIn
from rocket_optimizer.Astos import Astos

AstosOutput.stage1_tank_pressure = 7
AstosOutput.stage2_tank_pressure = 7

app = typer.Typer()

# epsilon = 0.001  # residuum for entire loop

# TODO: add update of safety margin calculation based on material (input_template excel)


@app.command()
def main(
    max_iter: Annotated[Optional[int], typer.Argument(help="Maximum number of iterations")] = 1,
    # default value for max_iter
    nominal_gtp_path: Annotated[
        Optional[Path],
        typer.Option(
            "-g",
            "--gtp-file",
            exists=True,
            file_okay=True,
            readable=True,
            resolve_path=True,
            help="Path to ASTOS nominal .gtp"
        )
    ] = Path("./.astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/"),
    material_stage1: Annotated[
        Optional[str],
        typer.Option("--material-s1", help="Stage 1 tank material, options are: Steel, Al, CFK")
    ] = "CFK",
    material_stage2: Annotated[
        Optional[str],
        typer.Option("--material-s2", help="Stage 1 tank material, options are: Steel, Al, CFK")
    ] = "CFK",
    material_stage3: Annotated[
        Optional[str],
        typer.Option("--material-s3", help="Stage 1 tank material, options are: Steel, Al, CFK")
    ] = "CFK",
    material_interstage1: Annotated[
        Optional[str],
        typer.Option("--material-is1", help="Interstage 1 material, options are: Steel, Al, CFK")
    ] = "CFK",
    material_interstage2: Annotated[
        Optional[str],
        typer.Option("--material-is2", help="Interstage 2 material, options are: Steel, Al, CFK")
    ] = "CFK",
    # output_path:  # TODO: store gtps in the S: drive
    # fast_mode: Annotated[
    #     Optional[bool],
    #     typer.Option(
    #         "--fast-mode",
    #         help="Run the program in fast mode by choosing small epsilon and max_iter values.",
    #     ),
    # ] = False,
):
    # Update Odin input file with material
    material_codes = {
        "Steel": "SS",
        "CFK": "CC",
        "Al": "AL"
    }

    input_directory = os.path.join(".input")  # Moves up one level to the parent directory
    AstosOutput.odin_input_path = (
        f"config_S1{material_codes[material_stage1]}" +
        f"_S2{material_codes[material_stage2]}_S3{material_codes[material_stage3]}"
        f"_IS1{material_codes[material_interstage1]}_IS2{material_codes[material_interstage2]}"
    )
    files = os.listdir(input_directory)
    txt_files = [f for f in files if f.endswith('.txt') and os.path.isfile(
        os.path.join(input_directory, f))]  # Assumption: .input contains only one .txt file!
    os.rename(f".input/{txt_files[0]}", ".input/" + AstosOutput.odin_input_path + ".txt")

    AstosOutput.odin_input_path = f".input/{AstosOutput.odin_input_path}.txt"
    update_mat_values_in_file(
        AstosOutput.odin_input_path, material_stage1, material_stage2,
        material_stage3, material_interstage1, material_interstage2)

    # Update dynamic database with materials
    AstosOutput.s1_tank_material = material_stage1
    AstosOutput.s2_tank_material = material_stage2
    AstosOutput.s3_tank_material = material_stage3
    AstosOutput.interstage1_material = material_interstage1
    AstosOutput.interstage2_material = material_interstage2

    # Check maximum iterations
    if max_iter is not None:
        if max_iter <= 0:
            typer.echo("Error: max_iter must be a positive integer.")
            raise typer.Exit(code=1)
        else:
            print(f"Maximum iterations set to: {max_iter}")
    else:
        print("Using default maximum iterations.")

    # Define output folder
    out_fold = './Images_Out/'
    if not os.path.exists(out_fold):
        os.makedirs(out_fold)

    """
    This is the main function that calls all the other functions to optimize the rocket.
    """

    # TODO: move code below into other file(line 128 - 149)
    scenario_name = [file for file in os.listdir(nominal_gtp_path) if file.endswith(".gtp")]

    if len(scenario_name) > 1:
        print("Found more than 1 nominal gtp file. Make sure you remove all the gtp files you don't want to optimize.\n"
              f"Optimizing {scenario_name[0]}...")
    scenario_name = scenario_name[0]
    print(scenario_name)

    # Cold start
    input_path = ".astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/inFiles"
    if os.path.isdir(input_path):
        shutil.rmtree(input_path)
        os.mkdir(input_path)
    nominal_homotopy_path = os.path.join(nominal_gtp_path, scenario_name, "batch", "homotopy.xml")
    initial_homotopy_path = os.path.join(input_path, "homotopy_0.xml")
    shutil.copyfile(nominal_homotopy_path, initial_homotopy_path)

    output_path = ".astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/outFiles"
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
        os.mkdir(output_path)
    nominal_gtp_path = os.path.join(nominal_gtp_path, scenario_name)
    initial_gtp_path = os.path.join(output_path, "0_" + scenario_name)
    shutil.copytree(nominal_gtp_path, initial_gtp_path)
    alphas = []
    for i in range(max_iter):

        if i < 3:
            astosOutputReader(output_path, i)
            odinOutToAstosIn(i)
            optimizingLoop(i)
            costCalculation(out_fold,
                            material_stage1,
                            material_stage2,
                            material_stage3,
                            material_interstage1,
                            material_interstage2, i)

            Astos()
            alphas.append(AstosOutput.price_per_kg)

        else:
            print("alphas: ", alphas)
            optimizingLoop_neadmead(i, alphas)

    '''
    now as the loop is finished, we can calculate the costs and create the plots/csv files
    '''
    costCalculation(out_fold,
                    material_stage1,
                    material_stage2,
                    material_stage3,
                    material_interstage1,
                    material_interstage2,
                    i)
    create_csv(out_fold)
    plot(out_fold, max_iter)
    pdf(out_fold, i, material_stage1, material_stage2, material_stage3, material_interstage1, material_interstage2)
