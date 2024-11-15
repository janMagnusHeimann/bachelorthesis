from rocket_optimizer.DynamicDatabase import AstosOutput, DatabaseOutput, Results
import matplotlib.pyplot as plt
import numpy as np

# If re-fitting the curve is needed (e.g. the nodes have changed)
# import sympy as sp
# # Define variables
# a, b, c = sp.symbols('a b c')
# nodes = np.array([[0.5, 10], [1, 2], [2, 1]])
# # Set up the system of equations based on the exponential function
# eq1 = sp.Eq(a/nodes[0, 0] * sp.exp(b * nodes[0, 0]) + c, nodes[0, 1])
# eq2 = sp.Eq(a/nodes[1, 0] * sp.exp(b * nodes[1, 0]) + c, nodes[1, 1])
# eq3 = sp.Eq(a/nodes[2, 0] * sp.exp(b * nodes[2, 0]) + c, nodes[2, 1])
# # Solve the system of equations for a, b, and c
# solutions = sp.solve([eq1, eq2, eq3], (a, b, c))
# # Process each solution to remove imaginary parts
# for i, sol in enumerate(solutions):
#     a_sol, b_sol, c_sol = sol
#     a_sol = sp.re(a_sol.evalf())  # Real part of a
#     b_sol = sp.re(b_sol.evalf())  # Real part of b
#     c_sol = sp.re(c_sol.evalf())  # Real part of c
#     # Print or store each solution
#     print(f"Solution {i + 1}: a = {a_sol}, b = {b_sol}, c = {c_sol}")


# a = 64/15*(9 + 4*np.sqrt(6))
# b = 2*np.log(np.sqrt(6)/4 - .5)
# c = 1 - 1/60*(np.sqrt(6) - 2)**4 * (9+4*np.sqrt(6))
# def exponential_func(x):
#     return a * np.exp(b * x) + c


a = 19.8428
b = -2.96263
c = 1  # 0.973446 to pass exactly through the three points, 1 to have a horizontal asymptote at 1
def exponential_func(x):
    return a/x * np.exp(b * x) + c


def material_price_at_thickenss(material, thickness):

    if material=="CFK":
        y_B = DatabaseOutput.cfk_prod_price
    elif material=="Steel":
        y_B = exponential_func(thickness) * DatabaseOutput.stainlesssteel_prod_price
    elif material=="Al":
        y_B = exponential_func(thickness) * DatabaseOutput.al_prod_price
    else:
        raise ValueError(f"Material {material} not recognized")

    return y_B


def costCalculation(fold, s1_mat, s2_mat, s3_mat, int1_mat, int2_mat, i):

    s1_tank_mass = Results.get_value_at('s1_tank_mass', i - 1)
    s2_tank_mass = Results.get_value_at('s2_tank_mass', i - 1)

    def get_material_prices():

        rp1_price = 5  # Kerolox [Euro/kg] v83
        lox_price = 5  # Kerolox [Euro/kg]
        return rp1_price, lox_price

    rp1_price, lox_price = get_material_prices()

    # tank prices
    tank_price = (
            material_price_at_thickenss(s1_mat, Results.get_value_at('wall_thickness_s1_lox_cylinder', i - 1)) * s1_tank_mass +
            material_price_at_thickenss(s2_mat, Results.get_value_at('wall_thickness_s2_lox_cylinder', i - 1)) * s2_tank_mass
    )

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
    engine_price = DatabaseOutput.S1_prop_system_price + DatabaseOutput.S2_prop_system_price
    avionics_price = DatabaseOutput.S1_avionics_price + DatabaseOutput.S2_avionics_price

    # # inert_price
    # inert_price = DatabaseOutput.s1_inert_mass * DatabaseOutput.inert_prod_price + (
    #     DatabaseOutput.s2_inert_mass * DatabaseOutput.inert_prod_price)  # TODO

    interstage1_price = material_price_at_thickenss(
        int1_mat, Results.get_value_at('s1_interstage_thickness', i - 1)) * Results.get_value_at('s1_interstage_mass', i - 1)
    interstage2_price = material_price_at_thickenss(
        int2_mat, Results.get_value_at('s2_interstage_thickness', i - 1)) * Results.get_value_at('s2_interstage_mass', i - 1)

    # total price
    total_price = tank_price + prop_price + engine_price + avionics_price + (
        DatabaseOutput.OTV_price + DatabaseOutput.fairing_price) + interstage1_price + interstage2_price
 
    AstosOutput.total_price = total_price
 
    AstosOutput.price_per_kg = total_price / (AstosOutput.payload_mass * 0.9)
 
    # Data
    cost_factors = ['OTV', 'Interstage 1', 'Interstage 2', 'Tank', 'Propellant', 'Propulsion', 'Avionics', 'Fairing']
    costs = [DatabaseOutput.OTV_price, interstage1_price, interstage2_price, tank_price, prop_price,
             engine_price, avionics_price, DatabaseOutput.fairing_price]
    total_cost = AstosOutput.total_price
 
    # Normalize the data
    normalized_costs = [cost / total_cost for cost in costs]
 
    # Initialize the pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
 
    # Plot data
    ax.pie(normalized_costs, labels=cost_factors, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)

    # Mapping of materials to labels
    material_mapping = {
        "CFK": "CC",
        "Al": "Al",
        "Steel": "SS"
    }

    # Get the corresponding labels for each stage
    label_stage1 = material_mapping[s1_mat]
    label_stage2 = material_mapping[s2_mat]
    label_stage3 = material_mapping[s3_mat]
    label_interstage1 = material_mapping[int1_mat]
    label_interstage2 = material_mapping[int2_mat]

    # Title
    fig.suptitle('Contributions of Cost Factors to Total Cost', fontsize=18, color='blue')
    ax.set_title(f"S1:{label_stage1}, S2:{label_stage2}, S3:{label_stage3}, IS1:{label_interstage1}, IS2:{label_interstage2}", fontsize=10)
    # plt.title('Contributions of Cost Factors to Total Cost', size=20, color='blue')
    # Add text box with total price and price per kg underneath the plot
    plt.figtext(
        0.5, 0.01, f'Total Price: €{AstosOutput.total_price:,.0f}\nPrice per kg: €{AstosOutput.price_per_kg:,.0f}',
        ha='center', fontsize=12, bbox={"facecolor": "orange", "alpha": 0.5, "pad": 5})
    plt.tight_layout()
    # Save the figure as a PDF
    plt.savefig(f'{fold}/price_contributions.pdf')
