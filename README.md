# FarmManager (Desktop - Tkinter + MySQL)

## Prérequis
- Python 3.11 recommandé
- MySQL Server (ou MariaDB) accessible en local

## Installation
1. Créer et activer un venv:
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .venv\\Scripts\\Activate.ps1
     ```
2. Installer les dépendances:
   ```powershell
   pip install -r requirements.txt
   ```
3. Configurer les variables d'environnement (copier `config.env.example` en `.env` et éditer):
   ```powershell
   Copy-Item config.env.example .env
   notepad .env
   ```
4. Initialiser la base de données:
   ```powershell
   python scripts/init_db.py
   ```
5. Créer un administrateur:
   ```powershell
   python scripts/create_admin.py
   ```
6. Lancer l'application:
   ```powershell
   python main.py
   ```

## Structure
- `app/config.py` : configuration (env)
- `app/db.py` : pool de connexions MySQL
- `app/ui/` : interfaces Tkinter (login, dashboard...)
- `migrations/001_init.sql` : schéma SQL
- `scripts/` : scripts utilitaires (init DB, créer admin)

## Packaging (.exe)
1) Option rapide (PowerShell):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1 -Name "FarmManager"
   ```
   - Résultat: `dist/FarmManager/FarmManager.exe`

2) Commande PyInstaller équivalente:
   ```powershell
   pyinstaller --noconfirm --clean --windowed --name FarmManager main.py
   ```

