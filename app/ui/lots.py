import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from datetime import date
# Importations factices (DAO et Utilitaires non fournis, mais nécessaires à la logique)
# NOTE : J'assume que ces imports sont corrects pour le reste de votre application.
from app.dao.lots import list_lots, create_lot, update_lot, get_lot, close_lot, delete_lot 
from app.dao.lot_events import record_mortality, record_partial_sale, get_lot_counters, record_slaughter 
from app.utils.validators import is_valid_date
from app.utils.pdf import export_table_pdf, export_sale_receipt
from pathlib import Path
from tkinter import filedialog
import time


class LotForm(tk.Toplevel):
    """
    Formulaire pour créer ou modifier les informations de base d'un lot d'animaux.
    Il est rendu semi-responsive et certains champs sont bloqués en mode édition.
    """
    def __init__(self, master, lot_id: Optional[int], on_saved):
        super().__init__(master)
        # Configuration de base de la fenêtre
        self.title("Lot - Édition" if lot_id else "Lot - Nouveau")
        self.resizable(True, False) # Autoriser le redimensionnement horizontal

        self._lot_id = lot_id       # ID du lot à éditer (None pour la création)
        self._on_saved = on_saved   # Callback à exécuter après l'enregistrement (ex: rafraîchir la liste)

        # Conteneur principal et configuration pour la responsivité
        container = ttk.Frame(self, padding=12)
        # Le conteneur occupe toute la place disponible dans la fenêtre
        container.grid(row=0, column=0, sticky="nsew") 

        # Configuration du Toplevel pour la responsivité
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Configuration du conteneur : seule la colonne des entrées s'étire
        container.columnconfigure(1, weight=1) 
        container.columnconfigure(0, weight=0) # Les labels restent fixes

        # Variables de contrôle Tkinter
        self.var_type = tk.StringVar()
        self.var_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.var_nombre = tk.IntVar()
        self.var_poids = tk.StringVar()
        self.var_source = tk.StringVar()
        self.var_statut = tk.StringVar(value="Actif")
        self.var_remarque = tk.StringVar()
        self.var_cout_initial = tk.StringVar()

        # Construction des champs de saisie (utilisant la grille)
        row = 0
        
        # Champ Espèce (Combobox)
        ttk.Label(container, text="Espèce").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        cb = ttk.Combobox(container, textvariable=self.var_type, values=["Poulet", "Porc"], state="readonly")
        cb.grid(row=row, column=1, pady=4, padx=5, sticky="ew") # sticky="ew" permet au widget de s'étirer
        row += 1
        
        # Champ Date d'arrivée
        ttk.Label(container, text="Date d'arrivée (YYYY-MM-DD)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        date_entry = ttk.Entry(container, textvariable=self.var_date)
        date_entry.grid(row=row, column=1, pady=4, padx=5, sticky="ew")
        row += 1
        
        # Champ Nombre initial
        ttk.Label(container, text="Nombre initial").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        nombre_entry = ttk.Entry(container, textvariable=self.var_nombre)
        nombre_entry.grid(row=row, column=1, pady=4, padx=5, sticky="ew")
        row += 1
        # Champ Poids moyen
        ttk.Label(container, text="Poids moyen (kg)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(container, textvariable=self.var_poids).grid(row=row, column=1, pady=4, padx=5, sticky="ew")
        row += 1
        # Champ Source
        ttk.Label(container, text="Source").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(container, textvariable=self.var_source).grid(row=row, column=1, pady=4, padx=5, sticky="ew")
        row += 1
        
        # Champ Statut
        ttk.Label(container, text="Statut").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        cb2 = ttk.Combobox(container, textvariable=self.var_statut)
        cb2.grid(row=row, column=1, pady=4, padx=5, sticky="ew")
        row += 1
        
        # Champ Remarque
        ttk.Label(container, text="Remarque (optionnel)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(container, textvariable=self.var_remarque).grid(row=row, column=1, pady=4, padx=5, sticky="ew")
        row += 1
        
        # Bouton Enregistrer
        btn = ttk.Button(container, text="Enregistrer", command=self._save)
        btn.grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")

        # Logique d'édition : charger les données et bloquer les champs sensibles
        if lot_id:
            self._load()
            # BLOCAGE DES CHAMPS SENSIBLES EN MODE ÉDITION
            # Empêcher la modification de la date et du nombre initial pour maintenir la cohérence de l'historique
            date_entry.config(state="readonly")
            nombre_entry.config(state="readonly")

    def _load(self):
        """Charge les données du lot existant pour l'édition."""
        lot = get_lot(self._lot_id)
        if not lot:
            messagebox.showerror("Erreur", "Lot introuvable")
            self.destroy()
            return
        # Remplissage des variables
        self.var_type.set(lot["type_animal"])
        self.var_date.set(str(lot["date_arrivee"]))
        self.var_nombre.set(lot["nombre_initial"]) 
        self.var_poids.set("" if lot["poids_moyen"] is None else str(lot["poids_moyen"]))
        self.var_source.set(lot.get("source") or "")
        self.var_statut.set(lot["statut"]) 
        self.var_remarque.set(lot.get("remarque (optionnel)") or "")
        self.var_cout_initial.set(str(lot.get("cout_initial",0)))

    def _save(self):
        """Valide et enregistre (crée ou met à jour) le lot."""
        # 1. Validation de base
        try:
            # Conversion du poids en float, ou None si vide
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
        
        # 2. Logique d'enregistrement
        if self._lot_id:
            # Mode Édition
            current_lot = get_lot(self._lot_id)
            
            # Mise à jour des informations de base
            update_lot(
                self._lot_id,
                self.var_type.get(),
                self.var_date.get(),
                int(self.var_nombre.get()),
                poids,
                self.var_source.get() or None,
                current_lot["statut"], # Garder le statut actuel
                self.var_remarque.get() or None,
                
            )
        else:
            # Mode Création
            create_lot(
                self.var_type.get(),
                self.var_date.get(),
                int(self.var_nombre.get()),
                poids,
                self.var_source.get() or None,
                "Actif", # Statut par défaut à la création
                self.var_remarque.get() or None,
                # === AJOUTEZ L'ARGUMENT MANQUANT ICI ===
                float(self.var_cout_initial.get()) if self.var_cout_initial.get().strip() else 0,
            )
            
        # 3. Finalisation
        self._on_saved()
        self.destroy()


# ----------------------------------------------------------------------
## Classe LotsFrame (Vue Principale)
# ----------------------------------------------------------------------

class LotsFrame(ttk.Frame):
    """
    Cadre principal pour la gestion des lots d'animaux.
    Contient la barre d'outils et le Treeview (liste), et gère les actions.
    **Implémentation du responsive design.**
    """
    def __init__(self, master):
        super().__init__(master, padding=10)
        
        # Configuration des poids pour la responsivité :
        # La colonne 0 (tout le contenu) s'étire horizontalement
        self.columnconfigure(0, weight=1)
        # La ligne 2 (le Treeview) s'étire verticalement.
        self.rowconfigure(2, weight=1) 
        
        self._build()
        self._refresh()

    def _build(self):
        """Construit l'interface utilisateur du cadre des lots."""
        
        # Titre (Ligne 0)
        ttk.Label(self, text="Gestion des Lots d'Animaux", 
                  font=("Segoe UI", 16, "bold"), foreground="#1C7D7D").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Variables pour le filtrage
        self.var_search = tk.StringVar()
        #Variable pour le filtre de statut (initialisée à 'Actif' par défaut)
        self.var_statut_filter = tk.StringVar(value="Actif")

        # Barre d'outils (Ligne 1)
        toolbar = ttk.Frame(self)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        toolbar = ttk.Frame(self)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 5)) 
        
        # Boutons de la barre d'outils
        self.btn_new = ttk.Button(toolbar, text="Nouveau lot (Fermier)", command=self._new)
        self.btn_new.pack(side=tk.LEFT)
        self.btn_edit = ttk.Button(toolbar, text="Modifier", command=self._edit)
        self.btn_edit.pack(side=tk.LEFT, padx=6)
        self.btn_delete = ttk.Button(toolbar, text="supprimer", command=self._delete)
        self.btn_delete.pack (side=tk.LEFT)
        
        
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill='y')

        # 2. Ajout du Filtre par Statut
        ttk.Label(toolbar, text="Statut:").pack(side=tk.LEFT, padx=(5, 0))
    
        statut_values = ["Actif", "Vendu", "Abattu", "Tous"]
        self.cb_statut_filter = ttk.Combobox(
            toolbar, 
            textvariable=self.var_statut_filter, 
            values=statut_values, 
            state="readonly", 
            width=10
        )
        self.cb_statut_filter.pack(side=tk.LEFT, padx=5)
    
        # Lie un événement pour rafraîchir la liste dès que la sélection change
        self.cb_statut_filter.bind('<<ComboboxSelected>>', lambda e: self._refresh())

        #Ajout du Champ de Recherche
    
        ttk.Label(toolbar, text="Rechercher:").pack(side=tk.LEFT, padx=(5, 0))
    
        self.entry_search = ttk.Entry(toolbar, textvariable=self.var_search, width=25)
        self.entry_search.pack(side=tk.LEFT, padx=5)
    
        # Lier la touche Entrée (Return) au rafraîchissement
        self.entry_search.bind('<Return>', lambda e: self._refresh())
    
        self.btn_search = ttk.Button(toolbar, text="🔎 Filtrer", command=self._refresh)
        self.btn_search.pack(side=tk.LEFT)

        self.btn_mort = ttk.Button(toolbar, text="❌ Mortalité", command=self._mortality)
        self.btn_mort.pack(side=tk.LEFT)
        self.btn_sale = ttk.Button(toolbar, text="💰 Vente partielle", command=self._sale)
        self.btn_sale.pack(side=tk.LEFT, padx=6)
        
        # Bouton Abattage partiel
        self.btn_slaughter = ttk.Button(toolbar, text="🔪 Abattage", command=self._slaughter) 
        self.btn_slaughter.pack(side=tk.LEFT)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill='y')
        
        self.btn_close = ttk.Button(toolbar, text="✅ Clôturer (Vendu)", command=self._close)
        self.btn_close.pack(side=tk.LEFT)

        # Treeview pour la liste des lots (Ligne 2)
        cols = ("id", "type", "date", "nombre", "morts", "vendus", "abattus", "restants", "poids", "source", "statut", "remarque")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        
        # Configuration des colonnes (pour la largeur)
        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("type", width=80, anchor=tk.CENTER)
        self.tree.column("date", width=100, anchor=tk.CENTER)
        self.tree.column("nombre", width=70, anchor=tk.CENTER)
        self.tree.column("morts", width=70, anchor=tk.CENTER)
        self.tree.column("vendus", width=70, anchor=tk.CENTER)
        self.tree.column("abattus", width=70, anchor=tk.CENTER)
        self.tree.column("restants", width=70, anchor=tk.CENTER)
        self.tree.column("poids", width=100, anchor=tk.CENTER)
        self.tree.column("source", width=120, anchor=tk.W)
        self.tree.column("statut", width=100, anchor=tk.CENTER)
        self.tree.column("remarque", width=150, anchor=tk.W)

        # Configuration des en-têtes
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Espèce")
        self.tree.heading("date", text="Arrivée")
        self.tree.heading("nombre", text="Initial")
        self.tree.heading("morts", text="Morts")
        self.tree.heading("vendus", text="Vendus")
        self.tree.heading("abattus", text="Abattus")
        self.tree.heading("restants", text="Restants")
        self.tree.heading("poids", text="Poids moy. (kg)")
        self.tree.heading("source", text="Source")
        self.tree.heading("statut", text="Statut")
        self.tree.heading("remarque", text="Remarque")

        # sticky="nsew" permet au Treeview de s'étirer dans toutes les directions.
        self.tree.grid(row=2, column=0, sticky="nsew", pady=6) 
        
        # Ajout d'une barre de défilement verticale
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        # sticky='ns' permet à la scrollbar de s'étirer verticalement.
        scrollbar.grid(row=2, column=1, sticky='ns') 

    def _refresh(self):
        """Charge et affiche la liste des lots depuis la base de données."""
        
        #Récupère le terme de recherche
        search_term = self.var_search.get() if hasattr(self, 'var_search') else None
        
        # Récupère le statut sélectionné. Si 'Tous' est sélectionné, on passe None
        statut_filter = self.var_statut_filter.get() if hasattr(self, 'var_statut_filter') and self.var_statut_filter.get() != "Tous" else None

        # Efface les lignes existantes
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Charge les lots (avec les compteurs calculés dans la DAO)
        for row in list_lots(search=search_term, statut=statut_filter):
            poids_moyen = f"{row['poids_moyen']:.2f} kg" if row.get("poids_moyen") else "-"
            
            self.tree.insert("", tk.END, values=(
                row["id"], 
                row["type_animal"], 
                str(row["date_arrivee"]), 
                row["nombre_initial"], 
                row.get("morts", 0), 
                row.get("vendus", 0), 
                row.get("abattus", 0),
                row.get("restants", 0), 
                poids_moyen, 
                row.get("source") or "-", 
                row["statut"],
                row.get("remarque") or "-" 
            ))

    def _selected_id(self) -> Optional[int]:
        """Récupère l'ID du lot sélectionné dans le Treeview."""
        item = self.tree.selection()
        if not item:
            return None
        values = self.tree.item(item[0], "values")
        return int(values[0])

    # --- Gestion des actions (Nouveau, Modifier, Clôturer) ---
    
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
    
    def _delete(self):
        """Gère la suppression définitive d'un lot."""
        id_ = self._selected_id()
        if not id_:
            messagebox.showinfo("Info", "Sélectionnez un lot à supprimer.")
            return
            
        lot = get_lot(id_)
        
        if lot and (lot.get("morts", 0) > 0 or lot.get("vendus", 0) > 0):
            # Vérification si le lot a déjà un historique
            if not messagebox.askyesno("⚠️ Attention - Suppression", 
                                       f"Lot #{id_} a déjà des événements enregistrés. Êtes-vous SÛR de vouloir SUPPRIMER DÉFINITIVEMENT ce lot et tout son historique associé ?"):
                return
        else:
            # Simple suppression si le lot est "neuf" ou non utilisé
            if not messagebox.askyesno("Confirmation de Suppression", f"Voulez-vous supprimer définitivement Lot #{id_} ?"):
                return
                
        try:
            delete_lot(id_) # Appel à la fonction DAO
            messagebox.showinfo("Succès", f"Lot #{id_} a été supprimé.")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Erreur de Suppression", f"Impossible de supprimer le lot. Assurez-vous que la fonction DAO 'delete_lot' est implémentée: {e}")

    # --- CORRECTION APPORTÉE ICI ---
    def _slaughter(self):
        """Ouvre le dialogue pour enregistrer l'abattage PARTIEL pour le lot sélectionné."""
        id_ = self._selected_id()
        if not id_:
            messagebox.showinfo("Info", "Sélectionnez un lot.")
            return
        lot = get_lot(id_)
        if lot and lot.get("statut") != "Actif":
            messagebox.showwarning("Action impossible", f"Le lot #{id_} n'est pas actif.")
            return
        
        # Appel direct au dialogue d'abattage partiel
        self._open_slaughter_dialog(id_)
        # L'ancienne logique d'abattage total est retirée.
    # --- FIN DE LA CORRECTION ---
    
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
        
        # Demande de confirmation si des animaux sont restants
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

    # --- Gestion des événements spécifiques (Mortalité et Vente) ---

    def _mortality(self):
        """Prépare l'ouverture du dialogue de mortalité pour le lot sélectionné."""
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
        """Prépare l'ouverture du dialogue de vente partielle pour le lot sélectionné."""
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
        """Dialogue pour enregistrer la mortalité (avec validation de la date)."""
        dlg = tk.Toplevel(self.master)
        dlg.title(f"Mortalité - Lot #{lot_id}")
        dlg.transient(self.master)
        dlg.grab_set()
        dlg.resizable(False, False)
        frm = ttk.Frame(dlg, padding=12)
        frm.grid()
        
        # Récupération de la date d'arrivée pour la validation temporelle
        lot = get_lot(lot_id)
        if not lot:
            messagebox.showerror("Erreur", "Lot introuvable")
            return
        date_arrivee = lot["date_arrivee"]

        # Variables du dialogue
        v_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d")) # Initialisé à la date du jour
        v_q = tk.IntVar(value=0)
        v_motif = tk.StringVar()
        
        # Construction des champs
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
            """Logique d'enregistrement et de validation de la mortalité."""
            if v_q.get() <= 0 or not v_date.get():
                messagebox.showwarning("Validation", "Date et quantité décédée requises et positives.")
                return
            if not is_valid_date(v_date.get()):
                messagebox.showwarning("Validation", "Format de date invalide (YYYY-MM-DD).")
                return

            # *** VÉRIFICATION DE LA COHÉRENCE TEMPORELLE ***
            if v_date.get() < str(date_arrivee):
                 messagebox.showwarning("Validation", 
                                        f"La date de mortalité ({v_date.get()}) ne peut être antérieure à la date d'arrivée du lot ({date_arrivee}).")
                 return
            # **********************************************

            counters = get_lot_counters(lot_id)
            if v_q.get() > counters["restants"]:
                messagebox.showwarning("Validation", f"Quantité ({v_q.get()}) supérieure aux restants ({counters['restants']}).")
                return
            
            try:
                record_mortality(lot_id, v_date.get(), int(v_q.get()), v_motif.get() or None)
                dlg.destroy()
                self._refresh()
            except Exception as e:
                messagebox.showerror("Erreur DAO", f"Échec de l'enregistrement de la mortalité : {e}")

            
        ttk.Button(frm, text="Enregistrer la mortalité", command=save).grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")

    def _open_sale_dialog(self, lot_id: int):
        """Dialogue pour enregistrer une vente partielle (avec validation de la date et génération de reçu)."""
        dlg = tk.Toplevel(self.master)
        dlg.title(f"Vente Partielle - Lot #{lot_id}")
        dlg.transient(self.master)
        dlg.grab_set()
        dlg.resizable(False, False)
        frm = ttk.Frame(dlg, padding=12)
        frm.grid()
        
        # Récupération de la date d'arrivée pour la validation temporelle
        lot = get_lot(lot_id)
        if not lot:
            messagebox.showerror("Erreur", "Lot introuvable")
            return
        date_arrivee = lot["date_arrivee"]
        
        # Variables du dialogue
        v_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d")) # Initialisé à la date du jour
        v_q = tk.IntVar(value=0)
        v_px = tk.StringVar() # Prix
        v_client = tk.StringVar()
        
        # Construction des champs
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
            """Logique d'enregistrement et de validation de la vente."""
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

            # *** VÉRIFICATION DE LA COHÉRENCE TEMPORELLE ***
            if v_date.get() < str(date_arrivee):
                 messagebox.showwarning("Validation", 
                                        f"La date de vente ({v_date.get()}) ne peut être antérieure à la date d'arrivée du lot ({date_arrivee}).")
                 return

            counters = get_lot_counters(lot_id)
            if v_q.get() > counters["restants"]:
                messagebox.showwarning("Validation", f"Quantité ({v_q.get()}) supérieure aux restants ({counters['restants']}).")
                return
                
            # Enregistrement de la vente
            try:
                record_partial_sale(lot_id, v_date.get(), int(v_q.get()), prix, v_client.get() or None)
            except Exception as e:
                messagebox.showerror("Erreur DAO", f"Échec de l'enregistrement de la vente : {e}")
                return
            
            messagebox.showinfo("Succès", f"{v_q.get()} animaux vendus enregistrés pour le Lot #{lot_id}.")
            dlg.destroy()
            self._refresh()
            
        ttk.Button(frm, text="Enregistrer la vente", command=save).grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")

    def _open_slaughter_dialog(self, lot_id: int):
        """Dialogue pour enregistrer un abattage partiel (avec validation)."""
        dlg = tk.Toplevel(self.master)
        dlg.title(f"Abattage Partiel - Lot #{lot_id}")
        dlg.transient(self.master)
        dlg.grab_set()
        dlg.resizable(False, False)
        frm = ttk.Frame(dlg, padding=12)
        frm.grid()
    
        lot = get_lot(lot_id)
        if not lot:
            messagebox.showerror("Erreur", "Lot introuvable")
            return
        date_arrivee = lot["date_arrivee"]

        # Variables du dialogue
        v_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        v_q = tk.IntVar(value=0)
        v_poids_unitaire = tk.StringVar()
    
        # Construction des champs
        row = 0
        ttk.Label(frm, text="Date (YYYY-MM-DD)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_date, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(frm, text="Quantité abattue").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_q, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
        ttk.Label(frm, text="Poids unitaire (kg)").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frm, textvariable=v_poids_unitaire, width=18).grid(row=row, column=1, pady=4, padx=5)
        row += 1
    
        def save():
            """Logique d'enregistrement et de validation de l'abattage."""
            try:
                poids_unitaire = float(v_poids_unitaire.get()) if v_poids_unitaire.get().strip() else None
            except ValueError:
                messagebox.showwarning("Validation", "Poids unitaire invalide. Entrez un nombre.")
                return
            
            if v_q.get() <= 0 or not v_date.get():
                messagebox.showwarning("Validation", "Date et quantité abattue requises et positives.")
                return
            
            if not is_valid_date(v_date.get()):
                messagebox.showwarning("Validation", "Format de date invalide (YYYY-MM-DD).")
                return

            # VÉRIFICATION DE LA COHÉRENCE TEMPORELLE
            if v_date.get() < str(date_arrivee):
                messagebox.showwarning("Validation", 
                                       f"La date d'abattage ({v_date.get()}) ne peut être antérieure à la date d'arrivée du lot ({date_arrivee}).")
                return

            counters = get_lot_counters(lot_id)
            if v_q.get() > counters["restants"]:
                messagebox.showwarning("Validation", f"Quantité ({v_q.get()}) supérieure aux restants ({counters['restants']}).")
                return

            try:
                record_slaughter(lot_id, v_date.get(), int(v_q.get()), poids_unitaire)
                messagebox.showinfo("Succès", f"{v_q.get()} animaux abattus enregistrés pour le Lot #{lot_id}.")
                dlg.destroy()
                self._refresh()
            except Exception as e:
                messagebox.showerror("Erreur DAO", f"Échec de l'enregistrement de l'abattage : {e}")
                
        ttk.Button(frm, text="Enregistrer l'Abattage", command=save).grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")