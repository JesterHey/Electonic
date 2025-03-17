from pyverilog.vparser.parser import parse
from .ir import IRNode
from pyverilog.vparser.ast import ModuleDef, Assign, And, Plus

class VerilogParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        # 解析 Verilog 文件生成 AST
        ast, _ = parse([self.file_path])
        return self._extract_ir(ast)

    def _extract_ir(self, ast):
        ir_nodes = []
        for module in ast.children():
            if isinstance(module, ModuleDef):
                for item in module.items:
                    if isinstance(item, Assign):
                        self._process_assign(item, ir_nodes)
        return ir_nodes

    def _process_assign(self, assign_node, ir_nodes):
        left = assign_node.left.var.name
        right = assign_node.right
        if isinstance(right, Plus):  # 加法（线性运算）
            operands = [op.name for op in right.children()]
            ir_nodes.append(IRNode("add", operands, left, is_linear=True))
        elif isinstance(right, And):  # 逻辑与（非线性运算）
            operands = [op.name for op in right.children()]
            ir_nodes.append(IRNode("and", operands, left, is_linear=False))