import unittest
from decimal import Decimal

from tax_model import (
    EmploymentType,
    HouseholdStatus,
    ProfileValidationError,
    profile_from_form,
)


class ProfileFromFormTests(unittest.TestCase):
    def valid_form(self):
        return {
            "tax_class": "3",
            "household_status": "verheiratet",
            "employment_type": "selbstständig",
            "income_value": "1234.56",
            "pension_insurance_applicable": "nein",
        }

    def test_creates_profile_without_interpreting_income(self):
        profile = profile_from_form(self.valid_form())
        self.assertEqual(profile.tax_class, 3)
        self.assertEqual(profile.household_status, HouseholdStatus.MARRIED)
        self.assertEqual(profile.employment_type, EmploymentType.SELF_EMPLOYED)
        self.assertEqual(profile.income_value, Decimal("1234.56"))
        self.assertFalse(profile.pension_insurance_applicable)

    def test_accepts_negative_numeric_value_without_business_assumption(self):
        form = self.valid_form()
        form["income_value"] = "-50"
        self.assertEqual(profile_from_form(form).income_value, Decimal("-50"))

    def test_reports_invalid_fields(self):
        form = self.valid_form()
        form.update({"tax_class": "7", "income_value": "not-a-number"})
        with self.assertRaises(ProfileValidationError) as raised:
            profile_from_form(form)
        self.assertIn("tax_class", raised.exception.errors)
        self.assertIn("income_value", raised.exception.errors)

    def test_requires_all_confirmed_choices(self):
        with self.assertRaises(ProfileValidationError) as raised:
            profile_from_form({})
        self.assertEqual(
            set(raised.exception.errors),
            {"tax_class", "household_status", "employment_type", "income_value", "pension_insurance_applicable"},
        )


if __name__ == "__main__":
    unittest.main()
