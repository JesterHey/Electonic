import os
import json
import subprocess
from verilog_parser.parser import VerilogParser
from loguru import logger
from photoelectronic.ir import parse_ast_to_json
from simulation import load_ir_from_json, run_simulation


def generate_ast(verilog_file, ast_txt_file):
    """
    生成原始 AST 文本。
    """
    parser = VerilogParser(include_paths=["include_dir"], defines=["DEBUG=1"])

    # 获取 Verilog 文件路径
    filelist = [v_file for v_file in os.listdir(
        verilog_file) if v_file.endswith(".v")]
    file_path = [os.path.join(verilog_file, v_file) for v_file in filelist]

    logger.info("Parsing Verilog files...")
    ast, _ = parser.parse_files(file_path)

    # 将 AST 写入文件
    with open(ast_txt_file, "w") as f:
        ast.show(buf=f)

    # 删除临时文件
    subprocess.run(["rm", "-f", "parser.out", "parsetab.py"])


def parse_and_save_ast(ast_txt_file, ast_json_file):
    """
    解析 AST 文本并保存为 JSON。
    """
    with open(ast_txt_file, "r") as f:
        ast_text = f.read()
    ast_data = parse_ast_to_json(ast_text)

    # 保存 JSON
    with open(ast_json_file, "w") as f:
        json.dump(ast_data, f, indent=4)
    logger.success("JSON file generated successfully.")


def main():
    # 路径设置
    verilog_file = "./examples"
    ast_txt_file = "./generated/ast.txt"
    ast_json_file = "./generated/ast.json"

    # 步骤1：生成原始 AST 文本
    generate_ast(verilog_file, ast_txt_file)

    # 步骤2：解析 AST 文本为 JSON
    parse_and_save_ast(ast_txt_file, ast_json_file)

    # 步骤3：加载 IR 节点
    ir_nodes = load_ir_from_json(ast_json_file)

    # 步骤4：执行仿真
    inputs = {"A": 3, "B": 5}
    outputs = run_simulation(ir_nodes, inputs)

    # 输出仿真结果
    logger.info("Simulation completed")
    for key, value in outputs.items():
        print(f"{key} = {value}")


if __name__ == "__main__":
    main()
