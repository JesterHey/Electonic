class ASTNode:
    """AST节点基类"""
    def __init__(self, line, indent_level, line_number):
        self.line = line.strip()
        self.indent_level = indent_level
        self.line_number = line_number
        self.children = []
        
    def add_child(self, node):
        self.children.append(node)
        
    def get_type(self):
        """获取节点类型"""
        parts = self.line.split(':')
        if len(parts) > 0:
            return parts[0].strip()
        return ""
        
    def get_value(self):
        """获取节点值"""
        parts = self.line.split(':')
        if len(parts) > 1:
            value_part = parts[1].strip()
            # 去除可能的括号内容
            if '(' in value_part:
                value_part = value_part.split('(')[0].strip()
            return value_part
        return ""
    
    def find_children_by_type(self, node_type):
        """查找特定类型的子节点"""
        result = []
        for child in self.children:
            if child.get_type() == node_type:
                result.append(child)
        return result
    
    def find_first_child_by_type(self, node_type):
        """查找第一个特定类型的子节点"""
        for child in self.children:
            if child.get_type() == node_type:
                return child
        return None
    
    def __str__(self):
        return f"{self.get_type()}: {self.get_value()}"


class ASTParser:
    """AST解析器"""
    def __init__(self, ast_file):
        self.ast_file = ast_file
        self.lines = []
        self.root = None
        
    def parse(self):
        """解析AST文件"""
        # 读取文件
        with open(self.ast_file, 'r') as f:
            self.lines = f.readlines()
        
        # 构建AST树
        self.root = self._build_ast_tree()
        
        # 提取信息
        return self._extract_verilog_info()
    
    def _build_ast_tree(self):
        """构建AST树结构"""
        if not self.lines:
            return None
            
        # 创建根节点
        first_line = self.lines[0]
        indent = len(first_line) - len(first_line.lstrip())
        root = ASTNode(first_line, indent, 0)
        
        # 使用栈来跟踪当前的父节点路径
        stack = [root]
        
        # 从第二行开始解析
        for i, line in enumerate(self.lines[1:], 1):
            if not line.strip():
                continue
                
            # 计算当前行的缩进级别
            current_indent = len(line) - len(line.lstrip())
            
            # 创建当前行的节点
            current_node = ASTNode(line, current_indent, i)
            
            # 调整栈，找到当前节点的父节点
            while stack and stack[-1].indent_level >= current_indent:
                stack.pop()
                
            if stack:  # 有父节点
                stack[-1].add_child(current_node)
                
            # 将当前节点压入栈中
            stack.append(current_node)
            
        return root
    
    def _extract_verilog_info(self):
        """从AST树中提取Verilog模块信息"""
        if not self.root:
            return None
            
        # 查找模块定义节点
        module_def = self._find_module_def(self.root)
        if not module_def:
            return {"error": "未找到模块定义"}
            
        # 提取模块名称
        module_name = module_def.get_value()
        
        # 提取端口列表
        port_list = module_def.find_first_child_by_type("Portlist")
        inputs, outputs = self._extract_ports(port_list)
        
        # 提取赋值语句
        assigns = module_def.find_children_by_type("Assign")
        operations = self._extract_operations(assigns)
        
        return {
            "module_name": module_name,
            "inputs": inputs,
            "outputs": outputs,
            "operations": operations
        }
    
    def _find_module_def(self, node):
        """递归查找模块定义节点"""
        if node.get_type() == "ModuleDef":
            return node
            
        for child in node.children:
            result = self._find_module_def(child)
            if result:
                return result
                
        return None
    
    def _extract_ports(self, port_list):
        """提取输入输出端口"""
        inputs = []
        outputs = []
        
        if not port_list:
            return inputs, outputs
            
        # 遍历所有IO端口
        io_ports = port_list.find_children_by_type("Ioport")
        for io_port in io_ports:
            # 查找Input节点
            input_node = io_port.find_first_child_by_type("Input")
            if input_node:
                port_info = self._extract_port_info(input_node)
                if port_info:
                    inputs.append(port_info)
                continue
                
            # 查找Output节点
            output_node = io_port.find_first_child_by_type("Output")
            if output_node:
                port_info = self._extract_port_info(output_node)
                if port_info:
                    outputs.append(port_info)
        
        return inputs, outputs
    
    def _extract_port_info(self, port_node):
        """提取端口信息"""
        if not port_node:
            return None
            
        # 提取端口名称
        name_parts = port_node.get_value().split(',')
        if not name_parts:
            return None
            
        port_name = name_parts[0].strip()
        
        # 提取端口宽度
        width_node = port_node.find_first_child_by_type("Width")
        width = self._extract_width(width_node)
        
        return {
            "name": port_name,
            "width": width
        }
    
    def _extract_width(self, width_node):
        """提取信号宽度"""
        if not width_node:
            return [0, 0]
            
        # 查找IntConst节点
        int_consts = width_node.find_children_by_type("IntConst")
        if len(int_consts) >= 2:
            msb = int(int_consts[0].get_value())
            lsb = int(int_consts[1].get_value())
            return [msb, lsb]
            
        return [0, 0]
    
    def _extract_operations(self, assign_nodes):
        """提取操作赋值"""
        operations = []
        
        for assign_node in assign_nodes:
            # 提取左值
            lvalue_node = assign_node.find_first_child_by_type("Lvalue")
            if not lvalue_node:
                continue
                
            lvalue = self._extract_identifier(lvalue_node)
            
            # 提取右值
            rvalue_node = assign_node.find_first_child_by_type("Rvalue")
            if not rvalue_node:
                continue
                
            # 提取运算表达式
            rvalue_expr = self._extract_expression(rvalue_node)
            
            operations.append({
                "lvalue": lvalue,
                "expression": rvalue_expr
            })
        
        return operations
    
    def _extract_identifier(self, node):
        """提取标识符"""
        id_node = node.find_first_child_by_type("Identifier")
        if id_node:
            return id_node.get_value()
        return ""
    
    def _extract_expression(self, node):
        """递归提取表达式"""
        # 检查是否为基本类型
        for child in node.children:
            # 如果是标识符
            if child.get_type() == "Identifier":
                return {
                    "type": "identifier",
                    "value": child.get_value()
                }
                
            # 如果是常量
            elif child.get_type() == "IntConst":
                return {
                    "type": "constant",
                    "value": child.get_value()
                }
                
            # 如果是运算符
            elif child.get_type() in ["Plus", "Minus", "Times", "Divide", "Xor", "And", "Or"]:
                operands = []
                for operand_node in child.children:
                    operand_expr = self._extract_expression(operand_node)
                    if operand_expr:
                        operands.append(operand_expr)
                
                return {
                    "type": "operation",
                    "operator": child.get_type().lower(),
                    "operands": operands
                }
        
        # 如果没有直接子节点，递归检查下一层
        for child in node.children:
            result = self._extract_expression(child)
            if result:
                return result
                
        return None


