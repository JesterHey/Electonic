class PythonProcessor:
    @staticmethod
    def compute_and(operands):
        if not operands:
            return False
        result = operands[0]
        for operand in operands[1:]:
            result = result and operand
        return result

    @staticmethod
    def compute_or(operands):
        if not operands:
            return False
        result = operands[0]
        for operand in operands[1:]:
            result = result or operand
        return result

    @staticmethod
    def compute_xor(operands):
        if not operands:
            return False
        result = bool(operands[0])
        for operand in operands[1:]:
            result = result != bool(operand)
        return result

    @staticmethod
    def compute_eq(operands):
        if len(operands) < 2:
            return True  # 只有一个元素与自身相等
        return operands[0] == operands[1]

    @staticmethod
    def compute_neq(operands):
        if len(operands) < 2:
            return False  # 只有一个元素与自身相等
        return operands[0] != operands[1]

    @staticmethod
    def compute_lt(operands):
        if len(operands) < 2:
            return False
        return operands[0] < operands[1]

    @staticmethod
    def compute_gt(operands):
        if len(operands) < 2:
            return False
        return operands[0] > operands[1]

    @staticmethod
    def compute_le(operands):
        if len(operands) < 2:
            return False
        return operands[0] <= operands[1]

    @staticmethod
    def compute_ge(operands):
        if len(operands) < 2:
            return False
        return operands[0] >= operands[1]