import unittest
from decimal import Decimal

from tax_model import EmploymentType, HouseholdStatus, TaxProfile
from web import render_page


class RenderPageTests(unittest.TestCase):
    def test_form_contains_confirmed_choices_and_unavailable_notice(self):
        page = render_page()
        for choice in ("1", "2", "3", "4", "5", "6", "ledig", "alleinerziehend", "verheiratet", "angestellt", "selbstständig", "Ja", "Nein"):
            self.assertIn(choice, page)
        self.assertIn("Berechnung noch nicht verfügbar", page)
        self.assertIn("keine Steuer- oder Versicherungsbeträge berechnet", page)

    def test_submitted_values_are_shown_without_calculated_amounts(self):
        profile = TaxProfile(
            tax_class=1,
            household_status=HouseholdStatus.SINGLE,
            employment_type=EmploymentType.EMPLOYED,
            income_value=Decimal("100"),
            pension_insurance_applicable=True,
        )
        page = render_page(profile=profile)
        self.assertIn("Erfasste Angaben", page)
        self.assertIn("Eingegebener Einkommenswert</dt><dd>100", page)
        self.assertIn("Berechnung noch nicht verfügbar", page)
        self.assertNotIn("Ergebnisbetrag", page)

    def test_user_values_are_escaped(self):
        page = render_page(values={"income_value": '"<script>alert(1)</script>'})
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;", page)


if __name__ == "__main__":
    unittest.main()
