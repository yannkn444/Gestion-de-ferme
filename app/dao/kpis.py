from datetime import date, timedelta
from app.db import get_connection

def fetch_kpis() -> dict:
    """
    Récupère tous les indicateurs de performance clés (KPIs) nécessaires
    pour le tableau de bord en exécutant des requêtes agrégées sur la BD.
    
    Retourne un dictionnaire contenant: lots_actifs, stocks_low, dep_mois, 
    rec_mois, solde_mois, et mort_30.
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            # 1. Nombre de lots actifs
            cur.execute("SELECT COUNT(*) AS n FROM lots WHERE statut='Actif'")
            lots_actifs = int(cur.fetchone()["n"])
            
            # 2. Stocks sous le seuil d'alerte
            # La colonne 'seuil' est maintenant garantie par l'exécution de la migration
            cur.execute("SELECT COUNT(*) AS n FROM stocks WHERE seuil IS NOT NULL AND seuil>0 AND quantite <= seuil")
            stocks_low = int(cur.fetchone()["n"])
            
            # 3. Calculs financiers du mois courant
            today = date.today()
            
            # Dépenses du mois
            cur.execute(
                "SELECT COALESCE(SUM(montant),0) AS s FROM depenses WHERE YEAR(date_depense)=%s AND MONTH(date_depense)=%s",
                (today.year, today.month),
            )
            dep_mois = float(cur.fetchone()["s"])
            
            # Recettes du mois
            cur.execute(
                "SELECT COALESCE(SUM(montant),0) AS s FROM recettes WHERE YEAR(date_recette)=%s AND MONTH(date_recette)=%s",
                (today.year, today.month),
            )
            rec_mois = float(cur.fetchone()["s"])
            
            # 4. Mortalité sur 30 jours
            start = today - timedelta(days=30)
            # Note: Le script SQL utilise la table 'mortalites' qui est une table d'événements
            cur.execute("SELECT COALESCE(SUM(quantite),0) AS s FROM mortalites WHERE date_event >= %s", (start,))
            mort_30 = int(cur.fetchone()["s"])
            
            return {
                "lots_actifs": lots_actifs,
                "stocks_low": stocks_low,
                "dep_mois": dep_mois,
                "rec_mois": rec_mois,
                "solde_mois": rec_mois - dep_mois,
                "mort_30": mort_30,
            }
    finally:
        # Assure la fermeture de la connexion quel que soit le résultat
        conn.close()