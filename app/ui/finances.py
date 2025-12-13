import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from app.dao.finances import (
	list_depenses,
	create_depense,
	update_depense,
	delete_depense,
	list_recettes,
	create_recette,
	update_recette,
	delete_recette,
	summary,
)
from app.dao.lots import list_active_lots
from app.utils.validators import is_valid_date, parse_positive_float


class FilterBar(ttk.Frame):
	def __init__(self, master, on_apply):
		super().__init__(master)
		self._on_apply = on_apply
		self.v_start = tk.StringVar()
		self.v_end = tk.StringVar()
		self.v_lot = tk.StringVar()
		self._lots = list_active_lots()
		self._lot_choices = ["(tous)"] + [f"{l['id']} - {l['type_animal']}" for l in self._lots]

		ttk.Label(self, text="Du").pack(side=tk.LEFT)
		ttk.Entry(self, textvariable=self.v_start, width=12).pack(side=tk.LEFT, padx=4)
		ttk.Label(self, text="au").pack(side=tk.LEFT)
		ttk.Entry(self, textvariable=self.v_end, width=12).pack(side=tk.LEFT, padx=4)
		ttk.Label(self, text="Lot").pack(side=tk.LEFT, padx=(8, 0))
		cb = ttk.Combobox(self, textvariable=self.v_lot, values=self._lot_choices, state="readonly", width=18)
		cb.current(0)
		cb.pack(side=tk.LEFT, padx=4)
		btn = ttk.Button(self, text="Appliquer", command=self._on_apply)
		btn.pack(side=tk.LEFT, padx=8)

	def current_filters(self) -> dict:
		lot_id: Optional[int] = None
		val = self.v_lot.get()
		if val and not val.startswith("("):
			try:
				lot_id = int(val.split(" - ", 1)[0])
			except Exception:
				lot_id = None
		return {"start": self.v_start.get() or None, "end": self.v_end.get() or None, "lot_id": lot_id}


class DepenseForm(tk.Toplevel):
	def __init__(self, master, dep: Optional[dict], on_saved):
		super().__init__(master)
		self.title("Dépense - Édition" if dep else "Dépense - Nouvelle")
		self.resizable(False, False)
		self._dep = dep
		self._on_saved = on_saved

		self._lots = list_active_lots()
		choices = ["(aucun)"] + [f"{l['id']} - {l['type_animal']}" for l in self._lots]

		frm = ttk.Frame(self, padding=12)
		frm.grid()
		self.v_type = tk.StringVar()
		self.v_montant = tk.StringVar()
		self.v_date = tk.StringVar()
		self.v_desc = tk.StringVar()
		self.v_lot = tk.StringVar()

		row = 0
		ttk.Label(frm, text="Type").grid(row=row, column=0, sticky="w")
		cbt = ttk.Combobox(frm, textvariable=self.v_type, values=["Alimentation", "Soin", "Entretien", "Autre"], state="readonly")
		cbt.grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Montant (XAF)").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_montant, width=18).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Date (YYYY-MM-DD)").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_date, width=18).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Description").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_desc, width=22).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Lot").grid(row=row, column=0, sticky="w")
		cbl = ttk.Combobox(frm, textvariable=self.v_lot, values=choices, state="readonly", width=20)
		cbl.current(0)
		cbl.grid(row=row, column=1, pady=4)
		row += 1
		ttk.Button(frm, text="Enregistrer", command=self._save).grid(row=row, column=0, columnspan=2, pady=8, sticky="ew")

		if dep:
			self.v_type.set(dep["type_depense"])
			self.v_montant.set(str(dep["montant"]))
			self.v_date.set(str(dep["date_depense"]))
			self.v_desc.set(dep.get("description") or "")
			if dep.get("lot_id"):
				self.v_lot.set(f"{dep['lot_id']} - ")

	def _parse_lot_id(self) -> Optional[int]:
		val = self.v_lot.get()
		if not val or val.startswith("("):
			return None
		try:
			return int(val.split(" - ", 1)[0])
		except Exception:
			return None

	def _save(self):
		try:
			montant = parse_positive_float(self.v_montant.get())
		except Exception:
			messagebox.showwarning("Validation", "Montant invalide")
			return
		if montant <= 0 or not self.v_date.get() or not self.v_type.get():
			messagebox.showwarning("Validation", "Type, date et montant > 0 requis")
			return
		if not is_valid_date(self.v_date.get()):
			messagebox.showwarning("Validation", "Date invalide (YYYY-MM-DD)")
			return
		lot_id = self._parse_lot_id()
		if self._dep:
			update_depense(self._dep["id"], self.v_type.get(), montant, self.v_date.get(), self.v_desc.get() or None, lot_id)
		else:
			create_depense(self.v_type.get(), montant, self.v_date.get(), self.v_desc.get() or None, lot_id)
		self._on_saved()
		self.destroy()


