from rocket_optimizer.DynamicDatabase import AstosOutput, DatabaseOutput, Results
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator


def material_price_at_thickenss(material, thickness):

    if material == "Al":
        nodes = np.array([[0.5, 10], [1, 2], [2, 1]])

        x = nodes[:, 0]
        y = nodes[:, 1]

        # Create a PCHIP interpolator (monotonic cubic interpolation)
        spl = PchipInterpolator(x, y)

        y_B = spl(thickness) * DatabaseOutput.al_prod_price

    elif material == "Steel":
        nodes = np.array([[0.5, 10], [1, 2], [2, 1]])

        x = nodes[:, 0]
        y = nodes[:, 1]

        # Create a PCHIP interpolator (monotonic cubic interpolation)
        spl = PchipInterpolator(x, y)

        y_B = spl(thickness) * DatabaseOutput.stainlesssteel_prod_price

    elif material == "CFK":
        y_B = DatabaseOutput.cfk_prod_price

    else:
        raise ValueError(f"Material {material} not recognized")

    return y_B


a = material_price_at_thickenss('Al', 1)

print(a)


def costCalculation(fold, s1_mat, s2_mat, int1_mat, int2_mat, i):

    s1_tank_mass = Results.get_value_at('s1_tank_mass', i)
    s2_tank_mass = Results.get_value_at('s2_tank_mass', i)

    def get_material_prices():

        rp1_price = 5  # Kerolox [Euro/kg] v83
        lox_price = 5  # Kerolox [Euro/kg]
        return rp1_price, lox_price

    rp1_price, lox_price = get_material_prices()

    # tank prices
    if s1_mat == "Al" and s2_mat == "Al":
        tank_price = material_price_at_thickenss('Al', Results.get_value_at('wall_thickness_s1_lox_cylinder', i - 1)) * (
            s1_tank_mass) + (material_price_at_thickenss('Al', Results.get_value_at('wall_thickness_s2_lox_cylinder', i - 1)) * s2_tank_mass)
    elif s1_mat == "Al" and s2_mat == "CFK":
        tank_price = (material_price_at_thickenss('Al', Results.get_value_at('wall_thickness_s1_lox_cylinder', i - 1)) * s1_tank_mass) + (
            DatabaseOutput.cfk_prod_price * s2_tank_mass)
    elif s1_mat == "Al" and s2_mat == "Steel":
        tank_price = (material_price_at_thickenss('Al', Results.get_value_at('wall_thickness_s1_lox_cylinder', i - 1)) * s1_tank_mass) + (
            material_price_at_thickenss('Steel', Results.get_value_at('wall_thickness_s2_lox_cylinder', i - 1)) * s2_tank_mass)
    elif s1_mat == "Steel" and s2_mat == "Steel":
        tank_price = (material_price_at_thickenss('Steel', Results.get_value_at('wall_thickness_s1_lox_cylinder', i - 1)) *
            s1_tank_mass) + (material_price_at_thickenss('Steel', Results.get_value_at('wall_thickness_s2_lox_cylinder', i - 1)) * s2_tank_mass)
    elif s1_mat == "Steel" and s2_mat == "Al":
        tank_price = (material_price_at_thickenss('Steel', Results.get_value_at('wall_thickness_s1_lox_cylinder', i - 1)) * s1_tank_mass) + (
            material_price_at_thickenss('Al', Results.get_value_at('wall_thickness_s2_lox_cylinder', i - 1)) * s2_tank_mass)
    elif s1_mat == "Steel" and s2_mat == "CFK":
        tank_price = (material_price_at_thickenss('Steel', Results.get_value_at('wall_thickness_s1_lox_cylinder', i - 1)) * s1_tank_mass) + (
            DatabaseOutput.cfk_prod_price * s2_tank_mass)
    elif s1_mat == "CFK" and s2_mat == "CFK":
        tank_price = DatabaseOutput.cfk_prod_price * (
            s1_tank_mass + s2_tank_mass)
    elif s1_mat == "CFK" and s2_mat == "Steel":
        tank_price = (DatabaseOutput.cfk_prod_price * s1_tank_mass) + (
            material_price_at_thickenss('Steel', Results.get_value_at('wall_thickness_s2_lox_cylinder', i - 1)) * s2_tank_mass)
    elif s1_mat == "CFK" and s2_mat == "Al":
        tank_price = (DatabaseOutput.cfk_prod_price * s1_tank_mass) + (
            material_price_at_thickenss('Al', Results.get_value_at('wall_thickness_s2_lox_cylinder', i - 1)) * s2_tank_mass)
    else:
        tank_price = 0

    # propellant total price
    s1_rp1_mass = AstosOutput.mass_stage1_prop / (1 + 2.63)
    s1_lox_mass = AstosOutput.mass_stage1_prop - s1_rp1_mass
    s2_rp1_mass = AstosOutput.mass_stage2_prop / (1 + 2.63)
    s2_lox_mass = AstosOutput.mass_stage2_prop - s2_rp1_mass

    prop_price = rp1_price * (s1_rp1_mass + s2_rp1_mass) + lox_price * (s1_lox_mass + s2_lox_mass)

    # price for propulsion system
    # s1_propulsion_system = DatabaseOutput.number_engines * 1547 * DatabaseOutput.engine_prod_price * 1.6 * 1.26 / 10
    # s2_propulsion_system = DatabaseOutput.number_engines_s2 * 97 * DatabaseOutput.engine_prod_price * 1.6 * 1.26 / 10

    # prices from cole
    # http://gitlab.ad.rfa.space/rfa/missionteam/aig/review_meetings/meeting_09_09_2024/-/issues/2?work_item_iid=4
    engine_plus_inert_price = DatabaseOutput.engine_plus_inert_price_s1 + DatabaseOutput.engine_plus_inert_price_s2

    # # inert_price
    # inert_price = DatabaseOutput.s1_inert_mass * DatabaseOutput.inert_prod_price + (
    #     DatabaseOutput.s2_inert_mass * DatabaseOutput.inert_prod_price)  # TODO

    if int1_mat == "CFK" and int2_mat == "CFK":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.cfk_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.cfk_prod_price
    elif int1_mat == "CFK" and int2_mat == "Al":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.cfk_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.al_prod_price
    elif int1_mat == "CFK" and int2_mat == "Steel":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.cfk_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.stainlesssteel_prod_price
    elif int1_mat == "Al" and int2_mat == "Al":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.al_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.al_prod_price
    elif int1_mat == "Al" and int2_mat == "CFK":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.al_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.cfk_prod_price
    elif int1_mat == "Al" and int2_mat == "Steel":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.al_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.stainlesssteel_prod_price
    elif int1_mat == "Steel" and int2_mat == "Steel":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.stainlesssteel_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.stainlesssteel_prod_price
    elif int1_mat == "Steel" and int2_mat == "Al":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.stainlesssteel_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.al_prod_price
    elif int1_mat == "Steel" and int2_mat == "CFK":
        interstages1_price = Results.get_value_at(
            's1_interstage_mass', i - 1) * DatabaseOutput.stainlesssteel_prod_price
        interstages2_price = Results.get_value_at(
            's2_interstage_mass', i - 1) * DatabaseOutput.cfk_prod_price
    else:
        raise ValueError(f"Interstage material combination {int1_mat} and {int2_mat} not recognized")

    # total price
    total_price = tank_price + prop_price + engine_plus_inert_price + (
        DatabaseOutput.OTV_price + DatabaseOutput.fairing_price) + interstages1_price + interstages2_price
 
    AstosOutput.total_price = total_price
 
    AstosOutput.price_per_kg = total_price / (AstosOutput.payload_mass * 0.9)
 
    # Data
    cost_factors = ['OTV', 'interstage1', 'interstage2', 'tank', 'prop', 'engine + inert', 'fairing']
    costs = [DatabaseOutput.OTV_price, interstages1_price, interstages2_price, tank_price, prop_price,
             engine_plus_inert_price, DatabaseOutput.fairing_price]
    total_cost = AstosOutput.total_price
 
    # Normalize the data
    normalized_costs = [cost / total_cost for cost in costs]
 
    # Initialize the pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
 
    # Plot data
    ax.pie(normalized_costs, labels=cost_factors, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
 
    # Title
    plt.title('Contributions of Cost Factors to Total Cost', size=20, color='blue')
    # Add text box with total price and price per kg underneath the plot
    plt.figtext(
        0.5, 0.01, f'Total Price: €{AstosOutput.total_price:,.0f}\nPrice per kg: €{AstosOutput.price_per_kg:,.0f}',
        ha='center', fontsize=12, bbox={"facecolor": "orange", "alpha": 0.5, "pad": 5})
    # Save the figure as a PDF
    plt.savefig(f'{fold}/price_contributions.pdf')

