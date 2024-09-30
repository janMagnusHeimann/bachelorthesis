import numpy as np


def tankLengthGenerator(fuel_mass: float, tank_diameter: float):
    """
    O/f ratio is 2.63
    """
    fuel_mass_lox = fuel_mass / (1 + (1 / 2.63))
    fuel_mass_rp1 = fuel_mass / (1 + 2.63)

    # formulas from excel sheet
    part1_lox = (fuel_mass_lox / (1091 * (1 + (1 / 2.63)))) - ((2 / 3) * np.pi * (tank_diameter ** 3) / 11.2)
    part2_lox = (fuel_mass_lox / (810 * (1 + 2.63))) - ((2 / 3) * np.pi * (tank_diameter ** 3) / 11.2)
    
    # Combine parts and compute the overall value
    tankLenght_lox = (part1_lox + part2_lox) / (np.pi * (
        tank_diameter / 2) ** 2) + (2 / 3) * np.sqrt(2) * (tank_diameter / 2)

    part1_rp1 = (fuel_mass_rp1 / (1091 * (1 + (1 / 2.63)))) - ((2 / 3) * np.pi * (tank_diameter ** 3) / 11.2)
    part2_rp1 = (fuel_mass_rp1 / (810 * (1 + 2.63))) - ((2 / 3) * np.pi * (tank_diameter ** 3) / 11.2)
    # Combine parts and compute the overall value
    tankLenght_rp1 = (part1_rp1 + part2_rp1) / (np.pi * (
        tank_diameter / 2) ** 2) + (2 / 3) * np.sqrt(2) * (tank_diameter / 2)

    return tankLenght_lox + tankLenght_rp1
