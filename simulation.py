import json
from photoelectronic.simulator import Simulator
from photoelectronic.ir import IRNode


def load_ir_from_json(json_file):
    """
    从 JSON 文件加载 IR 节点。
    """
    with open(json_file, "r") as f:
        ast_data = json.load(f)

    ir_nodes = []
    for assign in ast_data["assignments"]:
        ir_node = IRNode(
            op_type=assign["operation"],
            operands=assign["operands"],
            output=assign["output"],
            is_linear=assign["is_linear"]
        )
        ir_nodes.append(ir_node)
    return ir_nodes


def run_simulation(ir_nodes, inputs):
    """
    执行仿真并返回输出结果。
    """
    simulator = Simulator(ir_nodes)
    outputs = simulator.run(inputs)
    return outputs
