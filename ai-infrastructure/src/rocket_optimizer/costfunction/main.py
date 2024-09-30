from rocket_optimizer.AstosInputModifier import AstosInputModifier
from rocket_optimizer.Astos import Astos
from rocket_optimizer.astosOutputReader import astosOutputReader
from rocket_optimizer.tankLengthGenerator import tankLengthGenerator
from rocket_optimizer.odin_interstage_only import odin_interstage_only
from rocket_optimizer.odinOutInterstage import odinOutInterstage
from rocket_optimizer.optimizingLoop import optimizingLoop
from rocket_optimizer.costCalculation import costCalculation
from rocket_optimizer.DynamicDatabase import AstosOutput, Results
import math


def costfunction(sigmas, i):

    AstosInputModifier(sigmas[0], sigmas[1], "./.astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/inFiles/")
    Astos()
    astosOutputReader("./.astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/outFiles/")  # updates payload mass
    # TODO  tank lenght in dd
    s1_tank_length = tankLengthGenerator(AstosOutput.mass_stage1_prop, AstosOutput.rocket_diameter)
    s2_tank_length = tankLengthGenerator(AstosOutput.mass_stage2_prop, AstosOutput.rocket_diameter)

    # TODO: dynamic adjustable density
    # v1 = material volume s1
    V1 = (AstosOutput.residual_prop_s1 / sigmas[0]) * 8000  # density steel in kg/m^3
    discriminant1 = AstosOutput.rocket_diameter**2 + V1 / (math.pi * s1_tank_length)
    Results.append_value("wall_thickness_s1_lox_cylinder", -AstosOutput.rocket_diameter + math.sqrt(discriminant1))
    Results.append_value("wall_thickness_s1_rp1_cylinder", -AstosOutput.rocket_diameter + math.sqrt(discriminant1))

    V2 = (AstosOutput.residual_prop_s2 / sigmas[1]) * 8000  # thickness steel in kg/m^3

    discriminant2 = AstosOutput.rocket_diameter**2 + V2 / (math.pi * s2_tank_length)
    Results.append_value("wall_thickness_s2_lox_cylinder", -AstosOutput.rocket_diameter + math.sqrt(discriminant2))
    Results.append_value("wall_thickness_s2_rp1_cylinder", -AstosOutput.rocket_diameter + math.sqrt(discriminant2))

    Results.append_value("s1_tank_mass", sigmas[0] * AstosOutput.residual_prop_s1)
    Results.append_value("s2_tank_mass", sigmas[1] * AstosOutput.residual_prop_s2)

    odin_interstage_only("./.input_interstage_only", "./.output_interstage_only")
    odinOutInterstage()
    print(Results.get_value_at("s1_interstage_mass", -1))
    print(Results.get_value_at("s2_interstage_mass", -1))
    print(Results.get_value_at("s1_interstage_thickness", -1))
    print(Results.get_value_at("s2_interstage_thickness", -1))

    costCalculation(
        "./Images_Out/",
        "Steel",  # s1
        "Steel",  # s2
        "CFK",   # i1
        "CFK",  # i2
        i,
    )
    print("Total price: ", AstosOutput.total_price)
    # Odin check:
    optimizingLoop(i)
    i = i + 1
    sigma1_odin = Results.get_value_at("s1_sigma", -1)
    sigma2_odin = Results.get_value_at("s2_sigma", -1)

    if sigma1_odin > sigmas[0] or sigma2_odin > sigmas[1]:  # maybe iclude check for lower alpha here
        costCalculation(
            "./Images_Out/",
            "Steel",  # s1
            "Steel",  # s2
            "CFK",   # i1
            "CFK",  # i2
            i,
        )  # updates price per kg

        print("Sigmas in odin are higher as the sigmas in the homotopy file")

        # raise ValueError("Sigmas in odin are not the same as the sigmas in the homotopy file")

    # TODO: check with odin

    AstosOutput.price_per_kg = AstosOutput.total_price / AstosOutput.payload_mass
    print("Pricer per kg: ", AstosOutput.price_per_kg)
    return AstosOutput.price_per_kg  # price per kg
