from calculator_logic import add, subtract, multiply, divide

class CalculatorApp:
    def __init__(self):
        self.current_value = 0
        self.operator = None
        self.operand = None
        self._input_buffer = ""

    def press_clear(self):
        self.current_value = 0
        self.operator = None
        self.operand = None
        self._input_buffer = ""

    def press_number(self, number):
        if isinstance(number, (int, float)):
            if self.operator is None:
                self.current_value = float(number) if isinstance(number, float) else number
            else:
                self.operand = float(number) if isinstance(number, float) else number
            self._input_buffer = ""
            return
        if isinstance(number, str) and number.isdigit():
            self._input_buffer += number
            val = int(self._input_buffer)
            if self.operator is None:
                self.current_value = val
            else:
                self.operand = val
        else:
            raise ValueError("Unsupported number input")

    def press_operator(self, op):
        if op not in ['+', '-', '*', '/']:
            raise ValueError("Unsupported operator")
        if self.operator is not None and self.operand is not None:
            self.press_equals()
        self.operator = op
        self._input_buffer = ""

    def press_equals(self):
        if self.operator is None or self.operand is None:
            return self.current_value
        a = self.current_value
        b = self.operand
        if self.operator == '+':
            self.current_value = add(a, b)
        elif self.operator == '-':
            self.current_value = subtract(a, b)
        elif self.operator == '*':
            self.current_value = multiply(a, b)
        elif self.operator == '/':
            self.current_value = divide(a, b)
        else:
            raise ValueError("Unsupported operator")
        self.operator = None
        self.operand = None
        self._input_buffer = ""
        return self.current_value
