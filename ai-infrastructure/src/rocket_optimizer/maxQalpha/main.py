# from ambiance import Atmosphere
import numpy as np
from rocket_optimizer.DynamicDatabase import AstosOutput


def maxQalpha(altitude, dens, vx_j, vy_j, vz_j, mach_number, s1_burntime):
    """
    calculating max_Q and several other values
    """
    alpha = 10  # degrees, default value
    # maxQ = 0.0
    # i_maxQ = 0
    #
    # i = 0
    # while i < len(dens) - 3:
    #     if altitude[i+3] > 80:
    #         v_tot = np.sqrt((vx_j[i+3]*1000) ** 2 + (vy_j[i+3]*1000) ** 2 + (vz_j[i+3]*1000) ** 2)
    #
    #         cur_q = 0.5 * v_tot ** 2 * dens[i+3]
    #
    #         if cur_q > maxQ:
    #             maxQ = cur_q
    #             i_maxQ = i + 3
    #     i += 1

    AstosOutput.q_alpha = maxQ*alpha

    # altitude[i_maxQ]=11200 # hardcoded value for mow according to ASTOS
    # mach_number[i_maxQ]=1.29 # hardcoded value for mow according to ASTOS
    # s1_burntime[i_maxQ]=80 # hardcoded value for mow according to ASTOS

    print(f"time to maxQ{s1_burntime[i_maxQ]}")
    print(f"altitude at maxQ{altitude[i_maxQ]}")
    print(f"Mach at maxQ{mach_number[i_maxQ]}")
    print(f"maxQ:{maxQ}")

    AstosOutput.altitude_at_condition_min = altitude[i_maxQ]
    AstosOutput.altitude_at_condition_nominal = altitude[i_maxQ]
    AstosOutput.altitude_at_condition_max = altitude[i_maxQ]

    AstosOutput.mach_at_condition_min = mach_number[i_maxQ]
    AstosOutput.mach_at_condition_nominal = mach_number[i_maxQ]
    AstosOutput.mach_at_condition_max = mach_number[i_maxQ]

    AstosOutput.time_to_maxQ_min = s1_burntime[i_maxQ]
    AstosOutput.time_to_maxQ_nominal = s1_burntime[i_maxQ]
    AstosOutput.time_to_maxQ_max = s1_burntime[i_maxQ]
