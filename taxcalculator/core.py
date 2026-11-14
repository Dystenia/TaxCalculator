"""Deterministic payroll arithmetic; tax rates are supplied, never invented."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class InputError(ValueError):
    pass


def euro(value):
    try:
        number = Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError) as exc:
        raise InputError("Ungültiger Eurobetrag.") from exc
    if not number.is_finite() or number < 0:
        raise InputError("Betrag muss endlich und nicht negativ sein.")
    return number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PayrollInput:
    gross: Decimal
    wage_tax: Decimal
    solidarity: Decimal
    church_tax: Decimal
    pension: Decimal
    unemployment: Decimal
    health: Decimal
    nursing: Decimal

    @classmethod
    def from_values(cls, **values):
        expected = set(cls.__dataclass_fields__)
        if set(values) != expected:
            raise InputError("Erforderliche Felder: " + ", ".join(sorted(expected)))
        return cls(**{key: euro(value) for key, value in values.items()})


@dataclass(frozen=True)
class PayrollResult:
    gross: Decimal
    taxes: Decimal
    social_insurance: Decimal
    net: Decimal


def calculate(data: PayrollInput) -> PayrollResult:
    taxes = data.wage_tax + data.solidarity + data.church_tax
    social = data.pension + data.unemployment + data.health + data.nursing
    net = data.gross - taxes - social
    if net < 0:
        raise InputError("Abzüge übersteigen das Brutto. Eingaben prüfen.")
    return PayrollResult(data.gross, taxes, social, net)
