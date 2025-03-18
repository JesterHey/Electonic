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
    # 不删除括号，因为它们可能包含重要的位置信息
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
            expression = parse_expression_tree(lines, i+1)
            if expression:
                assignment["operation"] = expression["operation"]
                assignment["operands"] = expression["operands"]
                assignment["is_linear"] = expression["is_linear"]
            break
    
    return assignment

def parse_expression_tree(lines, start_idx):
    """递归解析表达式树"""
    if start_idx >= len(lines):
        return None
    
    line = lines[start_idx].strip()
    
    # 1. 检查是否是操作符
    op_mapping = {
        "Plus:": {"op": "add", "linear": True},
        "And:": {"op": "and", "linear": False},
        "Minus:": {"op": "sub", "linear": True},
        "Times:": {"op": "mul", "linear": True},
        "Xor:": {"op": "xor", "linear": False},
        "Or:": {"op": "or", "linear": False},
        "Eq:": {"op": "eq", "linear": False},
        "NotEq:": {"op": "neq", "linear": False},
        "LessThan:": {"op": "lt", "linear": False},
        "GreaterThan:": {"op": "gt", "linear": False},
        "LessEq:": {"op": "le", "linear": False},
        "GreaterEq:": {"op": "ge", "linear": False}
    }
    
    for op_key, op_info in op_mapping.items():
        if op_key in line:
            # 是操作符，递归解析其操作数
            result = {
                "operation": op_info["op"],
                "operands": [],
                "is_linear": op_info["linear"]
            }
            
            # 操作数可能是嵌套操作或标识符，需要逐个检查
            operands = []
            i = start_idx + 1
            while i < len(lines):
                current_line = lines[i].strip()
                indent = len(lines[i]) - len(lines[i].lstrip())
                
                # 检查是否是操作数
                if "Identifier:" in current_line:
                    match = re.search(r"Identifier:\s+(\w+)", current_line)
                    if match:
                        operands.append(match.group(1))
                        i += 1
                        continue
                
                # 检查是否是嵌套操作
                nested_op = False
                for op in op_mapping.keys():
                    if op in current_line:
                        # 是嵌套操作，递归解析
                        nested_expr = parse_expression_tree(lines, i)
                        if nested_expr:
                            # 为嵌套表达式创建中间变量
                            temp_var = f"_temp{len(operands)}"
                            
                            # 添加临时变量作为当前操作的操作数
                            operands.append({
                                "temp_var": temp_var,
                                "operation": nested_expr["operation"],
                                "operands": nested_expr["operands"],
                                "is_linear": nested_expr["is_linear"]
                            })
                            
                            # 跳过已处理的嵌套操作
                            nested_depth = 1
                            j = i + 1
                            while j < len(lines) and nested_depth > 0:
                                j_line = lines[j].strip()
                                j_indent = len(lines[j]) - len(lines[j].lstrip())
                                
                                # 更简单的方法：基于缩进判断何时退出嵌套
                                if j_indent <= indent and j > i + 1:
                                    break
                                j += 1
                            
                            i = j
                            nested_op = True
                            break
                
                if nested_op:
                    continue
                
                # 如果当前行不是操作数也不是嵌套操作，可能已经超出当前表达式的范围
                if i > start_idx + 1:  # 确保已经处理了至少一个操作数
                    # 检查缩进是否返回到上一级别，表示退出当前表达式
                    if indent <= (len(lines[start_idx]) - len(lines[start_idx].lstrip())):
                        break
                
                i += 1
            
            result["operands"] = operands
            return result
    
    # 2. 如果不是操作符，检查是否是标识符（叶子节点）
    if "Identifier:" in line:
        match = re.search(r"Identifier:\s+(\w+)", line)
        if match:
            return {
                "operation": None,
                "operands": [match.group(1)],
                "is_linear": True
            }
    
    return None

def flatten_nested_expressions(assignments):
    """将嵌套表达式转换为一系列IRNode对象"""
    ir_nodes = []
    temp_counter = 0
    
    for assign in assignments:
        output = assign["output"]
        operation = assign["operation"]
        is_linear = assign["is_linear"]
        
        # 处理操作数，可能包含嵌套表达式
        final_operands = []
        for operand in assign["operands"]:
            if isinstance(operand, dict) and "temp_var" in operand:
                # 是嵌套表达式，需要先处理
                temp_var = operand["temp_var"]
                nested_nodes = process_nested_expression(operand, temp_var, temp_counter)
                ir_nodes.extend(nested_nodes)
                final_operands.append(temp_var)
                temp_counter += 1
            else:
                # 是简单标识符
                final_operands.append(operand)
        
        # 创建当前赋值的IRNode
        ir_nodes.append(IRNode(operation, final_operands, output, is_linear))
    
    return ir_nodes

def process_nested_expression(expr, output_var, temp_counter):
    """递归处理嵌套表达式，返回IRNode列表"""
    nodes = []
    
    # 处理当前表达式的操作数
    final_operands = []
    for operand in expr["operands"]:
        if isinstance(operand, dict) and "temp_var" in operand:
            # 递归处理嵌套操作数
            nested_var = f"_nested{temp_counter}"
            nested_nodes = process_nested_expression(operand, nested_var, temp_counter+1)
            nodes.extend(nested_nodes)
            final_operands.append(nested_var)
        else:
            final_operands.append(operand)
    
    # 创建当前表达式的IRNode
    nodes.append(IRNode(
        expr["operation"],
        final_operands,
        output_var,
        expr["is_linear"]
    ))
    
    return nodes

def ast_to_ir_nodes(ast_data):
    """将解析后的AST数据转换为IRNode对象列表"""
    # 首先处理嵌套表达式
    ir_nodes = []
    
    for assign in ast_data["assignments"]:
        temp_vars = {}  # 用于存储临时变量
        
        # 递归处理表达式树
        operands, nodes = process_operands(assign["operands"], temp_vars)
        ir_nodes.extend(nodes)
        
        # 添加最终输出节点
        ir_nodes.append(IRNode(
            assign["operation"],
            operands,
            assign["output"],
            assign["is_linear"]
        ))
    
    return ir_nodes

def process_operands(operands, temp_vars, temp_counter=[0]):
    """处理操作数列表，返回(处理后的操作数, 生成的IR节点)"""
    processed = []
    nodes = []
    
    for operand in operands:
        if isinstance(operand, dict) and "operation" in operand:
            # 嵌套表达式
            temp_var = f"_temp{temp_counter[0]}"
            temp_counter[0] += 1
            
            # 递归处理嵌套表达式的操作数
            sub_operands, sub_nodes = process_operands(
                operand["operands"],
                temp_vars,
                temp_counter
            )
            
            # 添加子节点
            nodes.extend(sub_nodes)
            
            # 添加表示嵌套表达式的节点
            nodes.append(IRNode(
                operand["operation"],
                sub_operands,
                temp_var,
                operand["is_linear"]
            ))
            
            processed.append(temp_var)
            temp_vars[temp_var] = True
        else:
            # 简单操作数
            processed.append(operand)
    
    return processed, nodes