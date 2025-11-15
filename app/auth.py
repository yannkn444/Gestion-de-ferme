from typing import Dict

# --- Définition des rôles internes (techniques) ---
ROLE_ADMIN = "ADMIN"
ROLE_FERMIER = "FERMIER"
ROLE_VETERINAIRE = "VETERINAIRE"
ROLE_GESTIONNAIRE = "GESTIONNAIRE"

# --- Noms lisibles pour affichage dans l’interface ---
ROLE_LABELS = {
    ROLE_ADMIN: "Administrateur",
    ROLE_FERMIER: "Fermier / Soignant",
    ROLE_VETERINAIRE: "Vétérinaire",
    ROLE_GESTIONNAIRE: "Gestionnaire",
}

# --- Table de correspondance inversée ---
# Permet de reconnaître aussi bien "ADMIN" que "Administrateur"
ROLE_MAP = {
    "ADMIN": ROLE_ADMIN,
    "Administrateur": ROLE_ADMIN,
    "FERMIER": ROLE_FERMIER,
    "Fermier": ROLE_FERMIER,
    "Fermier / Soignant": ROLE_FERMIER,
    "VETERINAIRE": ROLE_VETERINAIRE,
    "Vétérinaire": ROLE_VETERINAIRE,
    "GESTIONNAIRE": ROLE_GESTIONNAIRE,
    "Gestionnaire": ROLE_GESTIONNAIRE,
}


def normalize_role(role: str) -> str:
    """Renvoie la valeur interne d’un rôle, quel que soit le format."""
    if not role:
        return ""
    return ROLE_MAP.get(role.strip(), role.strip())


def user_has_role(user: Dict, *roles: str) -> bool:
    """
    Vérifie si l'utilisateur possède au moins un des rôles spécifiés.
    Accepte à la fois les valeurs internes ('ADMIN') et lisibles ('Administrateur').
    """
    if not user or not isinstance(user, dict):
        return False

    user_role = normalize_role(user.get("role"))
    allowed_roles = [normalize_role(r) for r in roles]

    return user_role in allowed_roles
