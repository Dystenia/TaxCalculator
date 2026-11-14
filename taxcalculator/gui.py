"""Dependency-free desktop UI. Does not guess tax brackets or contribution rates."""
import tkinter as tk
from tkinter import ttk, messagebox
from .core import PayrollInput, calculate, InputError

FIELDS = (
    ("gross", "Monatsbrutto"),
    ("wage_tax", "Lohnsteuer laut Abrechnung / BMF"),
    ("solidarity", "Solidaritätszuschlag"),
    ("church_tax", "Kirchensteuer"),
    ("pension", "Rentenversicherung (AN)"),
    ("unemployment", "Arbeitslosenversicherung (AN)"),
    ("health", "Krankenversicherung (AN)"),
    ("nursing", "Pflegeversicherung (AN)"),
)


def main():
    root = tk.Tk()
    root.title("TaxCalculator · Gehaltsabrechnung")
    root.geometry("700x530")
    root.minsize(530, 470)
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Brutto-Netto-Prüfrechner", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(
        frame,
        text="MVP: Abzüge müssen aus einer verifizierten Quelle eingegeben werden. "
             "Keine automatische Steuerberechnung.",
        wraplength=640,
    ).pack(anchor="w", pady=(8, 16))
    entries = {}
    form = ttk.Frame(frame)
    form.pack(fill="x")
    for row, (key, label) in enumerate(FIELDS):
        ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=5)
        entry = ttk.Entry(form, width=20)
        entry.insert(0, "0,00")
        entry.grid(row=row, column=1, sticky="ew", padx=(18, 0), pady=5)
        entries[key] = entry
    form.columnconfigure(1, weight=1)
    result_label = ttk.Label(frame, text="Noch keine Berechnung", font=("Segoe UI", 12))
    result_label.pack(anchor="w", pady=16)

    def run():
        try:
            values = {key: entry.get() for key, entry in entries.items()}
            result = calculate(PayrollInput.from_values(**values))
        except InputError as exc:
            messagebox.showerror("Eingabefehler", str(exc), parent=root)
            return
        result_label.config(
            text=f"Steuern: {result.taxes:.2f} €    Sozialabgaben: "
                 f"{result.social_insurance:.2f} €\nNetto: {result.net:.2f} €"
        )

    ttk.Button(frame, text="Netto berechnen", command=run).pack(anchor="w")
    root.mainloop()


if __name__ == "__main__":
    main()
