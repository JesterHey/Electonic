from pyverilog.vparser.parser import parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from loguru import logger
import subprocess
import os
# 1. 解析 Verilog 文件，生成 AST
verilog_files = [v_file for v_file in os.listdir('./verilog_files') if v_file.endswith(".v")]
for v_file in verilog_files:
    logger.info(f"Parse {v_file}")
    ast, directives = parse([f"./verilog_files/{v_file}"])
    with open(f"./ast_files/{v_file[:-2]}_ast.txt", "w") as f:
        ast.show(buf = f)


subprocess.run(["rm", "-r", "parser.out"])
subprocess.run(["rm", "-r", "parsetab.py"])