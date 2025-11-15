import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from app.dao.soins import list_soins, create_soin, update_soin, delete_soin
from app.dao.lots import list_active_lots
from app.utils.validators import is_valid_date, parse_positive_float


class SoinForm(tk.Toplevel):
	def __init__(self, master, soin_id: Optional[int], initial: Optional[dict], on_saved):
		super().__init__(master)
		self.title("Soin - Édition" if soin_id else "Soin - Nouveau")
		self.resizable(False, False)
		self._soin_id = soin_id
		self._on_saved = on_saved

		self._lots = list_active_lots()
		self._lot_choices = [f"{l['id']} - {l['type_animal']}" for l in self._lots]

		frm = ttk.Frame(self, padding=12)
		frm.grid()

		self.v_lot = tk.StringVar()
		self.v_date = tk.StringVar()
		self.v_type = tk.StringVar()
		self.v_desc = tk.StringVar()
		self.v_cout = tk.StringVar(value="0")
		self.v_user = tk.StringVar()

		row = 0
		ttk.Label(frm, text="Lot").grid(row=row, column=0, sticky="w")
		cb = ttk.Combobox(frm, textvariable=self.v_lot, values=self._lot_choices, state="readonly", width=24)
		cb.grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Date (YYYY-MM-DD)").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_date, width=18).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Type de soin").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_type, width=22).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Description").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_desc, width=22).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Coût (XAF)").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_cout, width=18).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Effectué par").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_user, width=22).grid(row=row, column=1, pady=4)
		row += 1
		btn = ttk.Button(frm, text="Enregistrer", command=self._save)
		btn.grid(row=row, column=0, columnspan=2, pady=8, sticky="ew")

		if initial:
			self._prefill(initial)

	def _prefill(self, soin: dict):
		self.v_lot.set(f"{soin['lot_id']} - {soin.get('type_animal','')}")
		self.v_date.set(str(soin["date_soin"]))
		self.v_type.set(soin["type_soin"])
		self.v_desc.set(soin.get("description") or "")
		self.v_cout.set(str(soin.get("cout") or 0))
		self.v_user.set(soin.get("effectue_par") or "")

	def _parse_lot_id(self) -> Optional[int]:
		val = self.v_lot.get()
		if not val:
			return None
		try:
			return int(val.split(" - ", 1)[0])
		except Exception:
			return None

	def _save(self):
		lot_id = self._parse_lot_id()
		if not lot_id or not self.v_date.get().strip() or not self.v_type.get().strip():
			messagebox.showwarning("Validation", "Lot, date et type sont requis")
			return
		try:
			cout = parse_positive_float(self.v_cout.get() or "0") if (self.v_cout.get() and float(self.v_cout.get()) != 0) else 0.0
		except Exception:
			messagebox.showwarning("Validation", "Coût invalide")
			return
		if not is_valid_date(self.v_date.get()):
			messagebox.showwarning("Validation", "Date invalide (YYYY-MM-DD)")
			return
		if self._soin_id:
			update_soin(self._soin_id, lot_id, self.v_date.get(), self.v_type.get().strip(), self.v_desc.get() or None, cout, self.v_user.get() or None)
		else:
			create_soin(lot_id, self.v_date.get(), self.v_type.get().strip(), self.v_desc.get() or None, cout, self.v_user.get() or None)
		self._on_saved()
		self.destroy()


class SoinsFrame(ttk.Frame):
	def __init__(self, master):
		super().__init__(master, padding=8)
		self._build()
		self._refresh()

	def _build(self):
		toolbar = ttk.Frame(self)
		toolbar.pack(fill=tk.X)
		self.btn_new = ttk.Button(toolbar, text="Nouveau soin", command=self._new)
		self.btn_new.pack(side=tk.LEFT)
		self.btn_edit = ttk.Button(toolbar, text="Modifier", command=self._edit)
		self.btn_edit.pack(side=tk.LEFT, padx=6)
		self.btn_del = ttk.Button(toolbar, text="Supprimer", command=self._delete)
		self.btn_del.pack(side=tk.LEFT)

		cols = ("id", "lot", "espece", "date", "type", "cout", "effectue_par")
		self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
		self.tree.heading("id", text="ID")
		self.tree.heading("lot", text="Lot")
		self.tree.heading("espece", text="Espèce")
		self.tree.heading("date", text="Date")
		self.tree.heading("type", text="Type")
		self.tree.heading("cout", text="Coût")
		self.tree.heading("effectue_par", text="Effectué par")
		self.tree.pack(fill=tk.BOTH, expand=True, pady=6)

	def _refresh(self):
		for i in self.tree.get_children():
			self.tree.delete(i)
		for row in list_soins():
			self.tree.insert("", tk.END, values=(
				row["id"], row["lot_id"], row.get("type_animal"), str(row["date_soin"]), row["type_soin"], row.get("cout", 0), row.get("effectue_par")
			))

	def _selected_id(self) -> Optional[int]:
		item = self.tree.selection()
		if not item:
			return None
		values = self.tree.item(item[0], "values")
		return int(values[0])

	def _get_row(self) -> Optional[dict]:
		item = self.tree.selection()
		if not item:
			return None
		vals = self.tree.item(item[0], "values")
		return {
			"id": int(vals[0]),
			"lot_id": int(vals[1]),
			"type_animal": vals[2],
			"date_soin": vals[3],
			"type_soin": vals[4],
			"cout": float(vals[5]) if vals[5] not in (None, "") else 0,
			"effectue_par": vals[6],
		}

	def _new(self):
		SoinForm(self, None, None, self._refresh)

	def _edit(self):
		row = self._get_row()
		if not row:
			messagebox.showinfo("Info", "Sélectionnez un soin")
			return
		SoinForm(self, row["id"], row, self._refresh)

	def _delete(self):
		id_ = self._selected_id()
		if not id_:
			messagebox.showinfo("Info", "Sélectionnez un soin")
			return
		if messagebox.askyesno("Confirmation", "Supprimer ce soin ?"):
			delete_soin(id_)
			self._refresh()


