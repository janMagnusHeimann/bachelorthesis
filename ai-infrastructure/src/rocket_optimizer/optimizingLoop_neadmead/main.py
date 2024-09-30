from rocket_optimizer.xml_reader import xml_reader
from rocket_optimizer.neadmead import neadmead


def optimizingLoop_neadmead(i, alphas):

    print("sigmas: ", xml_reader())
    print("alphas: ", alphas)

    neadmead(xml_reader(), alphas, i)


if __name__ == "__main__":

    from rocket_optimizer.DynamicDatabase import AstosOutput

    AstosOutput.stage1_tank_pressure = 7
    AstosOutput.stage2_tank_pressure = 7
    AstosOutput.odin_input_path = "./.input/config_S1SS_S2SS_S3SS_IS1CC_IS2CC.txt"
    AstosOutput.total_price = 8000000

    alphas = [4053.6428669341058, 4615.225372916875, 4866.697621267359]
    try:
        optimizingLoop_neadmead(0, alphas)
    except ValueError as e:
        print(e)
