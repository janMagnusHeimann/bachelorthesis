from dataclasses import dataclass, field
from typing import Dict, List


class Results:
    _parameters_info = {
        'tank_length_s1': {'unit': 'm', 'description':
                           'Tank Length Stage 1', 'variable_name': 't_len_S1'},
        'tank_length_s2': {'unit': 'm', 'description':
                           'Tank Length Stage 2', 'variable_name': 't_len_S2'},
        'interstage_length_s1': {'unit': 'm', 'description':
                                 'Interstage Length Stage 1', 'variable_name': 'int_len_S1'},
        'interstage_length_s2': {'unit': 'm', 'description':
                                 'Interstage Length Stage 2', 'variable_name': 'int_len_S2'},
        'complete_length_s1': {'unit': 'm', 'description':
                               'Stage Length Stage 1', 'variable_name': 'tot_len_S1'},
        'complete_length_s2': {'unit': 'm', 'description':
                               'Stage Length Stage 2', 'variable_name': 'tot_len_S2'},
        'complete_length': {'unit': 'm', 'description':
                            'Rocket Length', 'variable_name': 'tot_len'},
        'aspect_ratio': {'unit': '-', 'description':
                         'aspect ratio of rocket', 'variable_name': 'L_D'},
        'p1': {'unit': 'bar', 'description':
               'Pressure 1', 'variable_name': 'P1'},
        'p2': {'unit': 'bar', 'description':
               'Pressure 2', 'variable_name': 'P2'},
        # 'p1_ullage': {'unit': 'bar', 'description':
        #               'ullage pressure 1', 'variable_name': 'P1_ullage'},
        # 'p2_ullage': {'unit': 'bar', 'description':
        #               'ullage pressure 2', 'variable_name': 'P2_ullage'},
        # 'flux': {'unit': 'kg/s', 'description':
        #        'Flux', 'variable_name': 'Flux'},
        'wall_thickness_s1_aftdome': {'unit': 'm', 'description':
                                      'Wall Thickness S1 Aft Dome', 'variable_name': 't_wall_aft_S1'},
        'wall_thickness_s1_lox_cylinder': {'unit': 'm', 'description':
                                           'Wall Thickness S1 LOX Cylinder', 'variable_name': 't_wall_LOX_S1'},
        'wall_thickness_s1_rp1_cylinder': {'unit': 'm', 'description':
                                           'Wall Thickness S1 RP1 Cylinder', 'variable_name': 't_wall_RP1_S1'},
        'wall_thickness_s1_fddome': {'unit': 'm', 'description':
                                     'Wall Thickness S1 Forward Dome', 'variable_name': 't_wall_fd_S1'},
        'wall_thickness_s2_aftdome': {'unit': 'm', 'description':
                                      'Wall Thickness S2 Aft Dome', 'variable_name': 't_wall_aft_S2'},
        'wall_thickness_s2_lox_cylinder': {'unit': 'm', 'description':
                                           'Wall Thickness S2 LOX Cylinder', 'variable_name': 't_wall_LOX_S2'},
        'wall_thickness_s2_rp1_cylinder': {'unit': 'm', 'description':
                                           'Wall Thickness S2 RP1 Cylinder', 'variable_name': 't_wall_RP1_S2'},
        'wall_thickness_s2_fddome': {'unit': 'm', 'description':
                                     'Wall Thickness S2 Forward Dome', 'variable_name': 't_wall_fd_S2'},
        's1_tank_mass': {'unit': 'kg', 'description':
                         'Stage 1 Tank Mass', 'variable_name': 'tank_mass_S1'},
        's2_tank_mass': {'unit': 'kg', 'description':
                         'Stage 2 Tank Mass', 'variable_name': 'tank_mass_S2'},
        's1_interstage_mass': {'unit': 'kg', 'description':
                               'Stage 1 Interstage Mass', 'variable_name': 'inter_mass_S1'},
        's2_interstage_mass': {'unit': 'kg', 'description':
                               'Stage 2 Interstage Mass', 'variable_name': 'inter_mass_S2'},
        's1_interstage_thickness': {'unit': 'm', 'description':
                                    'Stage 1 Interstage Thickness', 'variable_name': 'inter_thick_S1'},
        's2_interstage_thickness': {'unit': 'm', 'description':
                                    'Stage 2 Interstage Thickness', 'variable_name': 'inter_thick_S2'},
        's1_sigma': {'unit': '-', 'description':
                     'Stage 1 Sigma', 'variable_name': 'sigma_S1'},
        's2_sigma': {'unit': '-', 'description':
                     'Stage 2 Sigma', 'variable_name': 'sigma_S2'},
    }

    # Initialize _data based on _parameters_info
    _data: Dict[str, List[float]] = {key: [] for key in _parameters_info}

    @classmethod
    def append_value(cls, key: str, value: float) -> None:
        if key in cls._data:
            cls._data[key].append(value)
        else:
            raise KeyError(f"{key} is not a valid key. Valid keys are: {list(cls._data.keys())}")

    @classmethod
    def get_value_at(cls, key: str, index: int) -> float:
        if key in cls._data:
            try:
                return cls._data[key][index]
            except IndexError:
                raise IndexError(f"Index {index} is out of range for key '{key}'.")
        else:
            raise KeyError(f"{key} is not a valid key. Valid keys are: {list(cls._data.keys())}")

    @classmethod
    def __repr__(cls) -> str:
        return f"Results(data={cls._data})"

    @classmethod
    def get_units(cls, key: str) -> str:
        return cls._parameters_info.get(key, {}).get('unit', "No unit defined")

    @classmethod
    def get_description(cls, key: str) -> str:
        return cls._parameters_info.get(key, {}).get('description', "No description defined")

    @classmethod
    def get_variable_name(cls, key: str) -> str:
        return cls._parameters_info.get(key, {}).get('variable_name', "No variable name defined")


