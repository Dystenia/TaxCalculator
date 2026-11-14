import unittest
from decimal import Decimal
from taxcalculator.core import PayrollInput, InputError, calculate


class PayrollTests(unittest.TestCase):
    def values(self, **changes):
        data = dict(gross="3000", wage_tax="400", solidarity="0",
                    church_tax="30", pension="279", unemployment="39",
                    health="240", nursing="54")
        data.update(changes)
        return PayrollInput.from_values(**data)

    def test_net_and_totals(self):
        result = calculate(self.values())
        self.assertEqual(result.taxes, Decimal("430.00"))
        self.assertEqual(result.social_insurance, Decimal("612.00"))
        self.assertEqual(result.net, Decimal("1958.00"))

    def test_negative_rejected(self):
        with self.assertRaises(InputError):
            self.values(gross="-1")

    def test_nonfinite_rejected(self):
        with self.assertRaises(InputError):
            self.values(gross="NaN")

    def test_excess_deductions_rejected(self):
        with self.assertRaises(InputError):
            calculate(self.values(gross="100"))

    def test_comma_decimal(self):
        self.assertEqual(self.values(gross="1234,56").gross, Decimal("1234.56"))


if __name__ == "__main__":
    unittest.main()
