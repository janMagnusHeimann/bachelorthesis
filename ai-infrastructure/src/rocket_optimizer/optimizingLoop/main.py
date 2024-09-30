from rocket_optimizer.odin import odin
from rocket_optimizer.odinInputModifier import odinInputModifier
from rocket_optimizer.odinInputModifier import odinInputModifier_flux
from rocket_optimizer.tankLengthGenerator import tankLengthGenerator
from rocket_optimizer.DynamicDatabase import AstosOutput
from rocket_optimizer.DynamicDatabase import Results
from rocket_optimizer.loadCaseInputGenerator import loadCaseInputGenerator
from rocket_optimizer.odinOutToAstosIn import odinOutToAstosIn
from rocket_optimizer.distances_nozzle_exit_plane import distances_nozzle_exit_plane
# from rocket_optimizer.tank_pressure_optimizer import tank_pressure_optimizer
from rocket_optimizer.interstage_calc import interstage_calc
import os


# TODO: remove hardcoded values below
out_fold = './Images_Out/'
if not os.path.exists(out_fold):
    os.makedirs(out_fold)

material_stage1 = "Steel"  # material for stage 1 'Al', 'CFK', 'Steel'
material_stage2 = "Steel"  # material for stage 2 'Al', 'CFK', 'Steel'
material_stage3 = "Steel"  # material for stage 3 'Al', 'CFK', 'Steel'
material_interstage1 = "CFK"  # material for interstage 1 'Al', 'CFK', 'Steel'
material_interstage2 = "CFK"  # material for interstage 2 'Al', 'CFK', 'Steel'


'''
optimizingLoop function is called in the main function to optimize the rocket.
'''


def optimizingLoop(i):
    print(f"i: {i}")

    safety_factor_pressure = 1.6  # this safety factor increases tank wallthickness

    # tank lengths s1 and s2
    s1_tank_length = tankLengthGenerator(AstosOutput.mass_stage1_prop, AstosOutput.rocket_diameter)  # TODO
    s2_tank_length = tankLengthGenerator(AstosOutput.mass_stage2_prop, AstosOutput.rocket_diameter)  # TODO

    s1_complete_length = s1_tank_length + AstosOutput.rocket_diameter * 1.4 + AstosOutput.rocket_diameter * 0.895
    #  TODO: take interstage length from dyn database
    s2_complete_length = s2_tank_length + AstosOutput.rocket_diameter * 0.8 + AstosOutput.rocket_diameter * 0.895
    #  TODO: take interstage length from dyn database

    complete_length = s1_complete_length + s2_complete_length + AstosOutput.fairing_length

    L_D = complete_length / AstosOutput.rocket_diameter

    Results.append_value('complete_length_s1', s1_complete_length)
    Results.append_value('complete_length_s2', s2_complete_length)
    Results.append_value('complete_length', complete_length)
    Results.append_value('aspect_ratio', L_D)

    if s1_tank_length == 0 or s2_tank_length == 0:
        print("Tank length is zero. Exiting...")
        exit()

    Results.append_value('tank_length_s1', s1_tank_length)  # TODO
    Results.append_value('tank_length_s2', s2_tank_length)  # TODO

    AstosOutput.tlo_stage1_bottom_tank = AstosOutput.mass_stage1_prop / (1 + (1 / 2.63))  # TODO
    AstosOutput.tlo_stage1_top_tank = AstosOutput.mass_stage1_prop / (1 + 2.63)  # TODO
    AstosOutput.tlo_stage2_bottom_tank = AstosOutput.mass_stage2_prop / (1 + (1 / 2.63))  # TODO
    AstosOutput.tlo_stage2_top_tank = AstosOutput.mass_stage2_prop / (1 + 2.63)  # TODO

    # # distances to nozzle exit plane
    distances_nozzle_exit_plane(s1_tank_length, s2_tank_length)

    # create load case generator input excel file
    loadCaseInputGenerator()

    # # calculate new p1 and p2 values
    # p_s1, p_s2 = tank_pressure_optimizer(0, 15, 0, 15, 1.2, 100, 1.0e-6)  # 100 iterations hardcoded
    p_s1, p_s2 = 7., 7.
    Results.append_value('p1', p_s1)
    Results.append_value('p2', p_s2)
    # print('\n\n--------PRESSURE CHECK----------')
    # print (p_s1, p_s2, '\n\n')
    # safety factor here is 1.5, prev. 1.2 in order to increase tank wallthickness reasonably

    AstosOutput.stage1_tank_pressure = abs(p_s1)
    AstosOutput.stage2_tank_pressure = abs(p_s2)  # pure assumption that tank pressure of S2 is same as for S1 (TBD)
    # TODO: !DELETE HARCODED! /2, there to make tank pressure and wall thickness more realistic
    # AstosOutput.stage2_tank_pressure = p_s2

    s1_lox_tank_length = (2.63*(810/1091) * s1_tank_length) / (1+2.63*(810/1091))
    s1_rp1_tank_length = s1_tank_length - s1_lox_tank_length

    s2_lox_tank_length = (2.63 * (810 / 1091) * s2_tank_length) / (1 + 2.63 * (810 / 1091))
    s2_rp1_tank_length = s2_tank_length - s2_lox_tank_length

    s1_interstage_length = 1.4 * AstosOutput.rocket_diameter  # TODO
    s2_interstage_length = 0.7 * AstosOutput.rocket_diameter  # TODO

    Results.append_value('interstage_length_s1', s1_interstage_length)  # TODO
    Results.append_value('interstage_length_s2', s2_interstage_length)  # TODO

    odinInputModifier(AstosOutput.odin_input_path, 's1_cylinder', str(
        s1_rp1_tank_length), 'S1_LOXtank', str(
        (AstosOutput.stage1_tank_pressure * safety_factor_pressure) / 10))
    odinInputModifier(AstosOutput.odin_input_path, 's1_cylinder_2', str(
        s1_lox_tank_length), 'S1_Rp1tank', str(
        (AstosOutput.stage1_tank_pressure * safety_factor_pressure) / 10))
    odinInputModifier(AstosOutput.odin_input_path, 's2_cylinder', str(
        s2_rp1_tank_length), 'S2_LOXtank', str(
        (AstosOutput.stage2_tank_pressure * safety_factor_pressure) / 10))
    odinInputModifier(AstosOutput.odin_input_path, 's2_cylinder_2', str(
        s2_lox_tank_length), 'S2_LOXtank', str(
        (AstosOutput.stage2_tank_pressure * safety_factor_pressure) / 10))

    interstage_calc()

    odinInputModifier_flux(AstosOutput.odin_input_path, 'S1_interstage', str(
        s1_interstage_length), 'Flux_interstage_S1', str(
          AstosOutput.interstage1_flux))
    odinInputModifier_flux(AstosOutput.odin_input_path, 'S2_interstage', str(
        s2_interstage_length), 'Flux_interstage_S2', str(
            AstosOutput.interstage2_flux))

    # # run odin.exe to specify new wall thicknesses
    odin("./.input", "./.output")
    odinOutToAstosIn(i)  # calc sigmas

    # astosOutputReader("./.astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/outFiles/")

    # costCalculation(out_fold, material_stage1, material_stage2, material_interstage1, material_interstage2, i)
    