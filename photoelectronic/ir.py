import re
import json

class IRNode:
    def __init__(self, op_type, operands, output, is_linear=False):
        self.op_type = op_type
        self.operands = operands
        self.output = output
        self.is_linear = is_linear  # 线性/非线性标志

    def __repr__(self):
        return f"IRNode({self.op_type}, {self.operands} → {self.output}, Linear={self.is_linear})"

def parse_ast_to_json(ast_text):
    # 预处理：删除所有括号及内容
    processed_text = re.sub(r"\s*\(.*?\)", "", ast_text)
    lines = processed_text.splitlines()

    ast_data = {
        "module": None,
        "ports": {
            "input": [],
            "output": []
        },
        "assignments": []
    }

    current_assign = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        
        # 提取模块名
        if line.startswith("ModuleDef:"):
            module_name = line.split()[1]
            ast_data["module"] = module_name
        
        # 提取输入端口
        elif line.startswith("Input:"):
            port_name = line.split()[1].rstrip(",")
            ast_data["ports"]["input"].append(port_name)
        
        # 提取输出端口
        elif line.startswith("Output:"):
            port_name = line.split()[1].rstrip(",")
            ast_data["ports"]["output"].append(port_name)
        
        # 检测赋值语句
        elif line.startswith("Assign:"):
            current_assign = {
                "output": None,
                "operation": None,
                "operands": [],
                "is_linear": False  # 默认为非线性
            }
            ast_data["assignments"].append(current_assign)
            
            # 进入子行解析
            while i < len(lines):
                i += 1
                if i >= len(lines):
                    break
                
                subline = lines[i].strip()
                
                # 提取 Lvalue 中的 Identifier
                if subline.startswith("Lvalue:"):
                    # 下一行是 Identifier
                    if i+1 < len(lines):
                        identifier_line = lines[i+1].strip()
                        if identifier_line.startswith("Identifier:"):
                            current_assign["output"] = identifier_line.split()[1]
                
                # 提取 Rvalue 中的操作类型
                elif subline.startswith("Rvalue:"):
                    # 下一行是操作类型（And/Plus）
                    if i+1 < len(lines):
                        op_line = lines[i+1].strip()
                        if op_line.startswith("And:"):
                            current_assign["operation"] = "and"
                            current_assign["is_linear"] = False  # 显式设置为非线性
                        elif op_line.startswith("Plus:"):
                            current_assign["operation"] = "add"
                            current_assign["is_linear"] = True   # 显式设置为线性
                    
                    # 提取操作数（下两行）
                    operands = []
                    for _ in range(2):
                        if i+2 < len(lines):
                            operand_line = lines[i+2].strip()
                            if operand_line.startswith("Identifier:"):
                                operands.append(operand_line.split()[1])
                        i += 1
                    current_assign["operands"] = operands
                
                # 退出当前 Assign 解析
                elif subline.startswith(("Assign:", "ModuleDef:")):
                    i -= 1
                    break
        
        i += 1
    
    return ast_data