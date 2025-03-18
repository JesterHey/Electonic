import json
from photoelectronic.ir import IRNode, ast_to_ir_nodes

def load_ir_from_json(json_file):
    """
    从 JSON 文件加载 IR 节点。
    """
    with open(json_file, "r") as f:
        ast_data = json.load(f)
    
    # 使用ast_to_ir_nodes函数转换AST数据为IR节点
    ir_nodes = ast_to_ir_nodes(ast_data)
    return ir_nodes

def run_simulation(ir_nodes, inputs):
    """
    运行仿真。
    """
    from photoelectronic.simulator import Simulator
    
    simulator = Simulator(ir_nodes)
    outputs = simulator.run(inputs)
    return outputs