class VerilogASTVisualizer:
    """AST可视化工具"""
    def __init__(self, parsed_info):
        self.info = parsed_info
    
    def print_summary(self):
        """打印模块概要信息"""
        print(f"模块名称: {self.info['module_name']}")
        
        print("\n输入端口:")
        for inp in self.info['inputs']:
            print(f"  - {inp['name']} [{inp['width'][0]}:{inp['width'][1]}]")
        
        print("\n输出端口:")
        for out in self.info['outputs']:
            print(f"  - {out['name']} [{out['width'][0]}:{out['width'][1]}]")
        
        print("\n运算赋值:")
        for op in self.info['operations']:
            expr_str = self._format_expression(op['expression'])
            print(f"  {op['lvalue']} = {expr_str}")
    
    def _format_expression(self, expr):
        """格式化表达式输出"""
        if not expr:
            return "未知表达式"
        
        if expr['type'] == 'identifier':
            return expr['value']
        
        if expr['type'] == 'constant':
            return expr['value']
        
        if expr['type'] == 'operation':
            op_map = {
                'plus': '+', 
                'minus': '-', 
                'times': '*', 
                'divide': '/', 
                'xor': '^', 
                'and': '&', 
                'or': '|'
            }
            
            op_symbol = op_map.get(expr['operator'], expr['operator'])
            
            operand_strs = []
            for operand in expr['operands']:
                operand_str = self._format_expression(operand)
                operand_strs.append(operand_str)
            
            # 根据运算符优先级添加括号
            result = f" {op_symbol} ".join(operand_strs)
            if expr['operator'] in ['times', 'divide'] and len(expr['operands']) > 1:
                return result
            else:
                return f"({result})"
        
        return "未知表达式"