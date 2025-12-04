import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date
from pathlib import Path

from app.reports import kpis_by_lot, monthly_summary, lots_overview
from app.dao.lots import list_active_lots
from app.utils.pdf import export_table_pdf


class ReportsFrame(ttk.Frame):
	def __init__(self, master):
		super().__init__(master, padding=8)
		self._build()

	def _build(self):
		nb = ttk.Notebook(self)
		nb.pack(fill=tk.BOTH, expand=True)

		# Lot report tab
		tab_lot = ttk.Frame(nb)
		nb.add(tab_lot, text="Par lot")
		self._build_lot_tab(tab_lot)

		# Monthly tab
		tab_month = ttk.Frame(nb)
		nb.add(tab_month, text="Mensuel")
		self._build_month_tab(tab_month)

		# Overview tab
		tab_over = ttk.Frame(nb)
		nb.add(tab_over, text="Vue d'ensemble")
		self._build_overview_tab(tab_over)

	def _build_lot_tab(self, parent):
		frm = ttk.Frame(parent, padding=8)
		frm.pack(fill=tk.BOTH, expand=True)
		self._lots = list_active_lots()
		choices = [f"{l['id']} - {l['type_animal']}" for l in self._lots]
		self.v_lot = tk.StringVar()
		row = 0
		tk.Label(frm, text="Lot").grid(row=row, column=0, sticky="w")
		cb = ttk.Combobox(frm, textvariable=self.v_lot, values=choices, state="readonly", width=18)
		cb.grid(row=row, column=1, pady=4)
		row += 1
		self.lbl_kpi = ttk.Label(frm, text="")
		self.lbl_kpi.grid(row=row, column=0, columnspan=2, sticky="w", pady=6)
		row += 1
		ttk.Button(frm, text="Calculer", command=self._calc_lot).grid(row=row, column=0, pady=4)
		ttk.Button(frm, text="Exporter PDF", command=self._export_lot_pdf).grid(row=row, column=1, pady=4)

	def _parse_selected_lot(self):
		val = self.v_lot.get()
		if not val:
			return None
		return int(val.split(" - ", 1)[0])

	def _calc_lot(self):
		lot_id = self._parse_selected_lot()
		if not lot_id:
			messagebox.showinfo("Info", "Choisissez un lot")
			return
		k = kpis_by_lot(lot_id)
		self.lbl_kpi.configure(text=f"Initial: {k['initial']:.0f}, Morts: {k['morts']:.0f} ({k['mortalite_pct']:.1f}%), Vendus: {k['vendus']:.0f}, Restants: {k['restants']:.0f}, Dépenses: {k['depenses']:.0f} XAF, Recettes: {k['recettes']:.0f} XAF, Marge: {k['marge']:.0f} XAF")

	def _export_lot_pdf(self):
		lot_id = self._parse_selected_lot()
		if not lot_id:
			messagebox.showinfo("Info", "Choisissez un lot")
			return
		k = kpis_by_lot(lot_id)
		path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Exporter rapport lot")
		if not path:
			return
		headers = ["Initial", "Morts", "% Mortalité", "Vendus", "Restants", "Dépenses", "Recettes", "Marge"]
		row = [f"{k['initial']:.0f}", f"{k['morts']:.0f}", f"{k['mortalite_pct']:.1f}", f"{k['vendus']:.0f}", f"{k['restants']:.0f}", f"{k['depenses']:.0f}", f"{k['recettes']:.0f}", f"{k['marge']:.0f}"]
		export_table_pdf(Path(path), f"Rapport par lot #{lot_id}", headers, [row])
		messagebox.showinfo("Export", "PDF généré")

	def _build_month_tab(self, parent):
		frm = ttk.Frame(parent, padding=8)
		frm.pack(fill=tk.BOTH, expand=True)
		self.v_year = tk.IntVar(value=date.today().year)
		self.v_month = tk.IntVar(value=date.today().month)
		row = 0
		tk.Label(frm, text="Année").grid(row=row, column=0, sticky="w")
		tk.Entry(frm, textvariable=self.v_year, width=8).grid(row=row, column=1, pady=4)
		row += 1
		tk.Label(frm, text="Mois (1-12)").grid(row=row, column=0, sticky="w")
		tk.Entry(frm, textvariable=self.v_month, width=8).grid(row=row, column=1, pady=4)
		row += 1
		self.lbl_month = ttk.Label(frm, text="")
		self.lbl_month.grid(row=row, column=0, columnspan=2, sticky="w", pady=6)
		row += 1
		ttk.Button(frm, text="Calculer", command=self._calc_month).grid(row=row, column=0, pady=4)
		ttk.Button(frm, text="Exporter PDF", command=self._export_month_pdf).grid(row=row, column=1, pady=4)

	def _calc_month(self):
		y = int(self.v_year.get())
		m = int(self.v_month.get())
		sumry = monthly_summary(y, m)
		self.lbl_month.configure(text=f"Dépenses: {sumry['depenses']:.0f} XAF    Recettes: {sumry['recettes']:.0f} XAF    Solde: {sumry['solde']:.0f} XAF")

	def _export_month_pdf(self):
		y = int(self.v_year.get())
		m = int(self.v_month.get())
		sumry = monthly_summary(y, m)
		path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Exporter rapport mensuel")
		if not path:
			return
		headers = ["Dépenses", "Recettes", "Solde"]
		row = [f"{sumry['depenses']:.0f}", f"{sumry['recettes']:.0f}", f"{sumry['solde']:.0f}"]
		export_table_pdf(Path(path), f"Rapport mensuel {y}-{m:02d}", headers, [row])
		messagebox.showinfo("Export", "PDF généré")

	def _build_overview_tab(self, parent):
		frm = ttk.Frame(parent, padding=8)
		frm.pack(fill=tk.BOTH, expand=True)
		cols = ("id", "espece", "initial", "morts", "mort%", "vendus", "restants")
		self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=18)
		for k, t in zip(cols, ["ID", "Espèce", "Initial", "Morts", "%", "Vendus", "Restants"]):
			self.tree.heading(k, text=t)
		self.tree.pack(fill=tk.BOTH, expand=True)
		self._refresh_overview()
		btn = ttk.Button(frm, text="Exporter PDF", command=self._export_overview_pdf)
		btn.pack(pady=6)

	def _refresh_overview(self):
		for i in self.tree.get_children():
			self.tree.delete(i)
		for r in lots_overview():
			self.tree.insert("", tk.END, values=(r["id"], r["type_animal"], r["nombre_initial"], r["morts"], f"{r['mortalite_pct']:.1f}", r["vendus"], r["restants"]))

	def _export_overview_pdf(self):
		path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Exporter vue d'ensemble")
		if not path:
			return
		rows = []
		for item in self.tree.get_children():
			rows.append(list(self.tree.item(item, "values")))
		export_table_pdf(Path(path), "Vue d'ensemble des lots", ["ID", "Espèce", "Initial", "Morts", "%", "Vendus", "Restants"], rows)
		messagebox.showinfo("Export", "PDF généré")


