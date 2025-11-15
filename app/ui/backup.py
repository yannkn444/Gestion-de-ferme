import subprocess
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from app.config import get_config
from app.utils.export import export_table_csv, export_table_excel
from app.utils.pdf import export_table_pdf


TABLES = [
	"utilisateurs",
	"lots",
	"soins",
	"mortalites",
	"ventes_animaux",
	"depenses",
	"recettes",
	"stocks",
	"journal_activites",
]


class BackupFrame(ttk.Frame):
	def __init__(self, master):
		super().__init__(master, padding=8)
		self._build()

	def _build(self):
		title = ttk.Label(self, text="Export / Backup", font=("Segoe UI", 14))
		title.pack(anchor="w", pady=(0, 8))

		# Export CSV/Excel
		exp = ttk.LabelFrame(self, text="Export CSV/Excel", padding=8)
		exp.pack(fill=tk.X, pady=6)
		row = 0
		for tbl in TABLES:
			frm = ttk.Frame(exp)
			frm.grid(row=row, column=0, sticky="w", pady=2)
			lbl = ttk.Label(frm, text=tbl, width=18)
			lbl.pack(side=tk.LEFT)
			btnc = ttk.Button(frm, text="CSV", command=lambda t=tbl: self._export_csv(t))
			btnc.pack(side=tk.LEFT, padx=4)
			btne = ttk.Button(frm, text="Excel", command=lambda t=tbl: self._export_excel(t))
			btne.pack(side=tk.LEFT)
			row += 1

		# Backup / Restore SQL
		br = ttk.LabelFrame(self, text="Sauvegarde / Restauration base", padding=8)
		br.pack(fill=tk.X, pady=6)
		btn_b = ttk.Button(br, text="Sauvegarder (.sql)", command=self._backup)
		btn_b.pack(side=tk.LEFT, padx=4)
		btn_r = ttk.Button(br, text="Restaurer (.sql)", command=self._restore)
		btn_r.pack(side=tk.LEFT, padx=4)

		# Guide utilisateur
		guide = ttk.LabelFrame(self, text="Guide utilisateur", padding=8)
		guide.pack(fill=tk.X, pady=6)
		btn_g = ttk.Button(guide, text="Générer Guide (PDF)", command=self._guide)
		btn_g.pack(side=tk.LEFT, padx=4)

	def _export_csv(self, table: str):
		path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title=f"Exporter {table} en CSV")
		if not path:
			return
		try:
			export_table_csv(table, Path(path))
			messagebox.showinfo("Export", f"{table} exporté en CSV")
		except Exception as e:
			messagebox.showerror("Erreur", str(e))

	def _export_excel(self, table: str):
		path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], title=f"Exporter {table} en Excel")
		if not path:
			return
		try:
			export_table_excel(table, Path(path))
			messagebox.showinfo("Export", f"{table} exporté en Excel")
		except Exception as e:
			messagebox.showerror("Erreur", str(e))

	def _backup(self):
		cfg = get_config()
		path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL", "*.sql")], title="Sauvegarder la base")
		if not path:
			return
		cmd = [
			"mysqldump",
			f"-h{cfg.db_host}",
			f"-P{cfg.db_port}",
			f"-u{cfg.db_user}",
			f"-p{cfg.db_password}",
			cfg.db_name,
		]
		try:
			with open(path, "w", encoding="utf-8") as f:
				proc = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, shell=False)
				if proc.returncode != 0:
					raise RuntimeError(proc.stderr.strip() or "mysqldump a échoué")
			messagebox.showinfo("Backup", "Sauvegarde terminée")
		except FileNotFoundError:
			messagebox.showerror("Erreur", "mysqldump introuvable. Ajoutez MySQL bin au PATH.")
		except Exception as e:
			messagebox.showerror("Erreur", str(e))

	def _restore(self):
		cfg = get_config()
		path = filedialog.askopenfilename(filetypes=[("SQL", "*.sql")], title="Choisir un fichier .sql")
		if not path:
			return
		cmd = [
			"mysql",
			f"-h{cfg.db_host}",
			f"-P{cfg.db_port}",
			f"-u{cfg.db_user}",
			f"-p{cfg.db_password}",
			cfg.db_name,
		]
		try:
			with open(path, "r", encoding="utf-8") as f:
				proc = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True, shell=False)
				if proc.returncode != 0:
					raise RuntimeError(proc.stderr.strip() or "mysql restore a échoué")
			messagebox.showinfo("Restore", "Restauration terminée")
		except FileNotFoundError:
			messagebox.showerror("Erreur", "mysql introuvable. Ajoutez MySQL bin au PATH.")
		except Exception as e:
			messagebox.showerror("Erreur", str(e))

	def _guide(self):
		path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Enregistrer le guide utilisateur")
		if not path:
			return
		# Minimal guide content as a table
		headers = ["Module", "Actions principales"]
		rows = [
			["Connexion", "Saisir email + mot de passe"],
			["Lots", "Créer / Modifier / Clôturer, Mortalité, Vente partielle"],
			["Soins", "Ajouter / Modifier / Supprimer (lié à un lot)"],
			["Stocks", "Nouvel article, Entrée/Sortie, Seuil d'alerte"],
			["Finances", "Dépenses & Recettes, Filtres dates/lot, Résumé"],
			["Rapports", "Par lot, Mensuel, Vue d'ensemble, Export PDF"],
			["Outils", "Export CSV/Excel, Backup/Restore SQL, Guide PDF"],
		]
		try:
			export_table_pdf(Path(path), "Guide utilisateur - FarmManager", headers, rows)
			messagebox.showinfo("Guide", "Guide utilisateur généré")
		except Exception as e:
			messagebox.showerror("Erreur", str(e))