class RecetteForm(tk.Toplevel):
	def __init__(self, master, rec: Optional[dict], on_saved):
		super().__init__(master)
		self.title("Recette - Édition" if rec else "Recette - Nouvelle")
		self.resizable(False, False)
		self._rec = rec
		self._on_saved = on_saved

		self._lots = list_active_lots()
		choices = ["(aucun)"] + [f"{l['id']} - {l['type_animal']}" for l in self._lots]

		frm = ttk.Frame(self, padding=12)
		frm.grid()
		self.v_type = tk.StringVar()
		self.v_montant = tk.StringVar()
		self.v_date = tk.StringVar()
		self.v_client = tk.StringVar()
		self.v_lot = tk.StringVar()

		row = 0
		ttk.Label(frm, text="Type").grid(row=row, column=0, sticky="w")
		cbt = ttk.Combobox(frm, textvariable=self.v_type, values=["Vente", "Produit dérivé", "Autre"], state="readonly")
		cbt.grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Montant (XAF)").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_montant, width=18).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Date (YYYY-MM-DD)").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_date, width=18).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Client").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_client, width=22).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Lot").grid(row=row, column=0, sticky="w")
		cbl = ttk.Combobox(frm, textvariable=self.v_lot, values=choices, state="readonly", width=20)
		cbl.current(0)
		cbl.grid(row=row, column=1, pady=4)
		row += 1
		ttk.Button(frm, text="Enregistrer", command=self._save).grid(row=row, column=0, columnspan=2, pady=8, sticky="ew")

		if rec:
			self.v_type.set(rec["type_recette"])
			self.v_montant.set(str(rec["montant"]))
			self.v_date.set(str(rec["date_recette"]))
			self.v_client.set(rec.get("client") or "")
			if rec.get("lot_id"):
				self.v_lot.set(f"{rec['lot_id']} - ")

	def _parse_lot_id(self) -> Optional[int]:
		val = self.v_lot.get()
		if not val or val.startswith("("):
			return None
		try:
			return int(val.split(" - ", 1)[0])
		except Exception:
			return None

	def _save(self):
		try:
			montant = parse_positive_float(self.v_montant.get())
		except Exception:
			messagebox.showwarning("Validation", "Montant invalide")
			return
		if montant <= 0 or not self.v_date.get() or not self.v_type.get():
			messagebox.showwarning("Validation", "Type, date et montant > 0 requis")
			return
		if not is_valid_date(self.v_date.get()):
			messagebox.showwarning("Validation", "Date invalide (YYYY-MM-DD)")
			return
		lot_id = self._parse_lot_id()
		if self._rec:
			update_recette(self._rec["id"], self.v_type.get(), montant, self.v_date.get(), lot_id, self.v_client.get() or None)
		else:
			create_recette(self.v_type.get(), montant, self.v_date.get(), lot_id, self.v_client.get() or None)
		self._on_saved()
		self.destroy()


