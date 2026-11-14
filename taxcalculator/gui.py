"""Dark-mode desktop payroll review UI; unverified deductions are never estimated."""
import tkinter as tk
from tkinter import ttk, messagebox
from .core import PayrollInput, calculate, InputError

BG = "#111827"
PANEL = "#1f2937"
FIELD = "#293548"
TEXT = "#f3f4f6"
MUTED = "#9ca3af"
ACCENT = "#38bdf8"

DEDUCTIONS = (
    ("wage_tax", "Lohnsteuer laut BMF / Abrechnung"),
    ("solidarity", "Solidaritätszuschlag"),
    ("church_tax", "Kirchensteuer"),
    ("pension", "Rentenversicherung (AN)"),
    ("unemployment", "Arbeitslosenversicherung (AN)"),
    ("health", "Krankenversicherung (AN)"),
    ("nursing", "Pflegeversicherung (AN)"),
)
STATES = (
    "Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen",
    "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen",
    "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen",
    "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen",
)


def main():
    root = tk.Tk()
    root.title("TaxCalculator · Dark Mode")
    root.geometry("950x780")
    root.minsize(650, 570)
    root.configure(bg=BG)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Dark.TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("Dark.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
    style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 20, "bold"))
    style.configure("Dark.TEntry", fieldbackground=FIELD, foreground=TEXT, insertcolor=TEXT, borderwidth=0, padding=7)
    style.configure("Dark.TCombobox", fieldbackground=FIELD, background=FIELD, foreground=TEXT, arrowcolor=TEXT, padding=6)
    style.map("Dark.TCombobox", fieldbackground=[("readonly", FIELD)], foreground=[("readonly", TEXT)])
    style.configure("Action.TButton", background=ACCENT, foreground="#07131f", font=("Segoe UI", 11, "bold"), padding=11)
    style.map("Action.TButton", background=[("active", "#7dd3fc")])

    outer = ttk.Frame(root, style="Dark.TFrame", padding=20)
    outer.pack(fill="both", expand=True)
    ttk.Label(outer, text="TAXCALCULATOR", style="Title.TLabel").pack(anchor="w")
    tk.Label(outer, text="Gehaltsabrechnung · Deutschland · Dark Mode",
             bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 14))

    canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)
    content = ttk.Frame(canvas, style="Dark.TFrame")
    window_id = canvas.create_window((0, 0), window=content, anchor="nw")
    content.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

    def section(title):
        panel = ttk.Frame(content, style="Panel.TFrame", padding=17)
        panel.pack(fill="x", pady=(0, 12))
        ttk.Label(panel, text=title, style="Dark.TLabel",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        grid = ttk.Frame(panel, style="Panel.TFrame")
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=1)
        return panel, grid

    def entry(grid, row, label, default=""):
        ttk.Label(grid, text=label, style="Dark.TLabel").grid(row=row, column=0, sticky="w", pady=5, padx=(0, 12))
        value = ttk.Entry(grid, style="Dark.TEntry")
        value.insert(0, default)
        value.grid(row=row, column=1, sticky="ew", pady=5)
        return value

    def choice(grid, row, label, options, default=None):
        ttk.Label(grid, text=label, style="Dark.TLabel").grid(row=row, column=0, sticky="w", pady=5, padx=(0, 12))
        value = ttk.Combobox(grid, style="Dark.TCombobox", values=options, state="readonly")
        value.set(default or options[0])
        value.grid(row=row, column=1, sticky="ew", pady=5)
        return value

    _, personal = section("01  Beschäftigung und Steuermerkmale")
    tax_class = choice(personal, 0, "Steuerklasse", tuple(str(n) for n in range(1, 7)), "3")
    state = choice(personal, 1, "Bundesland", STATES, "Schleswig-Holstein")
    church = choice(personal, 2, "Kirchensteuerpflicht", ("Nein", "Ja"))
    children = entry(personal, 3, "Kinderfreibetrag (Angabe)", "0")
    employment = choice(personal, 4, "Beschäftigungsart",
                        ("Angestellt", "Minijob", "Selbstständig", "Sonstige"))
    multiple = choice(personal, 5, "Weitere Beschäftigung", ("Nein", "Ja"))
    pension = choice(personal, 6, "Rentenversicherungspflicht", ("Ja", "Nein", "Ungeklärt"))
    health = choice(personal, 7, "Krankenversicherung", ("Gesetzlich", "Privat", "Sonstige"))
    period = choice(personal, 8, "Abrechnungszeitraum", ("Monat", "Jahr"))

    _, values = section("02  Brutto und verifizierte Abzüge")
    gross = entry(values, 0, "Bruttobetrag (€)", "3000,00")
    deductions = {key: entry(values, i + 1, label, "0,00")
                  for i, (key, label) in enumerate(DEDUCTIONS)}
    ttk.Label(values,
              text="Abzüge werden NICHT aus Steuerklasse oder Versicherungsmerkmalen abgeleitet.",
              style="Muted.TLabel", wraplength=570).grid(
                  row=len(DEDUCTIONS) + 1, column=0, columnspan=2, sticky="w", pady=(8, 0))

    output, _ = section("03  Ergebnis")
    result = tk.Label(output, text="Noch keine Berechnung", bg=PANEL, fg=ACCENT,
                      font=("Segoe UI", 15, "bold"), justify="left", anchor="w")
    result.pack(fill="x", pady=5)
    ttk.Label(output,
              text="Die Steuer- und Versicherungsmerkmale sind für die spätere automatische "
                   "Berechnung vorbereitet. Der aktuelle Stand ist ausschließlich ein "
                   "Brutto-Netto-Prüfrechner mit manuell bestätigten Abzügen.",
              style="Muted.TLabel", wraplength=720).pack(anchor="w", fill="x", pady=(6, 12))

    def run():
        try:
            data = PayrollInput.from_values(
                gross=gross.get(),
                **{key: widget.get() for key, widget in deductions.items()}
            )
            calculated = calculate(data)
        except InputError as exc:
            messagebox.showerror("Eingabefehler", str(exc), parent=root)
            return
        result.configure(text=(
            f"Brutto: {calculated.gross:,.2f} €\n"
            f"Steuern: {calculated.taxes:,.2f} €\n"
            f"Sozialversicherung: {calculated.social_insurance:,.2f} €\n"
            f"Netto: {calculated.net:,.2f} €"
        ))

    ttk.Button(output, text="Abrechnung prüfen", style="Action.TButton",
               command=run).pack(anchor="w")
    root.mainloop()


if __name__ == "__main__":
    main()
