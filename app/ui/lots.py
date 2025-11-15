import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from app.dao.lots import list_lots, create_lot, update_lot, get_lot, close_lot
from app.dao.lot_events import record_mortality, record_partial_sale, get_lot_counters
from app.utils.validators import is_valid_date
from app.utils.pdf import export_table_pdf, export_sale_receipt
from pathlib import Path
from tkinter import filedialog


class LotForm(tk.Toplevel):
    """
    Formulaire pour créer ou modifier les informations d'un lot d'animaux.
    """
    def __init__(self, master, lot_id: Optional[int], on_saved):
        super().__init__(master)
        self.title("Lot - Édition" if lot_id else "Lot - Nouveau")
        self.resizable(False, False)
        self._lot_id = lot_id
        self._on_saved = on_saved

        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0)

        self.var_type = tk.StringVar()
        self.var_date = tk.StringVar()
        self.var_nombre = tk.IntVar()
        self.var_poids = tk.StringVar()
        self.var_source = tk.StringVar()
        self.var_statut = tk.StringVar(value="Actif")
        self.var_remarque = tk.StringVar()

        row = 0
        ttk.Label(container, text="Espèce").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        cb = ttk.Combobox(container, textvariable=self.var_type, values=["Poulet", "Porc"], state="readonly")
        cb.grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(container, text="Date d'arrivée (YYYY-MM-DD)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(container, textvariable=self.var_date, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(container, text="Nombre initial").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(container, textvariable=self.var_nombre, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(container, text="Poids moyen (kg)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(container, textvariable=self.var_poids, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(container, text="Source").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(container, textvariable=self.var_source, width=22).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(container, text="Statut").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        cb2 = ttk.Combobox(container, textvariable=self.var_statut, values=["Actif", "Vendu", "Mort", "Abattu"], state="readonly")
        cb2.grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(container, text="Remarque").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(container, textvariable=self.var_remarque, width=22).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        btn = ttk.Button(container, text="Enregistrer", command=self._save)
        btn.grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")

        if lot_id:
            self._load()

    def _load(self):
        """Charge les données du lot pour l'édition."""
        lot = get_lot(self._lot_id)
        if not lot:
            messagebox.showerror("Erreur", "Lot introuvable")
            self.destroy()
            return
        self.var_type.set(lot["type_animal"])
        self.var_date.set(str(lot["date_arrivee"]))
        # Correction pour garantir que le nombre initial ne change pas lors de l'édition
        self.var_nombre.set(lot["nombre_initial"]) 
        self.var_poids.set("" if lot["poids_moyen"] is None else str(lot["poids_moyen"]))
        self.var_source.set(lot.get("source") or "")
        self.var_statut.set(lot["statut"]) 
        self.var_remarque.set(lot.get("remarque") or "")

    def _save(self):
        """Valide et enregistre (crée ou met à jour) le lot."""
        try:
            poids = float(self.var_poids.get()) if self.var_poids.get().strip() else None
        except ValueError:
            messagebox.showwarning("Validation", "Poids moyen invalide. Veuillez entrer un nombre.")
            return

        if not self.var_type.get() or not self.var_date.get() or self.var_nombre.get() <= 0:
            messagebox.showwarning("Validation", "Espèce, date et nombre initial sont requis.")
            return

        if not is_valid_date(self.var_date.get()):
            messagebox.showwarning("Validation", "Format de date invalide (attendu : YYYY-MM-DD)")
            return
        
        # Vérification si un changement de statut est effectué sur un lot existant
        if self._lot_id:
            current_lot = get_lot(self._lot_id)
            if current_lot and current_lot["statut"] != self.var_statut.get():
                # On utilise la fonction de clôture pour s'assurer que toutes les règles sont respectées
                if self.var_statut.get() in ["Vendu", "Mort", "Abattu"]:
                    if not messagebox.askyesno("Attention", f"Changer le statut de Lot #{self._lot_id} à '{self.var_statut.get()}' ? Cela clôturera le lot."):
                        return
                    close_lot(self._lot_id, self.var_statut.get())
                
                # Mise à jour des autres champs si le statut n'est pas changé ou s'il est changé vers "Actif"
                update_lot(
                    self._lot_id,
                    self.var_type.get(),
                    self.var_date.get(),
                    int(self.var_nombre.get()), # Ne devrait pas changer l'initial après la création
                    poids,
                    self.var_source.get() or None,
                    self.var_statut.get(),
                    self.var_remarque.get() or None,
                )
            else:
                 # Mise à jour simple sans changement de statut de clôture
                update_lot(
                    self._lot_id,
                    self.var_type.get(),
                    self.var_date.get(),
                    int(self.var_nombre.get()),
                    poids,
                    self.var_source.get() or None,
                    self.var_statut.get(),
                    self.var_remarque.get() or None,
                )

        else:
            # Création d'un nouveau lot
            create_lot(
                self.var_type.get(),
                self.var_date.get(),
                int(self.var_nombre.get()),
                poids,
                self.var_source.get() or None,
                self.var_remarque.get() or None,
            )
        self._on_saved()
        self.destroy()


class LotsFrame(ttk.Frame):
    """
    Cadre principal pour la gestion des lots d'animaux, affichant la liste et les actions.
    """
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build()
        self._refresh()

    def _build(self):
        """Construit l'interface utilisateur du cadre des lots."""
        
        # Titre
        ttk.Label(self, text="Gestion des Lots d'Animaux", 
                  font=("Segoe UI", 16, "bold"), foreground="#1C7D7D").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Barre d'outils
        toolbar = ttk.Frame(self)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.btn_new = ttk.Button(toolbar, text="Nouveau lot (Fermier)", command=self._new)
        self.btn_new.pack(side=tk.LEFT)
        self.btn_edit = ttk.Button(toolbar, text="Modifier", command=self._edit)
        self.btn_edit.pack(side=tk.LEFT, padx=6)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill='y')

        self.btn_mort = ttk.Button(toolbar, text="❌ Mortalité", command=self._mortality)
        self.btn_mort.pack(side=tk.LEFT)
        self.btn_sale = ttk.Button(toolbar, text="💰 Vente partielle", command=self._sale)
        self.btn_sale.pack(side=tk.LEFT, padx=6)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill='y')
        
        self.btn_close = ttk.Button(toolbar, text="✅ Clôturer (Vendu)", command=self._close)
        self.btn_close.pack(side=tk.LEFT)

        # Treeview pour la liste des lots
        cols = ("id", "type", "date", "nombre", "morts", "vendus", "restants", "poids", "source", "statut")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        
        # Configuration des colonnes
        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("type", width=80, anchor=tk.CENTER)
        self.tree.column("date", width=100, anchor=tk.CENTER)
        self.tree.column("nombre", width=70, anchor=tk.CENTER)
        self.tree.column("morts", width=70, anchor=tk.CENTER)
        self.tree.column("vendus", width=70, anchor=tk.CENTER)
        self.tree.column("restants", width=70, anchor=tk.CENTER)
        self.tree.column("poids", width=100, anchor=tk.CENTER)
        self.tree.column("source", width=120, anchor=tk.W)
        self.tree.column("statut", width=100, anchor=tk.CENTER)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Espèce")
        self.tree.heading("date", text="Arrivée")
        self.tree.heading("nombre", text="Initial")
        self.tree.heading("morts", text="Morts")
        self.tree.heading("vendus", text="Vendus")
        self.tree.heading("restants", text="Restants")
        self.tree.heading("poids", text="Poids moy. (kg)")
        self.tree.heading("source", text="Source")
        self.tree.heading("statut", text="Statut")
        
        self.tree.grid(row=2, column=0, sticky="nsew", pady=6)
        
        # Ajout d'une barre de défilement verticale
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=1, sticky='ns')

    def _refresh(self):
        """Charge et affiche la liste des lots depuis la base de données."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # On utilise list_lots pour récupérer les lots avec les compteurs calculés (morts, vendus, restants)
        for row in list_lots():
            # Conversion en chaînes pour un affichage propre dans le Treeview
            poids_moyen = f"{row['poids_moyen']:.2f} kg" if row.get("poids_moyen") else "-"
            
            self.tree.insert("", tk.END, values=(
                row["id"], 
                row["type_animal"], 
                str(row["date_arrivee"]), 
                row["nombre_initial"], 
                row.get("morts", 0), 
                row.get("vendus", 0), 
                row.get("restants", 0), 
                poids_moyen, 
                row.get("source") or "-", 
                row["statut"]
            ))

    def _selected_id(self) -> Optional[int]:
        """Récupère l'ID du lot sélectionné dans le Treeview."""
        item = self.tree.selection()
        if not item:
            return None
        values = self.tree.item(item[0], "values")
        return int(values[0])

    def _new(self):
        """Ouvre le formulaire pour créer un nouveau lot."""
        LotForm(self.master, None, self._refresh)

    def _edit(self):
        """Ouvre le formulaire pour modifier le lot sélectionné."""
        id_ = self._selected_id()
        if not id_:
            messagebox.showinfo("Info", "Sélectionnez un lot à modifier.")
            return
        LotForm(self.master, id_, self._refresh)

    def _close(self):
        """Clôture le lot sélectionné et le marque comme 'Vendu'."""
        id_ = self._selected_id()
        if not id_:
            messagebox.showinfo("Info", "Sélectionnez un lot à clôturer.")
            return
        lot = get_lot(id_)
        if lot["statut"] != "Actif":
            messagebox.showwarning("Clôture", f"Le lot #{id_} est déjà en statut '{lot['statut']}'")
            return
            
        counters = get_lot_counters(id_)
        
        if counters["restants"] > 0:
            if not messagebox.askyesno("Confirmation de Clôture", 
                                      f"Lot #{id_}: Il reste {counters['restants']} animaux. "
                                      "Voulez-vous vraiment clôturer ce lot en 'Vendu' ? (Les animaux restants seront comptabilisés comme vendus)."):
                return
        else:
            if not messagebox.askyesno("Confirmation", f"Clôturer Lot #{id_} en 'Vendu' ?"):
                return
            
        close_lot(id_, "Vendu")
        self._refresh()

    def _mortality(self):
        """Ouvre la boîte de dialogue pour enregistrer un événement de mortalité."""
        id_ = self._selected_id()
        if not id_:
            messagebox.showinfo("Info", "Sélectionnez un lot.")
            return
        lot = get_lot(id_)
        if lot["statut"] != "Actif":
            messagebox.showwarning("Action impossible", f"Le lot #{id_} n'est pas actif.")
            return
        self._open_mortality_dialog(id_)

    def _sale(self):
        """Ouvre la boîte de dialogue pour enregistrer une vente partielle."""
        id_ = self._selected_id()
        if not id_:
            messagebox.showinfo("Info", "Sélectionnez un lot.")
            return
        lot = get_lot(id_)
        if lot["statut"] != "Actif":
            messagebox.showwarning("Action impossible", f"Le lot #{id_} n'est pas actif.")
            return
        self._open_sale_dialog(id_)

    def _open_mortality_dialog(self, lot_id: int):
        """Dialogue pour enregistrer la mortalité."""
        dlg = tk.Toplevel(self.master)
        dlg.title(f"Mortalité - Lot #{lot_id}")
        dlg.transient(self.master)
        dlg.grab_set()
        dlg.resizable(False, False)
        frm = ttk.Frame(dlg, padding=12)
        frm.grid()
        
        v_date = tk.StringVar()
        v_q = tk.IntVar(value=0)
        v_motif = tk.StringVar()
        
        row = 0
        ttk.Label(frm, text="Date (YYYY-MM-DD)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_date, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(frm, text="Quantité décédée").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_q, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(frm, text="Motif (Optionnel)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_motif, width=22).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        
        def save():
            if v_q.get() <= 0 or not v_date.get():
                messagebox.showwarning("Validation", "Date et quantité décédée requises et positives.")
                return
            if not is_valid_date(v_date.get()):
                messagebox.showwarning("Validation", "Format de date invalide (YYYY-MM-DD).")
                return

            counters = get_lot_counters(lot_id)
            if v_q.get() > counters["restants"]:
                messagebox.showwarning("Validation", f"Quantité ({v_q.get()}) supérieure aux restants ({counters['restants']}).")
                return
            
            record_mortality(lot_id, v_date.get(), int(v_q.get()), v_motif.get() or None)
            dlg.destroy()
            self._refresh()
            
        ttk.Button(frm, text="Enregistrer la mortalité", command=save).grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")

    def _open_sale_dialog(self, lot_id: int):
        """Dialogue pour enregistrer une vente partielle."""
        dlg = tk.Toplevel(self.master)
        dlg.title(f"Vente Partielle - Lot #{lot_id}")
        dlg.transient(self.master)
        dlg.grab_set()
        dlg.resizable(False, False)
        frm = ttk.Frame(dlg, padding=12)
        frm.grid()
        
        v_date = tk.StringVar()
        v_q = tk.IntVar(value=0)
        v_px = tk.StringVar()
        v_client = tk.StringVar()
        
        row = 0
        ttk.Label(frm, text="Date (YYYY-MM-DD)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_date, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(frm, text="Quantité vendue").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_q, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(frm, text="Prix unitaire (XAF)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_px, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(frm, text="Client (Optionnel)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_client, width=22).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        
        def save():
            try:
                prix = float(v_px.get())
            except ValueError:
                messagebox.showwarning("Validation", "Prix unitaire invalide. Veuillez entrer un nombre.")
                return
                
            if v_q.get() <= 0 or not v_date.get():
                messagebox.showwarning("Validation", "Date et quantité vendue requises et positives.")
                return
                
            if not is_valid_date(v_date.get()):
                messagebox.showwarning("Validation", "Format de date invalide (YYYY-MM-DD).")
                return

            counters = get_lot_counters(lot_id)
            if v_q.get() > counters["restants"]:
                messagebox.showwarning("Validation", f"Quantité ({v_q.get()}) supérieure aux restants ({counters['restants']}).")
                return
                
            # Enregistrement de la vente
            record_partial_sale(lot_id, v_date.get(), int(v_q.get()), prix, v_client.get() or None)
            
            # Demande d'exportation du reçu
            if messagebox.askyesno("Reçu", "Voulez-vous générer un reçu PDF pour cette vente ?"):
                path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                    filetypes=[("PDF files", "*.pdf")], 
                                                    title="Enregistrer le reçu de vente")
                if path:
                    montant = int(v_q.get()) * prix
                    lot_info = get_lot(lot_id)
                    meta = {
                        "date": v_date.get(),
                        "lot_id": lot_id,
                        "type_animal": lot_info.get("type_animal", "Inconnu"),
                        "quantite": int(v_q.get()),
                        "prix_unitaire": f"{prix:,.0f} XAF".replace(",", " "),
                        "montant": f"{montant:,.0f} XAF".replace(",", " "),
                        "client": v_client.get() or "Non spécifié",
                    }
                    try:
                        export_sale_receipt(Path(path), "Reçu de Vente Animale", meta)
                        messagebox.showinfo("Succès", f"Reçu enregistré à :\n{path}")
                    except Exception as e:
                        messagebox.showerror("Erreur PDF", f"Échec de l'exportation du reçu: {e}")
            
            dlg.destroy()
            self._refresh()
            
        ttk.Button(frm, text="Enregistrer la vente", command=save).grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")