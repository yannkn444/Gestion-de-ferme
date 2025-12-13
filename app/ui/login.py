import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import bcrypt
import os

from app.db import get_connection, init_connection_pool
from app.auth import ROLE_ADMIN


class LoginFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, padding=0)
        self._on_success = on_success

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        style = ttk.Style(master)
        
        # 1. Carte principale 
        style.configure("LoginCard.TFrame",
                        background="#FFFFFF", 
                        relief="flat",
                        borderwidth=1)
        
        # 2. Styles de TEXTE 
        style.configure("FormTitle.TLabel",
                        background="",  
                        foreground="#007ACC",
                        font=("Segoe UI", 16, "bold"))
                        
        style.configure("FormSubtitle.TLabel",
                        background="",  
                        foreground="#666666",
                        font=("Segoe UI", 9))
                        
        style.configure("FormContent.TLabel",
                        background="",  
                        font=("Segoe UI", 10))
                        
        style.configure("Login.TEntry", relief="flat")
        
        style.configure("Accent.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=10)

        # === Conteneur principal centré (Fond Blanc) ===
        main_frame = ttk.Frame(self, style="LoginCard.TFrame")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Définir une taille adaptée à l’écran
        main_frame.config(padding=(40, 45))

        # === ZONE FORMULAIRE (tk.Frame) ===
        form_frame = tk.Frame(main_frame, 
                              bg="#EEEEEE",
                              bd=2, 
                              relief="solid") 
        
        form_frame.pack(fill="x", padx=20, pady=20)

        # === Logo ===
        logo_path = Path(__file__).resolve().parents[2] / "assets" / "logo.png"
        if logo_path.exists():
            try:
                pil_image = Image.open(logo_path)
                pil_image = pil_image.resize((350, 350), Image.Resampling.LANCZOS)
                logo_img = ImageTk.PhotoImage(pil_image)
                logo_lbl = ttk.Label(form_frame, image=logo_img) 
                logo_lbl.image = logo_img 
                logo_lbl.pack(pady=(0, 15))
            except Exception:
                ttk.Label(form_frame, text="🚜", font=("Segoe UI Emoji", 40)).pack(pady=(0, 15))
        else:
            ttk.Label(form_frame, text="🚜", font=("Segoe UI Emoji", 40)).pack(pady=(0, 15))

        # === Titre et sous-titre ===
        ttk.Label(form_frame, text="Bienvenue sur FarmManager", style="FormTitle.TLabel").pack(pady=(0, 5))
        ttk.Label(form_frame, text="Connectez-vous pour continuer", style="FormSubtitle.TLabel").pack(pady=(0, 25))

        # === Champs email/pass ===
        self.email_var = tk.StringVar(value="admin@example.com")
        self.password_var = tk.StringVar(value="ChangeMe123!")

        ttk.Label(form_frame, text="Adresse email", style="FormContent.TLabel").pack(anchor="w", pady=(5, 2))
        email_entry = ttk.Entry(form_frame, textvariable=self.email_var, width=35, style="Login.TEntry")
        email_entry.pack(fill="x", pady=(0, 10), padx=5)

        ttk.Label(form_frame, text="Mot de passe", style="FormContent.TLabel").pack(anchor="w", pady=(5, 2))
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=35, style="Login.TEntry")
        password_entry.pack(fill="x", pady=(0, 15), padx=5)

        # === Bouton connexion ===
        self.login_btn = ttk.Button(form_frame,
                                    text="Se connecter",
                                    command=self._handle_login,
                                    style="Accent.TButton")
        self.login_btn.pack(fill="x", pady=(10, 5), padx=5)

        # === Pied de page / astuce ===
        ttk.Label(main_frame,
                  text="Astuce : admin@example.com / ChangeMe123!",
                  style="FormSubtitle.TLabel", 
                  background="#FFFFFF").pack(pady=(5, 0))

        # Focus sur le premier champ
        email_entry.focus_set()
        self.bind("<Return>", lambda _e: self._handle_login())

        # Initialiser le pool de connexion
        init_connection_pool()

    #  Authentification
    def _handle_login(self):
        self.login_btn.config(state=tk.DISABLED)

        email = self.email_var.get().strip()
        password = self.password_var.get()

        if not email or not password:
            messagebox.showwarning("Champs requis", "Veuillez saisir email et mot de passe.")
            self.login_btn.config(state=tk.NORMAL)
            return

        try:
            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("SELECT id, nom, email, mot_de_passe, role FROM utilisateurs WHERE email=%s", (email,))
                    user = cur.fetchone()

                    if not user:
                        messagebox.showerror("Erreur", "Identifiants invalides.")
                        self.login_btn.config(state=tk.NORMAL)
                        return

                    stored_hash = user["mot_de_passe"].encode("utf-8")
                    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                        if 'role' not in user:
                            user['role'] = ROLE_ADMIN

                        self.after(0, lambda: self._on_success(user))
                    else:
                        messagebox.showerror("Erreur", "Identifiants invalides.")
                        self.login_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Erreur de connexion", f"Une erreur s'est produite : {e}")
            self.login_btn.config(state=tk.NORMAL)