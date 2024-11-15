from rocket_optimizer.DynamicDatabase import AstosOutput


def distances_nozzle_exit_plane(s1_tank_length, s2_tank_length):

    AstosOutput.stage1_length = AstosOutput.rocket_diameter * 0.895 + s1_tank_length
    AstosOutput.stage2_length = AstosOutput.rocket_diameter * 1.4 + s2_tank_length
    AstosOutput.stage3_length = AstosOutput.rocket_diameter * 0.8  # TODO


    AstosOutput.d_n_gimbal_point = AstosOutput.rocket_diameter * 0.895
    AstosOutput.d_n_stage1_bottom_tank_head = AstosOutput.rocket_diameter * 0.895
    AstosOutput.d_n_stage1_bulkhead = AstosOutput.rocket_diameter * 0.895 + (s1_tank_length / (
        1 + 2.63))
    AstosOutput.d_n_stage1_top_tank_head = AstosOutput.rocket_diameter * 0.895 + (s1_tank_length)
    AstosOutput.d_n_stage2_bottom_tank_head = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4
    AstosOutput.d_n_stage2_bulkhead = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + (s2_tank_length / (1 + 2.63))
    AstosOutput.d_n_stage2_top_tank_head = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + s2_tank_length
    AstosOutput.d_n_stage1_common_main_stage = AstosOutput.rocket_diameter * 0.895
    AstosOutput.d_n_stage1_thrust_module = AstosOutput.rocket_diameter * 0.895
    AstosOutput.d_n_unaccounted_S1 = AstosOutput.rocket_diameter * 0.895
    AstosOutput.d_n_stage1_unburned_RP1 = AstosOutput.rocket_diameter * 0.895
    AstosOutput.d_n_stage1_unburned_LOX = AstosOutput.rocket_diameter * 0.895
    AstosOutput.d_n_stage1_tank_system = AstosOutput.rocket_diameter * 0.895 + (s1_tank_length / 2)
    AstosOutput.d_n_stage1_pressurization = AstosOutput.rocket_diameter * 0.895 + (s1_tank_length / 2)
    AstosOutput.d_n_stage2_propulsion_system = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4
    AstosOutput.d_n_stage2_reaction_control_system = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4
    AstosOutput.d_n_stage2_prop_distribution_system = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4
    AstosOutput.d_n_stage2_pressurization = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4
    AstosOutput.d_n_stage2_unburned_RP1 = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4
    AstosOutput.d_n_stage2_unburned_LOX = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4
    AstosOutput.d_n_stage2_tank_system = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4
    AstosOutput.d_n_S3_dry = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + s2_tank_length + AstosOutput.rocket_diameter * 0.8
    AstosOutput.d_n_S3_prop = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + s2_tank_length + AstosOutput.rocket_diameter * 0.8
    AstosOutput.d_n_payload = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + s2_tank_length + AstosOutput.rocket_diameter * 0.8
    AstosOutput.d_n_fairing = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + s2_tank_length + AstosOutput.rocket_diameter * 0.8
    # defined twice (this probably refers to S3)
    # AstosOutput.d_n_stage1_bottom_tank_head = AstosOutput.rocket_diameter * 0.895 + (
    #     s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + s2_tank_length + AstosOutput.rocket_diameter * 0.8
    AstosOutput.d_n_stage1__stage2_interstage_bottom = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length)  # + AstosOutput.rocket_diameter * 1.4 + s2_tank_length + AstosOutput.rocket_diameter * 0.8
    AstosOutput.d_n_stage1__stage2_interstage_flange = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4  # + s2_tank_length + AstosOutput.rocket_diameter * 0.8
    AstosOutput.d_n_stage2__fairing_interstage_bottom = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + s2_tank_length  # + AstosOutput.rocket_diameter * 0.8
    AstosOutput.d_n_stage2__fairing_interstage_flange = AstosOutput.rocket_diameter * 0.895 + (
        s1_tank_length) + AstosOutput.rocket_diameter * 1.4 + s2_tank_length + AstosOutput.rocket_diameter * 0.8
