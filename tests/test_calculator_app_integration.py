import unittest
from calculator_app import CalculatorApp
class TestCalculatorAppIntegration(unittest.TestCase):
    def test_addition_sequence(self):
        app = CalculatorApp()
        app.current_value = 5
        app.operator = '+'
        app.operand = 3
        app.press_equals()
        self.assertEqual(app.current_value, 8)
    def test_complex_operation(self):
        app = CalculatorApp()
        app.current_value = 10
        app.operator = '-'
        app.operand = 4
        app.press_equals()
        app.operator = '*'
        app.operand = 2
        app.press_equals()
        self.assertEqual(app.current_value, 12)
if __name__ == '__main__':
    unittest.main()
