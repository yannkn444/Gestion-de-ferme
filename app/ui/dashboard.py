import tkinter as tk
from tkinter import ttk

from app.dao.kpis import fetch_kpis


class DashboardFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20) # Augmentation du padding pour une meilleure esthétique
        self.columnconfigure(0, weight=1) # Permet au contenu de s'étendre
        self._build()
        self._refresh()

    def _build(self):
        # Utilisation d'un style plus grand pour le titre
        title = ttk.Label(self, text="Tableau de bord de la Ferme", font=("Segoe UI", 20, "bold"))
        title.pack(anchor="w", pady=(0, 20))

        # --- Cadre de la grille des KPI (mise en page) ---
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Configuration des colonnes pour un affichage uniforme
        for i in range(2):
            self.grid_frame.columnconfigure(i, weight=1, uniform="a")

        self.lbl_lots = self._create_kpi_label("Lots actifs:", self.grid_frame, row=0, col=0)
        self.lbl_low = self._create_kpi_label("Stocks sous seuil:", self.grid_frame, row=0, col=1, is_alert=True)
        self.lbl_dep = self._create_kpi_label("Dépenses (mois):", self.grid_frame, row=1, col=0)
        self.lbl_rec = self._create_kpi_label("Recettes (mois):", self.grid_frame, row=1, col=1)
        self.lbl_solde = self._create_kpi_label("Solde (mois):", self.grid_frame, row=2, col=0)
        self.lbl_mort = self._create_kpi_label("Mortalité (30j):", self.grid_frame, row=2, col=1)
        
        # Bouton actualiser déplacé
        refresh_btn = ttk.Button(self, text="Actualiser les Indicateurs", command=self._refresh)
        refresh_btn.pack(anchor="w", pady=(20, 0))

    def _create_kpi_label(self, label_text, parent, row, col, is_alert=False):
        """Fonction utilitaire pour créer et positionner un label KPI."""
        frame = ttk.Frame(parent, padding=10, relief="solid", borderwidth=1)
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        # Titre du KPI (Lot actif, Stock sous seuil, etc.)
        title_label = ttk.Label(frame, text=label_text, font=("Segoe UI", 10))
        title_label.pack(anchor="w")

        # Label de la valeur (où le KPI sera affiché)
        value_font_style = ("Segoe UI", 16, "bold")
        
        # Mise en évidence des alertes (Stocks)
        value_color = "red" if is_alert else "black"
        
        value_label = ttk.Label(frame, text="-", font=value_font_style, foreground=value_color)
        value_label.pack(anchor="w", pady=(5, 0))
        
        return value_label # Retourne le label de valeur pour la mise à jour

    def _refresh(self):
        """Récupère les données via le DAO et met à jour les Labels."""
        try:
            k = fetch_kpis() # Appel au DAO
            self.lbl_lots.configure(text=f"{k['lots_actifs']}")
            self.lbl_low.configure(text=f"{k['stocks_low']}")
            self.lbl_dep.configure(text=f"{k['dep_mois']:.0f} XAF")
            self.lbl_rec.configure(text=f"{k['rec_mois']:.0f} XAF")
            
            # Couleur du solde: Vert si positif, Rouge si négatif
            solde = k['solde_mois']
            self.lbl_solde.configure(
                text=f"{solde:.0f} XAF",
                foreground="green" if solde >= 0 else "red"
            )
            
            self.lbl_mort.configure(text=f"{k['mort_30']}")
            
        except Exception as e:
            # Gérer les erreurs de rafraîchissement (ex: BD déconnectée)
            print(f"Erreur de rafraîchissement des KPI: {e}")
            # Afficher un message d'erreur dans le tableau de bord si nécessaire
            self.lbl_lots.configure(text="Erreur")