"""Einfache Weboberfläche auf Basis der Python-Standardbibliothek."""

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from tax_model import ProfileValidationError, TaxProfile, profile_from_form


HOST = "127.0.0.1"
PORT = 8000
MAX_REQUEST_BYTES = 16_384


def _selected(current: str, candidate: str) -> str:
    return " selected" if current == candidate else ""


def _field_error(errors: dict[str, str], field: str) -> str:
    message = errors.get(field)
    if not message:
        return ""
    return f'<p class="error" role="alert">{escape(message)}</p>'


def render_page(
    values: dict[str, str] | None = None,
    errors: dict[str, str] | None = None,
    profile: TaxProfile | None = None,
) -> str:
    """Rendert Formular und Status, zeigt ausdrücklich keine Berechnung an."""
    values = values or {}
    errors = errors or {}

    def value(name: str) -> str:
        return escape(values.get(name, ""), quote=True)

    tax_options = '<option value="">Bitte auswählen</option>' + "".join(
        f'<option value="{number}"{_selected(values.get("tax_class", ""), str(number))}>{number}</option>'
        for number in range(1, 7)
    )
    household_options = '<option value="">Bitte auswählen</option>' + "".join(
        f'<option value="{escape(item)}"{_selected(values.get("household_status", ""), item)}>{escape(item)}</option>'
        for item in ("ledig", "alleinerziehend", "verheiratet")
    )
    employment_options = '<option value="">Bitte auswählen</option>' + "".join(
        f'<option value="{escape(item)}"{_selected(values.get("employment_type", ""), item)}>{escape(item)}</option>'
        for item in ("angestellt", "selbstständig")
    )
    pension_options = '<option value="">Bitte auswählen</option>' + "".join(
        f'<option value="{item}"{_selected(values.get("pension_insurance_applicable", ""), item)}>{item.capitalize()}</option>'
        for item in ("ja", "nein")
    )

    submitted = ""
    if profile is not None:
        submitted = f"""
        <section aria-labelledby="submitted-heading">
          <h2 id="submitted-heading">Erfasste Angaben</h2>
          <dl>
            <dt>Steuerklasse</dt><dd>{profile.tax_class}</dd>
            <dt>Familienstand</dt><dd>{escape(profile.household_status.value)}</dd>
            <dt>Beschäftigungsart</dt><dd>{escape(profile.employment_type.value)}</dd>
            <dt>Eingegebener Einkommenswert</dt><dd>{escape(str(profile.income_value))}</dd>
            <dt>Rentenversicherung anwendbar</dt><dd>{'Ja' if profile.pension_insurance_applicable else 'Nein'}</dd>
          </dl>
        </section>
        """

    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Steuerrechner – Eingaben</title>
  <style>
    body {{ font: 1rem/1.5 system-ui, sans-serif; max-width: 48rem; margin: 2rem auto; padding: 0 1rem; color: #202124; }}
    label {{ display: block; margin-top: 1rem; font-weight: 600; }}
    input, select, button {{ box-sizing: border-box; width: 100%; max-width: 32rem; padding: .55rem; font: inherit; }}
    button {{ margin-top: 1.25rem; cursor: pointer; }}
    .notice {{ padding: 1rem; border-left: .3rem solid #805500; background: #fff7df; }}
    .error {{ color: #a00000; }}
    dt {{ font-weight: 600; margin-top: .5rem; }}
  </style>
</head>
<body>
  <h1>Steuerrechner</h1>
  <p class="notice" role="status"><strong>Berechnung noch nicht verfügbar.</strong>
    Für diese Anwendung sind noch keine Berechnungsgrundlagen festgelegt.
    Es werden keine Steuer- oder Versicherungsbeträge berechnet oder angezeigt.</p>
  <p>Der Einkommenswert wird ohne Festlegung von Einkommensart, Zeitraum oder Währung erfasst. Angaben werden nicht dauerhaft gespeichert.</p>
  <form method="post" action="/">
    <label for="tax_class">Steuerklasse</label>
    <select id="tax_class" name="tax_class" required>{tax_options}</select>
    {_field_error(errors, 'tax_class')}

    <label for="household_status">Familienstand</label>
    <select id="household_status" name="household_status" required>{household_options}</select>
    {_field_error(errors, 'household_status')}

    <label for="employment_type">Beschäftigungsart</label>
    <select id="employment_type" name="employment_type" required>{employment_options}</select>
    {_field_error(errors, 'employment_type')}

    <label for="income_value">Einkommenswert</label>
    <input id="income_value" name="income_value" type="number" step="any" value="{value('income_value')}" required>
    {_field_error(errors, 'income_value')}

    <label for="pension_insurance_applicable">Rentenversicherung anwendbar</label>
    <select id="pension_insurance_applicable" name="pension_insurance_applicable" required>{pension_options}</select>
    {_field_error(errors, 'pension_insurance_applicable')}

    <button type="submit">Angaben erfassen</button>
  </form>
  {submitted}
</body>
</html>"""


def _read_form(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    raw_length = handler.headers.get("Content-Length", "0")
    try:
        length = int(raw_length)
    except ValueError as exc:
        raise ValueError("Ungültige Anfragegröße.") from exc
    if length < 0 or length > MAX_REQUEST_BYTES:
        raise ValueError("Die Anfrage ist zu groß oder ungültig.")
    body = handler.rfile.read(length).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True, strict_parsing=False)
    return {key: entries[0] for key, entries in parsed.items() if entries}


class TaxCalculatorHandler(BaseHTTPRequestHandler):
    def _send_html(self, status: int, content: str) -> None:
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path != "/":
            self._send_html(404, "<!doctype html><html lang=\"de\"><meta charset=\"utf-8\"><title>Nicht gefunden</title><p>Seite nicht gefunden.</p></html>")
            return
        self._send_html(200, render_page())

    def do_POST(self) -> None:
        if self.path != "/":
            self._send_html(404, "<!doctype html><html lang=\"de\"><meta charset=\"utf-8\"><title>Nicht gefunden</title><p>Seite nicht gefunden.</p></html>")
            return
        try:
            values = _read_form(self)
        except (ValueError, UnicodeDecodeError):
            self._send_html(400, "<!doctype html><html lang=\"de\"><meta charset=\"utf-8\"><title>Ungültige Anfrage</title><p>Die Anfrage konnte nicht gelesen werden.</p></html>")
            return
        try:
            profile = profile_from_form(values)
        except ProfileValidationError as exc:
            self._send_html(400, render_page(values=values, errors=exc.errors))
            return
        self._send_html(200, render_page(values=values, profile=profile))


def run_server() -> None:
    server = ThreadingHTTPServer((HOST, PORT), TaxCalculatorHandler)
    print(f"Steuerrechner erreichbar unter http://{HOST}:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer wird beendet.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
