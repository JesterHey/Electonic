from pyverilog.vparser.parser import parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from loguru import logger
import subprocess
# 1. 解析 Verilog 文件，生成 AST
ast, directives = parse(["test.v"])  # 输入 Verilog 文件路径

# 2. 打印 AST 结构
logger.info("Generating AST structure...")
with open("ast_structure.txt", "w") as f:
    ast.show(buf=f)
logger.success("AST structure has been saved to ast_structure.txt")

subprocess.run(["rm", "-r", "parser.out"])
subprocess.run(["rm", "-r", "parsetab.py"])