@dataclass()
class AstosOutput:

    price_per_kg: float

    total_price: float

    thrust: float
    # sealevel_thrust_s1: float
    interstage1_flux: float
    interstage2_flux: float
    S1_LOX_tank_flux: float
    S1_RP1_tank_flux: float
    S2_LOX_tank_flux: float
    S2_RP1_tank_flux: float
    S1_total_dry_mass: float
    S2_total_dry_mass: float
    residual_prop_s1: float
    residual_prop_s2: float
    residual_prop_s3: float
    vacuum_isp_s1: float
    vacuum_isp_s2: float
    vacuum_isp_s3: float
    vacuum_thrust_s1: float
    vacuum_thrust_s2: float
    vacuum_thrust_s3: float
    engine_nozzle_exit_s1: float
    engine_nozzle_exit_s2: float
    engine_nozzle_exit_s3: float
    payload_mass: float

    # Odin input data
    # structural_mass_S1: float
    # structural_mass_S2: float
    # structural_mass_S3: float
    # s1_tank_radius: float
    # fuel_mass_S1: float
    # fairing_length: float

    # load case calculator input

    # sheet1 (except booster and engine data, its in frozen dataclass)

    # d_n : distances from S1 nozzle exit plane [m]
    # tlo : Total lift-off propellant mass
    q_alpha: float
    length_conical_section: float
    nosecone_semivertex_angle: float
    rocket_diameter: float
    stage1_length: float
    stage2_length: float
    stage3_length: float
    fairing_length: float
    d_n_gimbal_point: float
    d_n_stage1_bottom_tank_head: float
    d_n_stage1_bulkhead: float
    d_n_stage1_top_tank_head: float
    d_n_stage2_bottom_tank_head: float
    d_n_stage2_bulkhead: float
    d_n_stage2_top_tank_head: float
    tlo_stage1_bottom_tank: float
    tlo_stage1_top_tank: float
    tlo_stage2_bottom_tank: float
    tlo_stage2_top_tank: float
    stage1_tank_pressure: float
    stage2_tank_pressure: float
    altitude_at_condition_min: float
    altitude_at_condition_nominal: float
    altitude_at_condition_max: float
    mach_at_condition_min: float
    mach_at_condition_nominal: float
    mach_at_condition_max: float
    time_to_maxQ_min: float
    time_to_maxQ_nominal: float
    time_to_maxQ_max: float
    stage1_burntime: float

    # d_n : distances from S1 nozzle exit plane [m]
    d_n_stage1_common_main_stage: float
    d_n_stage1_thrust_module: float
    d_n_unaccounted_S1: float
    d_n_stage1_unburned_RP1: float
    d_n_stage1_unburned_LOX: float
    d_n_stage1_tank_system: float
    d_n_stage1_pressurization: float
    d_n_stage2_propulsion_system: float
    d_n_stage2_reaction_control_system: float
    d_n_stage2_prop_distribution_system: float
    d_n_stage2_pressurization: float
    d_n_stage2_unburned_RP1: float
    d_n_stage2_unburned_LOX: float
    d_n_stage2_tank_system: float
    d_n_S3_dry: float
    d_n_S3_prop: float
    d_n_payload: float
    d_n_fairing: float

    # sheet3

    # ?

    # sheet4

    # d_n : distances from S1 nozzle exit plane [m]
    d_n_stage1_bottom_tank_head: float  # TODO: defined twice (?)
    d_n_stage1_bulkhead: float  # TODO: defined twice (?)
    d_n_stage1__stage2_interstage_bottom: float
    d_n_stage1_top_tank_head: float
    d_n_stage1__stage2_interstage_flange: float
    d_n_stage2_bottom_tank_head: float
    d_n_stage2_bulkhead: float
    d_n_stage2__fairing_interstage_bottom: float
    d_n_stage2_top_tank_head: float
    d_n_stage2__fairing_interstage_flange: float

    # homotopy file input
    mass_stage1_prop: float
    mass_stage2_prop: float
    mass_stage3_prop: float

    engine_sealevel_thrust: float
    engine_vacuum_thrust_s1: float
    engine_vacuum_thrust_s2: float
    engine_vacuum_isp_s1: float
    engine_vacuum_isp_s2: float
    engine_nozzle_area_s1: float
    engine_nozzle_area_s2: float

    # TODO: move it somewhere else
    odin_input_path: str
    s1_tank_material: str
    s2_tank_material: str
    s3_tank_material: str
    interstage1_material: str
    interstage2_material: str

