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
    lines = ast_text.splitlines()

    ast_data = {
        "module": None,
        "ports": {
            "input": [],
            "output": []
        },
        "assignments": []
    }

    # 提取模块名和端口
    for i, line in enumerate(lines):
        line = line.strip()
        if "ModuleDef:" in line:
            match = re.search(r"ModuleDef:\s+(\w+)", line)
            if match:
                ast_data["module"] = match.group(1)
        elif "Input:" in line:
            match = re.search(r"Input:\s+(\w+)", line)
            if match:
                ast_data["ports"]["input"].append(match.group(1).rstrip(','))
        elif "Output:" in line:
            match = re.search(r"Output:\s+(\w+)", line)
            if match:
                ast_data["ports"]["output"].append(match.group(1).rstrip(','))

    # 寻找并解析所有赋值语句
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Assign:"):
            # 找到一个赋值语句
            assignment = extract_assignment(lines, i)
            if assignment:
                ast_data["assignments"].append(assignment)
        i += 1

    return ast_data

def extract_assignment(lines, start_idx):
    """提取一个完整的赋值语句"""
    assignment = {
        "output": None,
        "operation": None,
        "operands": [],
        "is_linear": False
    }
    
    # 在赋值语句中查找左值（输出）
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if "Lvalue:" in line:
            # 搜索下一行的标识符
            for j in range(i+1, min(i+5, len(lines))):
                if "Identifier:" in lines[j]:
                    match = re.search(r"Identifier:\s+(\w+)", lines[j].strip())
                    if match:
                        assignment["output"] = match.group(1)
                        break
            break
    
    # 查找右值（操作与操作数）
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if "Rvalue:" in line:
            # 找到右值后，解析表达式树
            expression_data, _ = parse_expression_tree(lines, i+1)
            if expression_data:
                assignment["operation"] = expression_data["operation"]
                assignment["operands"] = expression_data["operands"]
                assignment["is_linear"] = expression_data["is_linear"]
            break
    
    return assignment

def parse_expression_tree(lines, start_idx, depth=0):
    """
    递归解析表达式树
    
    返回:
        - 表达式数据字典
        - 处理到的行索引
    """
    if start_idx >= len(lines):
        return None, start_idx
    
    line = lines[start_idx].strip()
    start_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    
    # 定义支持的操作符
    op_mapping = {
        "Plus:": {"op": "add", "is_linear": True},
        "And:": {"op": "and", "is_linear": False},
        "Minus:": {"op": "sub", "is_linear": True},
        "Times:": {"op": "mul", "is_linear": True},
        "Xor:": {"op": "xor", "is_linear": False},
        "Or:": {"op": "or", "is_linear": False},
        "Eq:": {"op": "eq", "is_linear": False},
        "NotEq:": {"op": "neq", "is_linear": False},
        "LessThan:": {"op": "lt", "is_linear": False},
        "GreaterThan:": {"op": "gt", "is_linear": False},
        "LessEq:": {"op": "le", "is_linear": False},
        "GreaterEq:": {"op": "ge", "is_linear": False}
    }
    
    # 检查当前行是否是操作符
    for op_key, op_info in op_mapping.items():
        if op_key in line:
            result = {
                "operation": op_info["op"],
                "operands": [],
                "is_linear": op_info["is_linear"]
            }
            
            # 解析操作数 - 二元操作
            current_idx = start_idx + 1
            
            # 第一个操作数
            first_operand_data, current_idx = extract_operand(lines, current_idx, start_indent)
            if first_operand_data:
                result["operands"].append(first_operand_data)
                
            # 第二个操作数
            second_operand_data, current_idx = extract_operand(lines, current_idx, start_indent)
            if second_operand_data:
                result["operands"].append(second_operand_data)
                
            return result, current_idx
            
    # 如果不是操作符，检查是否是标识符（叶子节点）
    if "Identifier:" in line:
        match = re.search(r"Identifier:\s+(\w+)", line)
        if match:
            return match.group(1), start_idx + 1
            
    # 检查是否是数字常量
    if "IntConst:" in line:
        match = re.search(r"IntConst:\s+(\d+)", line)
        if match:
            return int(match.group(1)), start_idx + 1
            
    # 未识别的表达式类型
    return None, start_idx + 1

def extract_operand(lines, start_idx, parent_indent):
    """
    提取一个操作数，可能是嵌套表达式或标识符
    
    返回:
        - 操作数数据
        - 处理到的下一行索引
    """
    if start_idx >= len(lines):
        return None, start_idx
        
    line = lines[start_idx].strip()
    current_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    
    # 如果缩进比父级小，则可能已经超出了当前表达式的范围
    if current_indent < parent_indent:
        return None, start_idx
    
    # 检查是否是操作符，表示嵌套表达式
    op_keys = ["Plus:", "And:", "Minus:", "Times:", "Xor:", "Or:", 
               "Eq:", "NotEq:", "LessThan:", "GreaterThan:", "LessEq:", "GreaterEq:"]
    
    for op_key in op_keys:
        if op_key in line:
            # 是嵌套操作，递归解析
            nested_expr, next_idx = parse_expression_tree(lines, start_idx)
            if nested_expr:
                return nested_expr, next_idx
    
    # 检查是否是标识符
    if "Identifier:" in line:
        match = re.search(r"Identifier:\s+(\w+)", line)
        if match:
            return match.group(1), start_idx + 1
            
    # 检查是否是数字常量
    if "IntConst:" in line:
        match = re.search(r"IntConst:\s+(\d+)", line)
        if match:
            return int(match.group(1)), start_idx + 1
            
    return None, start_idx + 1

def generate_ir_nodes(ast_data):
    """从AST数据生成IR节点列表"""
    ir_nodes = []
    temp_counter = 0
    
    for assignment in ast_data["assignments"]:
        # 获取输出变量
        output = assignment["output"]
        operation = assignment["operation"]
        operands = assignment["operands"]
        is_linear = assignment["is_linear"]
        
        # 如果有嵌套操作，递归处理
        nodes, operand_refs = process_complex_expression(operands, operation, output, is_linear, temp_counter)
        temp_counter += len(nodes)
        ir_nodes.extend(nodes)
    
    return ir_nodes
    
def process_complex_expression(expression, op_type, output, is_linear, temp_counter):
    """
    处理可能包含嵌套表达式的表达式
    
    返回:
        - 生成的IR节点列表
        - 操作数引用列表（用于父节点）
    """
    nodes = []
    operand_refs = []
    
    if not isinstance(expression, list):
        # 单个表达式
        expression = [expression]
    
    for i, operand in enumerate(expression):
        if isinstance(operand, dict) and "operation" in operand:
            # 嵌套表达式，需要创建临时变量
            temp_var = f"_temp{temp_counter + len(nodes)}"
            sub_nodes, sub_refs = process_complex_expression(
                operand["operands"],
                operand["operation"],
                temp_var,
                operand["is_linear"],
                temp_counter + len(nodes)
            )
            nodes.extend(sub_nodes)
            operand_refs.append(temp_var)
        else:
            # 简单操作数
            operand_refs.append(operand)
    
    # 创建当前表达式的节点
    nodes.append(IRNode(op_type, operand_refs, output, is_linear))
    
    return nodes, operand_refs

# 主函数：从AST到IR节点转换
def ast_to_ir_nodes(ast_data):
    return generate_ir_nodes(ast_data)