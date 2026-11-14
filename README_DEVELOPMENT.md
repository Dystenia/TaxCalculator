# TaxCalculator – erster ausführbarer MVP

Python 3.10+; keine zusätzlichen Pakete nötig.

## Start

```powershell
python main.py
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Fachliche Grenze

Die Desktop-Anwendung prüft derzeit ausschließlich die arithmetische Brutto-Netto-Abrechnung.
Lohnsteuer, Solidaritätszuschlag, Kirchensteuer und Arbeitnehmerbeiträge werden **nicht**
automatisch ermittelt. Diese Beträge sind anhand einer Abrechnung oder verifizierter
amtlicher Berechnung einzugeben. Der Rechner ist **kein fertiger Steuerrechner** und
keine Steuerberatung.

## Geplante Erweiterung

- BMF-Programmablaufplan für Lohnsteuer mit versionierten Steuerjahren
- Sozialversicherung mit versionierten Beitragssätzen und Beitragsbemessungsgrenzen
- Steuerklassen 1–6, Kinder, Bundesland, Mehrfachbeschäftigung
- Referenztests gegen amtliche Ergebnisse
- Sichere Mehrdatei-Änderungen durch AgentFactory
