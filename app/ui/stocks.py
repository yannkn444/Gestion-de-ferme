import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from app.dao.stocks import list_stocks, create_product, add_entry, add_exit, set_threshold


class ProductForm(tk.Toplevel):
	def __init__(self, master, on_saved):
		super().__init__(master)
		self.title("Nouvel article")
		self.resizable(False, False)
		self._on_saved = on_saved

		frm = ttk.Frame(self, padding=12)
		frm.grid()

		self.v_nom = tk.StringVar()
		self.v_type = tk.StringVar()
		self.v_qty = tk.IntVar(value=0)
		self.v_unite = tk.StringVar()
		self.v_seuil = tk.IntVar(value=0)

		row = 0
		ttk.Label(frm, text="Nom produit").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_nom, width=24).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Type").grid(row=row, column=0, sticky="w")
		cb = ttk.Combobox(frm, textvariable=self.v_type, values=["Aliment", "Médicament", "Matériel"], state="readonly")
		cb.grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Quantité initiale").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_qty, width=18).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Unité").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_unite, width=18).grid(row=row, column=1, pady=4)
		row += 1
		ttk.Label(frm, text="Seuil d'alerte").grid(row=row, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_seuil, width=18).grid(row=row, column=1, pady=4)
		row += 1
		btn = ttk.Button(frm, text="Créer", command=self._save)
		btn.grid(row=row, column=0, columnspan=2, pady=8, sticky="ew")

	def _save(self):
		if not self.v_nom.get().strip() or not self.v_type.get():
			messagebox.showwarning("Validation", "Nom et type requis")
			return
		create_product(self.v_nom.get().strip(), self.v_type.get(), int(self.v_qty.get()), self.v_unite.get() or None, int(self.v_seuil.get()))
		self._on_saved()
		self.destroy()


class ThresholdForm(tk.Toplevel):
	def __init__(self, master, stock_id: int, on_saved):
		super().__init__(master)
		self.title("Définir seuil")
		self.resizable(False, False)
		self._stock_id = stock_id
		self._on_saved = on_saved
		frm = ttk.Frame(self, padding=12)
		frm.grid()
		self.v_seuil = tk.IntVar(value=0)
		ttk.Label(frm, text="Seuil d'alerte").grid(row=0, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_seuil, width=18).grid(row=0, column=1, pady=4)
		ttk.Button(frm, text="Enregistrer", command=self._save).grid(row=1, column=0, columnspan=2, pady=8, sticky="ew")

	def _save(self):
		set_threshold(self._stock_id, int(self.v_seuil.get()))
		self._on_saved()
		self.destroy()


class MoveForm(tk.Toplevel):
	def __init__(self, master, stock_id: int, is_entry: bool, on_saved):
		super().__init__(master)
		self.title("Entrée stock" if is_entry else "Sortie stock")
		self.resizable(False, False)
		self._stock_id = stock_id
		self._is_entry = is_entry
		self._on_saved = on_saved

		frm = ttk.Frame(self, padding=12)
		frm.grid()
		self.v_qty = tk.IntVar(value=1)
		ttk.Label(frm, text="Quantité").grid(row=0, column=0, sticky="w")
		ttk.Entry(frm, textvariable=self.v_qty, width=18).grid(row=0, column=1, pady=4)
		ttk.Button(frm, text="Valider", command=self._save).grid(row=1, column=0, columnspan=2, pady=8, sticky="ew")

	def _save(self):
		qty = int(self.v_qty.get())
		try:
			if self._is_entry:
				add_entry(self._stock_id, qty)
			else:
				add_exit(self._stock_id, qty)
		except Exception as e:
			messagebox.showerror("Erreur", str(e))
			return
		self._on_saved()
		self.destroy()


class StocksFrame(ttk.Frame):
	def __init__(self, master):
		super().__init__(master, padding=8)
		self._build()
		self._refresh()

	def _build(self):
		toolbar = ttk.Frame(self)
		toolbar.pack(fill=tk.X)
		self.btn_new = ttk.Button(toolbar, text="Nouvel article", command=self._new)
		self.btn_new.pack(side=tk.LEFT)
		self.btn_in = ttk.Button(toolbar, text="Entrée", command=self._entry)
		self.btn_in.pack(side=tk.LEFT, padx=6)
		self.btn_out = ttk.Button(toolbar, text="Sortie", command=self._exit)
		self.btn_out.pack(side=tk.LEFT)
		self.btn_thr = ttk.Button(toolbar, text="Seuil", command=self._threshold)
		self.btn_thr.pack(side=tk.LEFT, padx=6)

		cols = ("id", "nom", "type", "quantite", "unite", "seuil")
		self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
		self.tree.heading("id", text="ID")
		self.tree.heading("nom", text="Nom")
		self.tree.heading("type", text="Type")
		self.tree.heading("quantite", text="Quantité")
		self.tree.heading("unite", text="Unité")
		self.tree.heading("seuil", text="Seuil")
		self.tree.pack(fill=tk.BOTH, expand=True, pady=6)

	def _refresh(self):
		for i in self.tree.get_children():
			self.tree.delete(i)
		for row in list_stocks():
			vals = (row["id"], row["nom_produit"], row["type_produit"], row.get("quantite", 0), row.get("unite"), row.get("seuil", 0))
			item = self.tree.insert("", tk.END, values=vals)
			# low stock highlighting
			try:
				if row.get("seuil") and row.get("quantite", 0) <= row.get("seuil"):
					self.tree.item(item, tags=("low",))
			except Exception:
				pass
		self.tree.tag_configure("low", background="#ffe6e6")

	def _selected_id(self) -> Optional[int]:
		item = self.tree.selection()
		if not item:
			return None
		vals = self.tree.item(item[0], "values")
		return int(vals[0])

	def _new(self):
		ProductForm(self, self._refresh)

	def _entry(self):
		id_ = self._selected_id()
		if not id_:
			messagebox.showinfo("Info", "Sélectionnez un article")
			return
		MoveForm(self, id_, True, self._refresh)

	def _exit(self):
		id_ = self._selected_id()
		if not id_:
			messagebox.showinfo("Info", "Sélectionnez un article")
			return
		MoveForm(self, id_, False, self._refresh)

	def _threshold(self):
		id_ = self._selected_id()
		if not id_:
			messagebox.showinfo("Info", "Sélectionnez un article")
			return
		ThresholdForm(self, id_, self._refresh)


