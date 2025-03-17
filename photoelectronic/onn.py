import torch

class ONNProcessor:
    def __init__(self):
        self.model = self._build_model()
    
    def _build_model(self):
        # 定义线性层，输入维度为 2，输出维度为 1
        model = torch.nn.Linear(2, 1, bias=False)
        # 初始化权重为 [1.0, 1.0]（模拟加法）
        with torch.no_grad():
            model.weight.data = torch.tensor([[1.0, 1.0]])
        return model
    
    def compute(self, operands):
        # 转换为二维张量（batch_size=1）
        inputs = torch.tensor([operands], dtype=torch.float32)
        result = self.model(inputs).item()
        return int(result)