@dataclass(frozen=True)
class DatabaseOutput:

    s1_inert_mass: float = 950.  # TODO: read data from gtp, not hardcoded
    s2_inert_mass: float = 600.  # TODO: read data from gtp, not hardcoded
    s3_dry_mass: float = 327.  # TODO: read data from gtp, not hardcoded

    # load case calculator input
    # sheet1

    # booster data
    number_boosters: int = 0
    mass_boster: float = 0.  # TODO: correct typo
    cog_booster: float = 1.
    thrust_booster: float = 0.
    booster_diameter: float = 2.15
    booster_length: float = 10.
    booster_cone_length: float = 1.
    booster_nosecone_vertexangle: float = 20.46
    booster_forward_attach_point: float = 10.
    booster_aft_attach_point: float = 2.

    # engine data
    s1_engine_startup_pressure: float = 7.  # [bars]
    s2_engine_startup_pressure: float = 7.  # [bars]
    number_engines: int = 9
    number_engines_s2: int = 1
    mass_engine_s1: float = 343.89  # TODO: read data from gtp or homotopy, not hardcoded
    mass_engine_s2: float = 243.  # TODO: read data from gtp or homotopy, not hardcoded
    engine_sealevel_thrust: float = 73400.  # TODO: read data from gtp or homotopy, not hardcoded
    engine_nozzle_exhaust_pressure: float = 50000.
    engine_nozzle_area: float = 0.118  # TODO: read data from gtp or homotopy, not hardcoded

    # manufacturing prices
    stainlesssteel_prod_price: float = 200.  # [Euro/kg]
    al_prod_price: float = 400.  # [Euro/kg]
    cfk_prod_price: float = 2200.  # [Euro/kg]

    S1_prop_system_price: float = 3373416.94  # [Euros]
    S1_avionics_price: float = 141416.  # [Euros]
    S2_prop_system_price: float = 340749.19  # [Euros]
    S2_avionics_price: float = 750171.  # [Euros]

    # engine_plus_inert_price_s1: float = 3514832.94

    # engine_plus_inert_price_s2: float = 1090920.19

    # OTV price
    OTV_price: float = 921765.32
    fairing_price: float = 500000.

    materials: dict[str, dict[str, float]] = field(default_factory=lambda: {
        "Steel":
            {"yield strenght": 870.0,
             "Young's modulus": 200.0e+3,
             "Poisson's ratio": .28,
             "Shear modulus": 77000,
             "density": 7.9e+3,
             "MorC": "M"},
        "Al":
            {"yield strenght": 276.0,
             "Young's modulus": 70.0e+3,
             "Poisson's ratio": .33,
             "Shear modulus": 26000,
             "density": 2.7e+3,
             "MorC": "M"},
        "CFK":
            {"yield strenght": 748.1,
             "Young's modulus": 48.0e+3,
             "Poisson's ratio": .04,
             "Shear modulus": 2625,
             "density": 1.57e+3,
             "MorC": "C"},
    })  # TODO: use these instead of excel


@dataclass
class Masses:  # TODO: get rid of hardcoded values can be read in from the gtp or homotopy
    # sheet2

    # Masses [kg]
    mass_stage1_common_main_stage: float = 1674.1
    mass_stage1_thrust_module: float = 70.0
    mass_unaccounted: float = 350.0
    mass_stage1_unburned_RP1: float = 0.0
    mass_stage1_unburned_LOX: float = 0.0
    mass_stage1_tank_system: float = 2195.8
    mass_stage1_pressurization: float = 491.3
    mass_stage2_propulsion_system: float = 221
    mass_stage2_reaction_control_system: float = 29.2
    mass_stage2_prop_distribution_system: float = 34.3
    mass_stage2_pressurization: float = 114.1
    mass_stage2_unburned_RP1: float = 0.0
    mass_stage2_unburned_LOX: float = 0.0
    mass_stage2_tank_system: float = 834.1
    mass_stage3_dry: float = 554.5
    mass_stage3_prop: float = 541.7
    mass_payload: float = 504.7
    mass_fairing: float = 250  # TODO: read data from gtp or homotopy, not hardcoded
