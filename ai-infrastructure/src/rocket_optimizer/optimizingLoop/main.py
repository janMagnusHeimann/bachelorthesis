from rocket_optimizer.loadCaseGenerator import loadCaseGenerator
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
from rocket_optimizer.flux_calc import max_flux_calc
from rocket_optimizer.tank_pressure_optimizer.main import loadCaseEditInput, loadFactorFromOutput

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
    loadCaseInputGenerator(i)

    # # calculate new p1 and p2 values
    # p_s1, p_s2 = tank_pressure_optimizer(0, 15, 0, 15, 1.2, 100, 1.0e-6)  # 100 iterations hardcoded
    p_s1, p_s2 = 7., 7.
    Results.append_value('p1', p_s1)
    Results.append_value('p2', p_s2)
    loadCaseEditInput(p_s1, p_s2)
    loadCaseGenerator(AstosOutput.rocket_diameter)
    loadFactor_s1, loadFactor_s2 = loadFactorFromOutput()
    print("Stage 1 tank factor of safety: ", loadFactor_s1)
    print("Stage 2 tank factor of safety: ", loadFactor_s2)
    # print('\n\n--------PRESSURE CHECK----------')
    # print (p_s1, p_s2, '\n\n')
    # safety factor here is 1.5, prev. 1.2 in order to increase tank wallthickness reasonably

    AstosOutput.stage1_tank_pressure = abs(p_s1)
    AstosOutput.stage2_tank_pressure = abs(p_s2)  # pure assumption that tank pressure of S2 is same as for S1 (TBD)
    # TODO: !DELETE HARCODED! /2, there to make tank pressure and wall thickness more realistic
    # AstosOutput.stage2_tank_pressure = p_s2

    s1_lox_tank_length = (2.63*(810.0/1091.0) * s1_tank_length) / (1.0 + 2.63*(810.0/1091.0))
    s1_rp1_tank_length = s1_tank_length - s1_lox_tank_length

    s2_lox_tank_length = (2.63*(810.0/1091.0) * s2_tank_length) / (1.0 + 2.63*(810.0/1091.0))
    s2_rp1_tank_length = s2_tank_length - s2_lox_tank_length

    s1_interstage_length = 1.4 * AstosOutput.rocket_diameter  # TODO
    s2_interstage_length = 0.7 * AstosOutput.rocket_diameter  # TODO

    Results.append_value('interstage_length_s1', s1_interstage_length)  # TODO
    Results.append_value('interstage_length_s2', s2_interstage_length)  # TODO

    odinInputModifier(AstosOutput.odin_input_path, 's1_cylinder', s1_rp1_tank_length,
                      'S1_RP1tank', (AstosOutput.stage1_tank_pressure * safety_factor_pressure) / 10)
    odinInputModifier(AstosOutput.odin_input_path, 's1_cylinder_2', s1_lox_tank_length,
                      'S1_LOXtank', (AstosOutput.stage1_tank_pressure * safety_factor_pressure) / 10)
    odinInputModifier(AstosOutput.odin_input_path, 's2_cylinder', s2_rp1_tank_length,
                      'S2_RP1tank', (AstosOutput.stage2_tank_pressure * safety_factor_pressure) / 10)
    odinInputModifier(AstosOutput.odin_input_path, 's2_cylinder_2', s2_lox_tank_length,
                      'S2_LOXtank', (AstosOutput.stage2_tank_pressure * safety_factor_pressure) / 10)

    AstosOutput.S1_RP1_tank_flux = max_flux_calc(AstosOutput.d_n_stage1_bottom_tank_head,
                                                 AstosOutput.d_n_stage1_bulkhead)
    AstosOutput.S1_LOX_tank_flux = max_flux_calc(AstosOutput.d_n_stage1_bulkhead,
                                                 AstosOutput.d_n_stage1_top_tank_head)
    AstosOutput.S2_RP1_tank_flux = max_flux_calc(AstosOutput.d_n_stage2_bottom_tank_head,
                                                 AstosOutput.d_n_stage2_bulkhead)
    AstosOutput.S2_LOX_tank_flux = max_flux_calc(AstosOutput.d_n_stage2_bulkhead,
                                                 AstosOutput.d_n_stage2_top_tank_head)

    odinInputModifier_flux(AstosOutput.odin_input_path, 's1_cylinder', s1_interstage_length,
                           'S1_RP1tank', AstosOutput.S1_RP1_tank_flux)
    odinInputModifier_flux(AstosOutput.odin_input_path, 's1_cylinder_2', s2_interstage_length,
                           'S1_LOXtank', AstosOutput.S1_LOX_tank_flux)
    odinInputModifier_flux(AstosOutput.odin_input_path, 's2_cylinder', s1_interstage_length,
                           'S2_RP1tank', AstosOutput.S2_RP1_tank_flux)
    odinInputModifier_flux(AstosOutput.odin_input_path, 's2_cylinder_2', s2_interstage_length,
                           'S2_LOXtank', AstosOutput.S2_LOX_tank_flux)

    AstosOutput.interstage1_flux = max_flux_calc(AstosOutput.d_n_stage1__stage2_interstage_bottom,
                                                 AstosOutput.d_n_stage1__stage2_interstage_flange - 0.2)
    print("Interstage 1 max flux: ", AstosOutput.interstage1_flux)
    AstosOutput.interstage2_flux = max_flux_calc(AstosOutput.d_n_stage2__fairing_interstage_bottom,
                                                 AstosOutput.d_n_stage2__fairing_interstage_flange)
    print("Interstage 2 max flux: ", AstosOutput.interstage2_flux)

    odinInputModifier_flux(AstosOutput.odin_input_path, 'S1_interstage', s1_interstage_length,
                           'S1_interstage', AstosOutput.interstage1_flux)
    odinInputModifier_flux(AstosOutput.odin_input_path, 'S2_interstage', s2_interstage_length,
                           'S2_interstage', AstosOutput.interstage2_flux)

    # TODO: add thruss frame loads

    # # run odin.exe to specify new wall thicknesses
    odin("./.input", "./.output")
    odinOutToAstosIn(i)  # calc sigmas

    # astosOutputReader("./.astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/outFiles/")

    # costCalculation(out_fold, material_stage1, material_stage2, material_interstage1, material_interstage2, i)