class FinancesFrame(ttk.Frame):
	def __init__(self, master):
		super().__init__(master, padding=8)
		self._build()
		self._refresh()

	def _build(self):
		self.filter = FilterBar(self, self._refresh)
		self.filter.pack(fill=tk.X, pady=4)

		nb = ttk.Notebook(self)
		nb.pack(fill=tk.BOTH, expand=True)

		self.tab_dep = ttk.Frame(nb)
		nb.add(self.tab_dep, text="Dépenses")
		self.tab_rec = ttk.Frame(nb)
		nb.add(self.tab_rec, text="Recettes")

		# Dépenses
		bar_d = ttk.Frame(self.tab_dep)
		bar_d.pack(fill=tk.X)
		tk.Button(bar_d, text="Nouvelle", command=self._new_dep).pack(side=tk.LEFT)
		tk.Button(bar_d, text="Modifier", command=self._edit_dep).pack(side=tk.LEFT, padx=6)
		tk.Button(bar_d, text="Supprimer", command=self._del_dep).pack(side=tk.LEFT)
		cols_d = ("id", "type", "montant", "date", "lot", "desc")
		self.tree_dep = ttk.Treeview(self.tab_dep, columns=cols_d, show="headings", height=14)
		for k, t in zip(cols_d, ["ID", "Type", "Montant", "Date", "Lot", "Description"]):
			self.tree_dep.heading(k, text=t)
		self.tree_dep.pack(fill=tk.BOTH, expand=True, pady=6)

		# Recettes
		bar_r = ttk.Frame(self.tab_rec)
		bar_r.pack(fill=tk.X)
		tk.Button(bar_r, text="Nouvelle", command=self._new_rec).pack(side=tk.LEFT)
		tk.Button(bar_r, text="Modifier", command=self._edit_rec).pack(side=tk.LEFT, padx=6)
		tk.Button(bar_r, text="Supprimer", command=self._del_rec).pack(side=tk.LEFT)
		cols_r = ("id", "type", "montant", "date", "lot", "client")
		self.tree_rec = ttk.Treeview(self.tab_rec, columns=cols_r, show="headings", height=14)
		for k, t in zip(cols_r, ["ID", "Type", "Montant", "Date", "Lot", "Client"]):
			self.tree_rec.heading(k, text=t)
		self.tree_rec.pack(fill=tk.BOTH, expand=True, pady=6)

		# Résumé
		self.summary_label = ttk.Label(self, text="")
		self.summary_label.pack(fill=tk.X, pady=(4, 0))

	def _filters(self) -> dict:
		return self.filter.current_filters()

	def _refresh(self):
		f = self._filters()
		# Dépenses
		for i in self.tree_dep.get_children():
			self.tree_dep.delete(i)
		for d in list_depenses(f.get("start"), f.get("end"), f.get("lot_id")):
			self.tree_dep.insert("", tk.END, values=(d["id"], d["type_depense"], d["montant"], str(d["date_depense"]), d.get("lot_id") or "", (d.get("description") or "")[:60]))
		# Recettes
		for i in self.tree_rec.get_children():
			self.tree_rec.delete(i)
		for r in list_recettes(f.get("start"), f.get("end"), f.get("lot_id")):
			self.tree_rec.insert("", tk.END, values=(r["id"], r["type_recette"], r["montant"], str(r["date_recette"]), r.get("lot_id") or "", r.get("client") or ""))
		# Résumé
		sumry = summary(f.get("start"), f.get("end"), f.get("lot_id"))
		self.summary_label.configure(text=f"Dépenses: {sumry['depenses']:.0f} XAF    Recettes: {sumry['recettes']:.0f} XAF    Benefice: {sumry['solde']:.0f} XAF")

	def _sel_dep_id(self) -> Optional[int]:
		it = self.tree_dep.selection()
		if not it:
			return None
		return int(self.tree_dep.item(it[0], "values")[0])

	def _sel_rec_id(self) -> Optional[int]:
		it = self.tree_rec.selection()
		if not it:
			return None
		return int(self.tree_rec.item(it[0], "values")[0])

	def _new_dep(self):
		DepenseForm(self, None, self._refresh)

	def _edit_dep(self):
		it = self.tree_dep.selection()
		if not it:
			messagebox.showinfo("Info", "Sélectionnez une dépense")
			return
		vals = self.tree_dep.item(it[0], "values")
		dep = {"id": int(vals[0]), "type_depense": vals[1], "montant": float(vals[2]), "date_depense": vals[3], "lot_id": int(vals[4]) if vals[4] else None, "description": vals[5]}
		DepenseForm(self, dep, self._refresh)

	def _del_dep(self):
		id_ = self._sel_dep_id()
		if not id_:
			messagebox.showinfo("Info", "Sélectionnez une dépense")
			return
		if messagebox.askyesno("Confirmation", "Supprimer cette dépense ?"):
			delete_depense(id_)
			self._refresh()

	def _new_rec(self):
		RecetteForm(self, None, self._refresh)

	def _edit_rec(self):
		it = self.tree_rec.selection()
		if not it:
			messagebox.showinfo("Info", "Sélectionnez une recette")
			return
		vals = self.tree_rec.item(it[0], "values")
		rec = {"id": int(vals[0]), "type_recette": vals[1], "montant": float(vals[2]), "date_recette": vals[3], "lot_id": int(vals[4]) if vals[4] else None, "client": vals[5]}
		RecetteForm(self, rec, self._refresh)

	def _del_rec(self):
		id_ = self._sel_rec_id()
		if not id_:
			messagebox.showinfo("Info", "Sélectionnez une recette")
			return
		if messagebox.askyesno("Confirmation", "Supprimer cette recette ?"):
			delete_recette(id_)
			self._refresh()


