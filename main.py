import subprocess
import os
import sys
import json
from photoelectronic.ir import parse_ast_to_json, IRNode
from photoelectronic.simulator import Simulator
from verilog_parser.parser import VerilogParser
import loguru
def main():
    # 路径设置
    verilog_file = "./examples"
    ast_txt_file = "./generated/ast.txt"
    ast_json_file = "./generated/ast.json"

    # 步骤1：生成原始 AST 文本
    with open(ast_txt_file, "w") as f:
        # 初始化解析器
        
        parser = VerilogParser(include_paths=["include_dir"], defines=["DEBUG=1"])

        # 以下文件路径获取需优化
        filelist = [v_file for v_file in os.listdir(verilog_file) if v_file.endswith(".v")]
        file_path = [os.path.join(verilog_file, v_file) for v_file in filelist]

        loguru.logger.info("parsing verilog files...")
        ast, directives = parser.parse_files(file_path)
        ast.show(buf=f)


    # 步骤2：解析 AST 文本为 JSON
    with open(ast_txt_file, "r") as f:
        ast_text = f.read()
    ast_data = parse_ast_to_json(ast_text)
    
    # 保存 JSON
    with open(ast_json_file, "w") as f:
        json.dump(ast_data, f, indent=4)
    loguru.logger.success("json file generated successfully")
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
    
    loguru.logger.info("simulation completed")
    for key, value in outputs.items():
        print(f"{key} = {value}")

if __name__ == "__main__":
    main()