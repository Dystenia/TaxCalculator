"""Eingabedaten des Steuerrechners, ohne fachliche Berechnungslogik."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Mapping


class HouseholdStatus(str, Enum):
    SINGLE = "ledig"
    SINGLE_PARENT = "alleinerziehend"
    MARRIED = "verheiratet"


class EmploymentType(str, Enum):
    EMPLOYED = "angestellt"
    SELF_EMPLOYED = "selbstständig"


class ProfileValidationError(ValueError):
    """Enthält feldbezogene Fehlermeldungen für ungültige Formulareingaben."""

    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors
        super().__init__("Die Eingaben sind unvollständig oder ungültig.")


@dataclass(frozen=True)
class TaxProfile:
    """Erfasste Angaben; Einkommensart, Zeitraum und Währung bleiben offen."""

    tax_class: int
    household_status: HouseholdStatus
    employment_type: EmploymentType
    income_value: Decimal
    pension_insurance_applicable: bool


def profile_from_form(form: Mapping[str, str]) -> TaxProfile:
    """Validiert Formularwerte und erstellt ein Datenmodell ohne Berechnungen."""
    errors: dict[str, str] = {}

    raw_tax_class = form.get("tax_class", "").strip()
    try:
        tax_class = int(raw_tax_class)
        if str(tax_class) != raw_tax_class or tax_class not in range(1, 7):
            raise ValueError
    except ValueError:
        errors["tax_class"] = "Bitte wählen Sie eine Steuerklasse von 1 bis 6."
        tax_class = 0

    try:
        household_status = HouseholdStatus(form.get("household_status", ""))
    except ValueError:
        errors["household_status"] = "Bitte wählen Sie einen Familienstand aus."
        household_status = HouseholdStatus.SINGLE

    try:
        employment_type = EmploymentType(form.get("employment_type", ""))
    except ValueError:
        errors["employment_type"] = "Bitte wählen Sie eine Beschäftigungsart aus."
        employment_type = EmploymentType.EMPLOYED

    raw_income = form.get("income_value", "").strip()
    try:
        income_value = Decimal(raw_income)
        if not income_value.is_finite():
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        errors["income_value"] = "Bitte geben Sie einen gültigen Zahlenwert ein."
        income_value = Decimal(0)

    raw_pension = form.get("pension_insurance_applicable", "")
    if raw_pension not in ("ja", "nein"):
        errors["pension_insurance_applicable"] = "Bitte wählen Sie Ja oder Nein."
        pension_applicable = False
    else:
        pension_applicable = raw_pension == "ja"

    if errors:
        raise ProfileValidationError(errors)

    return TaxProfile(
        tax_class=tax_class,
        household_status=household_status,
        employment_type=employment_type,
        income_value=income_value,
        pension_insurance_applicable=pension_applicable,
    )
