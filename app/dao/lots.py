from typing import List, Dict, Optional, Tuple
from ..db import get_connection 


def list_lots(search: Optional[str] = None, statut: Optional[str] = None) -> List[Dict]:
    """
    Récupère la liste des lots avec les compteurs calculés (morts, vendus, abattus, restants),
    en appliquant des filtres optionnels par statut et recherche textuelle.
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            base_select = (
                """
                SELECT l.id, l.type_animal, l.date_arrivee, l.nombre_initial, l.poids_moyen, l.source, l.statut, l.remarque, l.cout_initial, -- AJOUT de cout_initial
                COALESCE(m.q,0) AS morts,
                COALESCE(v.q,0) AS vendus,
                COALESCE(a.q,0) AS abattus, 
                (l.nombre_initial - COALESCE(m.q,0) - COALESCE(v.q,0) - COALESCE(a.q,0)) AS restants
                FROM lots l
                LEFT JOIN (
                    SELECT lot_id, SUM(quantite) AS q FROM mortalites GROUP BY lot_id
                ) m ON m.lot_id = l.id
                LEFT JOIN (
                    SELECT lot_id, SUM(quantite) AS q FROM ventes_animaux GROUP BY lot_id
                ) v ON v.lot_id = l.id
                LEFT JOIN (
                    SELECT lot_id, SUM(quantite) AS q FROM abattages GROUP BY lot_id
                ) a ON a.lot_id = l.id 
                """
            )
            
            # --- Logique de Filtrage Unifiée ---
            conditions = []
            params = []
            
            # 1. Filtre par Statut (si spécifié)
            if statut:
                conditions.append("l.statut = %s")
                params.append(statut)
                
            # 2. Filtre par Recherche textuelle (si spécifié)
            if search:
                like = f"%{search}%"
                conditions.append("(l.type_animal LIKE %s OR l.source LIKE %s OR l.statut LIKE %s)")
                params.extend([like, like, like])
            
            # 3. Construction de la requête finale
            full_query = base_select
            if conditions:
                full_query += " WHERE " + " AND ".join(conditions) 
            
            full_query += " ORDER BY l.id DESC"
            
            cur.execute(full_query, tuple(params))
            
            return cur.fetchall()
    finally:
        conn.close()


def create_lot(
    type_animal: str,
    date_arrivee: str,
    nombre_initial: int,
    poids_moyen: Optional[float],
    source: Optional[str],
    statut: str, 
    remarque: Optional[str],
    cout_initial: Optional[float], 
) -> int:
    """
    Crée un nouveau lot.
    
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO lots(type_animal, date_arrivee, nombre_initial, poids_moyen, source, statut, remarque, cout_initial)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (type_animal, date_arrivee, nombre_initial, poids_moyen, source, statut, remarque, cout_initial),
            )
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()


def update_lot(
    id_: int,
    type_animal: str,
    date_arrivee: str,
    nombre_initial: int,
    poids_moyen: Optional[float],
    source: Optional[str],
    statut: str,
    remarque: Optional[str],
) -> None:
    """
    Met à jour les informations de base d'un lot existant, y compris son statut.

    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE lots
                SET type_animal=%s, date_arrivee=%s, nombre_initial=%s, poids_moyen=%s, source=%s, statut=%s, remarque=%s
                WHERE id=%s
                """,
                (type_animal, date_arrivee, nombre_initial, poids_moyen, source, statut, remarque, id_),
            )
            conn.commit()
    finally:
        conn.close()


def get_lot(id_: int) -> Optional[Dict]:
    """
    Récupère un lot par son ID.
    
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT id, type_animal, date_arrivee, nombre_initial, poids_moyen, source, statut, remarque, cout_initial FROM lots WHERE id=%s",
                (id_,),
            )
            return cur.fetchone()
    finally:
        conn.close()


def close_lot(id_: int, statut: str = "Vendu") -> None:
    """
    Met à jour le statut d'un lot, généralement pour le marquer comme 'Vendu' ou 'Abattu' (si tout est parti).

    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE lots SET statut=%s WHERE id=%s", (statut, id_))
            conn.commit()
    finally:
        conn.close()


def list_active_lots() -> List[Dict]:
    """
    Récupère une liste simplifiée des lots actifs pour les menus déroulants d'événements.
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT id, type_animal, date_arrivee, nombre_initial FROM lots WHERE statut='Actif' ORDER BY id DESC"
            )
            return cur.fetchall()
    finally:
        conn.close()

def delete_lot(lot_id: int):
   
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Supprime le lot principal
        cursor.execute("DELETE FROM lots WHERE id = %s", (lot_id,))
        
        conn.commit()
        
    except Exception as e:
        print(f"Erreur lors de la suppression du lot {lot_id} : {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def check_and_close_lot(lot_id: int):
    """
    Vérifie si un lot n'a plus d'animaux restants et met à jour son statut
    à 'Terminé' si la quantité restante est <= 0 et que le statut actuel est 'Actif'.
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            # 1. Calculer le nombre d'animaux restants
            cur.execute(
                """
                SELECT 
                    (l.nombre_initial - COALESCE(m.q, 0) - COALESCE(v.q, 0) - COALESCE(a.q, 0)) AS restants,
                    l.statut
                FROM lots l
                LEFT JOIN (SELECT lot_id, SUM(quantite) AS q FROM mortalites GROUP BY lot_id) m ON m.lot_id = l.id
                LEFT JOIN (SELECT lot_id, SUM(quantite) AS q FROM ventes_animaux GROUP BY lot_id) v ON v.lot_id = l.id
                LEFT JOIN (SELECT lot_id, SUM(quantite) AS q FROM abattages GROUP BY lot_id) a ON a.lot_id = l.id
                WHERE l.id = %s
                """,
                (lot_id,)
            )
            result = cur.fetchone()
            
            if not result:
                return False

            restants = result['restants']
            current_statut = result['statut']

            # 2. Vérification de la condition et mise à jour
            if restants <= 0 and current_statut == 'Actif':
                new_statut = 'Terminé'
                
                cur.execute(
                    "UPDATE lots SET statut = %s WHERE id = %s",
                    (new_statut, lot_id)
                )
                conn.commit()
                return True
                
            return False
            
    except Exception as e:
        print(f"Erreur lors de la vérification du statut du lot {lot_id}: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()