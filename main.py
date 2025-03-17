import subprocess
import os
import sys
import json
from photoelectronic.ir import parse_ast_to_json, IRNode
from photoelectronic.simulator import Simulator

def main():
    # 路径设置
    verilog_file = "./Electonic/examples/m1.v"
    ast_txt_file = "./Electonic/generated/ast.txt"
    ast_json_file = "./Electonic/generated/ast.json"
    
    os.makedirs(os.path.dirname(ast_txt_file), exist_ok=True)

    # 步骤1：生成原始 AST 文本
    with open(ast_txt_file, "w") as f:
        subprocess.run(
            ["python3","./pyverilog/examples/example_parser.py", verilog_file],
            stdout=f,
            check=True
        )

    # 步骤2：解析 AST 文本为 JSON
    with open(ast_txt_file, "r") as f:
        ast_text = f.read()
    ast_data = parse_ast_to_json(ast_text)
    
    # 保存 JSON
    with open(ast_json_file, "w") as f:
        json.dump(ast_data, f, indent=4)
    print(f"AST 已保存为 JSON：{ast_json_file}")

    # 步骤3：生成 IR 节点
    ir_nodes = []
    for assign in ast_data["assignments"]:
        ir_node = IRNode(
            op_type=assign["operation"],
            operands=assign["operands"],
            output=assign["output"],
            is_linear=assign["is_linear"]  # 使用解析后的 is_linear 值
        )
        ir_nodes.append(ir_node)



    # 步骤4：执行仿真
    inputs = {"A": 3, "B": 5}
    simulator = Simulator(ir_nodes)
    outputs = simulator.run(inputs)
    
    print("\n仿真结果：")
    for key, value in outputs.items():
        print(f"{key} = {value}")

if __name__ == "__main__":
    main()