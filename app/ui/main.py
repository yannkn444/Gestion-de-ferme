import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional, Dict

# === Import des cadres de module (à adapter selon ton arborescence) ===
from app.ui.login import LoginFrame # <-- Correction appliquée dans app/ui/login.py
from app.ui.lots import LotsFrame
from app.ui.soins import SoinsFrame
from app.ui.stocks import StocksFrame
from app.ui.finances import FinancesFrame
from app.ui.reports import ReportsFrame
from app.ui.dashboard import DashboardFrame
from app.ui.backup import BackupFrame

# === Import des rôles et fonctions d’authentification ===
from app.auth import user_has_role, ROLE_ADMIN, ROLE_FERMIER, ROLE_VETERINAIRE, ROLE_GESTIONNAIRE
from app.theme import apply_theme


# === Configuration des modules disponibles ===
MODULE_CONFIG = [
    ("Dashboard", "Tableau de bord", DashboardFrame, []),
    ("Lots", "Lots d'animaux", LotsFrame, []),
    ("Soins", "Soins / Santé", SoinsFrame, []),
    ("Stocks", "Gestion des stocks", StocksFrame, []),
    ("Finances", "Finances", FinancesFrame, []),
    ("Rapports", "Rapports", ReportsFrame, []),
    ("Backup", "Sauvegarde / Export", BackupFrame, []),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FarmManager")
        self.geometry("1024x768")

        self._current_user: Optional[Dict] = None
        self._current_frame: Optional[ttk.Frame] = None

        self._load_and_apply_theme()

        # Conteneur principal
        self.content_wrapper = ttk.Frame(self, padding=0)
        self.content_wrapper.pack(fill=tk.BOTH, expand=True)

        self.sidebar_frame: Optional[ttk.Frame] = None
        self.main_content_frame: Optional[ttk.Frame] = None
        self._sidebar_buttons: Dict[str, ttk.Button] = {}

        # Écran de connexion au démarrage
        self._show_login()

    # =================================================================
    # CONFIGURATION DU THÈME
    # =================================================================
    def _load_and_apply_theme(self):
        """Applique le thème et les styles personnalisés."""
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "icon.ico"
        try:
            if icon_path.exists():
                self.iconbitmap(default=str(icon_path))
        except Exception:
            pass

        apply_theme(self)

        style = ttk.Style(self)
        style.configure("Sidebar.TFrame", background="#E8E8E8")
        style.configure("Sidebar.TButton",
                        font=("Segoe UI", 10, "bold"),
                        background="#E8E8E8",
                        foreground="#333333",
                        padding=[15, 10],
                        relief="flat")
        style.map("Sidebar.TButton",
                  background=[('active', '#D0D0D0'), ('disabled', '#E8E8E8')],
                  foreground=[('active', '#007ACC'), ('disabled', '#AAAAAA')])

        style.configure("Active.Sidebar.TButton",
                        background="#D0D0D0",
                        foreground="#007ACC",
                        font=("Segoe UI", 10, "bold"))

    # =================================================================
    # AUTHENTIFICATION
    # =================================================================
    def _clear_content(self):
        """Supprime tout le contenu principal (utile à la déconnexion)."""
        for widget in self.content_wrapper.winfo_children():
            widget.destroy()
        self.sidebar_frame = None
        self.main_content_frame = None
        self._current_frame = None
        self._sidebar_buttons = {}

    def _show_login(self):
        """Affiche la fenêtre de connexion."""
        self._clear_content()
        frame = LoginFrame(self.content_wrapper, on_success=self._on_login_success)
        frame.pack(fill=tk.BOTH, expand=True)
        self._current_frame = frame

    def _handle_logout(self):
        """Déconnecte l’utilisateur."""
        self._current_user = None
        self._show_login()

    def _on_login_success(self, user: Dict):
        """Appelée après une connexion réussie."""
        self._current_user = user
        print(f"[DEBUG] Utilisateur connecté : {user}")
        self._build_main_interface()
        self._open_module_by_name("Dashboard")

    # =================================================================
    # INTERFACE PRINCIPALE (SIDEBAR + CONTENU)
    # =================================================================
    def _build_main_interface(self):
        """Construit l’interface à deux colonnes après connexion."""
        self._clear_content()

        self.content_wrapper.grid_columnconfigure(0, weight=0)
        self.content_wrapper.grid_columnconfigure(1, weight=1)
        self.content_wrapper.grid_rowconfigure(0, weight=1)

        # --- Barre latérale ---
        self.sidebar_frame = ttk.Frame(self.content_wrapper, style="Sidebar.TFrame")
        self.sidebar_frame.grid(row=0, column=0, sticky="ns")
        self.sidebar_frame.columnconfigure(0, weight=1)

        self._build_sidebar_buttons()

        # --- Contenu principal ---
        self.main_content_frame = ttk.Frame(self.content_wrapper, padding=10)
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

    def _build_sidebar_buttons(self):
        """Construit les boutons de navigation de la barre latérale."""
        button_map = {}
        current_row = 0

        # --- Logo ---
        logo_lbl = ttk.Label(
            self.sidebar_frame,
            text="FarmManager",
            font=("Segoe UI", 14, "bold"),
            foreground="#007ACC",
            background="#E8E8E8",
            padding=(10, 15)
        )
        logo_lbl.grid(row=current_row, column=0, sticky="ew")
        current_row += 1

        ttk.Separator(self.sidebar_frame).grid(row=current_row, column=0, sticky="ew", pady=(5, 10))
        current_row += 1

        # --- Boutons des modules ---
        for name, label, _, _ in MODULE_CONFIG:
        # Changement : on suppose que l'utilisateur a toujours accès si la connexion a réussi.
            can_access = True  # <--- Accès forcé à Vrai

            text = label # <--- Retirer le cadenas 🔒

            btn = ttk.Button(
                self.sidebar_frame,
                text=text,
                command=(lambda n=name: self._open_module_by_name(n)), # <--- La commande est toujours définie
                style="Sidebar.TButton",
                state="normal" # <--- Le bouton est TOUJOURS actif
            )
            btn.grid(row=current_row, column=0, sticky="ew", padx=10, pady=2)
            button_map[name] = btn
            current_row += 1

        # --- Espaceur ---
        self.sidebar_frame.rowconfigure(current_row, weight=1)
        current_row += 1

        # --- Pied de page ---
        ttk.Separator(self.sidebar_frame).grid(row=current_row, column=0, sticky="ew", pady=(15, 5))
        current_row += 1

        footer_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        footer_frame.grid(row=current_row, column=0, sticky="ew", padx=10, pady=(0, 10))
        footer_frame.columnconfigure(0, weight=1)
        footer_frame.columnconfigure(1, weight=0)

        role_display = self._current_user.get("role", "N/A")

        role_label = ttk.Label(
            footer_frame,
            text=f"Utilisateur : {self._current_user.get('nom', 'Inconnu')}\nRôle : {role_display}",
            font=("Segoe UI", 8, "italic"),
            foreground="#666666",
            background="#E8E8E8",
            padding=(0, 5)
        )
        role_label.grid(row=0, column=0, sticky="w")

        ttk.Button(
            footer_frame,
            text="🔒 Déconnexion",
            command=self._handle_logout,
            style="Accent.TButton",
        ).grid(row=0, column=1, sticky="e", padx=(5, 0))

        self._sidebar_buttons = button_map

    # =================================================================
    # LOGIQUE DES MODULES
    # =================================================================
    def _clear_module_content(self):
        """Efface le contenu principal."""
        if self.main_content_frame:
            for widget in self.main_content_frame.winfo_children():
                widget.destroy()
        self._current_frame = None

    def _open_module(self, FrameClass, name: str):
        """Affiche le module correspondant."""
        self._clear_module_content()

        frame = FrameClass(self.main_content_frame)
        frame.grid(row=0, column=0, sticky="nsew")
        self._current_frame = frame

        # Met à jour le style actif
        for btn_name, btn in self._sidebar_buttons.items():
            if btn_name == name:
                btn.config(style="Active.Sidebar.TButton")
            else:
                btn.config(style="Sidebar.TButton")

    def _open_module_by_name(self, module_name: str):
        """Ouvre un module en fonction de son nom."""
        for name, _, FrameClass, _ in MODULE_CONFIG:
            if name == module_name:
                self._open_module(FrameClass, name)
                return


# === Lancement de l'application ===
def run_app():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_app()