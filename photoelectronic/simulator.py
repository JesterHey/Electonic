from photoelectronic.onn import ONNProcessor
from photoelectronic.python_processor import PythonProcessor

class Simulator:
    def __init__(self, ir_nodes):
        self.ir_nodes = ir_nodes
        self.onn = ONNProcessor()
        self.py_processor = PythonProcessor()
        self.outputs = {}

    def run(self, inputs):
        for node in self.ir_nodes:
            if node.is_linear:
                # 线性运算（加法）
                a = inputs[node.operands[0]]
                b = inputs[node.operands[1]]
                self.outputs[node.output] = self.onn.compute([a, b])  # 传递列表
            else:
                # 非线性运算（逻辑与）
                operands = [inputs[op] for op in node.operands]
                self.outputs[node.output] = self.py_processor.compute_and(operands)  # 传递列表
        return self.outputs