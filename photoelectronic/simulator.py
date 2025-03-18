from photoelectronic.onn import ONNProcessor
from photoelectronic.python_processor import PythonProcessor

class Simulator:
    def __init__(self, ir_nodes):
        self.ir_nodes = ir_nodes
        self.onn = ONNProcessor()
        self.py_processor = PythonProcessor()
        self.outputs = {}

    def run(self, inputs):
        # 复制输入到临时字典，这样我们可以在其中存储中间结果
        values = inputs.copy()
        self.outputs = {}
        
        for node in self.ir_nodes:
            # 从values字典中获取操作数值
            operand_values = []
            for op in node.operands:
                # 检查操作数类型和处理
                if isinstance(op, dict):
                    # 如果操作数是字典，需要提取实际值
                    if "value" in op:
                        operand_values.append(op["value"])
                    elif "name" in op and op["name"] in values:
                        operand_values.append(values[op["name"]])
                    else:
                        # 如果无法提取值，则添加None或者跳过
                        operand_values.append(None)
                elif isinstance(op, str) and op in values:
                    # 如果操作数是字符串并且在values中找到对应值
                    operand_values.append(values[op])
                elif isinstance(op, (int, float)):
                    # 如果操作数是数值字面量
                    operand_values.append(op)
                else:
                    # 尝试将字符串转换为整数或浮点数（如果是字面量）
                    try:
                        if isinstance(op, str):
                            operand_values.append(float(op) if '.' in op else int(op))
                        else:
                            operand_values.append(op)  # 保留原始值
                    except (ValueError, TypeError):
                        operand_values.append(op)  # 保留原始值
            
            # 如果没有操作类型，直接将第一个操作数作为结果（可能是简单赋值）
            if not node.op_type:
                if operand_values:
                    result = operand_values[0]
                else:
                    result = None
            # 根据操作类型和线性标志选择处理方法
            elif node.is_linear:
                result = self._compute_linear_operation(node.op_type, operand_values)
            else:
                result = self._compute_nonlinear_operation(node.op_type, operand_values)
            
            # 保存结果到values字典和outputs字典
            values[node.output] = result
            
            # 仅将主输出（不是临时变量）添加到self.outputs
            if not node.output.startswith('_temp'):
                self.outputs[node.output] = result
            
        return self.outputs

    def _compute_linear_operation(self, op_type, operands):
        """处理线性操作"""
        if not operands:
            return None
        
        if op_type == "add":
            # 加法操作使用ONN处理器
            result = operands[0]
            for operand in operands[1:]:
                if operand is not None:  # 确保操作数不是None
                    result = self.onn.compute([result, operand], "add")
            return result
        
        elif op_type == "sub":
            # 减法操作使用ONN处理器的减法模型
            if len(operands) >= 2:
                result = operands[0]
                for operand in operands[1:]:
                    if operand is not None:  # 确保操作数不是None
                        result = self.onn.compute([result, operand], "sub")
                return result
            return operands[0] if operands else 0
            
        elif op_type == "mul":
            # 乘法操作使用ONN处理器的乘法实现
            result = operands[0]
            for operand in operands[1:]:
                if operand is not None:  # 确保操作数不是None
                    result = self.onn.compute([result, operand], "mul")
            return result
            
        else:
            # 其他未实现的线性操作
            raise NotImplementedError(f"线性操作 {op_type} 尚未实现")

    def _compute_nonlinear_operation(self, op_type, operands):
        """处理非线性操作"""
        # 过滤掉None值
        valid_operands = [op for op in operands if op is not None]
        
        if not valid_operands:
            return None
        
        if op_type == "and":
            return self.py_processor.compute_and(valid_operands)
            
        elif op_type == "or":
            return self.py_processor.compute_or(valid_operands)
            
        elif op_type == "xor":
            return self.py_processor.compute_xor(valid_operands)
            
        elif op_type == "eq":
            return self.py_processor.compute_eq(valid_operands)
            
        elif op_type == "neq":
            return self.py_processor.compute_neq(valid_operands)
            
        elif op_type == "lt":
            return self.py_processor.compute_lt(valid_operands)
            
        elif op_type == "gt":
            return self.py_processor.compute_gt(valid_operands)
            
        elif op_type == "le":
            return self.py_processor.compute_le(valid_operands)
            
        elif op_type == "ge":
            return self.py_processor.compute_ge(valid_operands)
            
        else:
            # 其他未实现的非线性操作
            raise NotImplementedError(f"非线性操作 {op_type} 尚未实现")