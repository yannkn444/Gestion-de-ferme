from typing import Dict, List, Optional
from ..db import get_connection


def record_mortality(lot_id: int, date_event: str, quantite: int, motif: Optional[str]) -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"INSERT INTO mortalites(lot_id, date_event, quantite, motif) VALUES(%s,%s,%s,%s)",
				(lot_id, date_event, quantite, motif),
			)
			conn.commit()
	finally:
		conn.close()


def record_partial_sale(lot_id: int, date_vente: str, quantite: int, prix_unitaire: float, client: Optional[str]) -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			# insert sale event
			cur.execute(
				"INSERT INTO ventes_animaux(lot_id, date_vente, quantite, prix_unitaire, client) VALUES(%s,%s,%s,%s,%s)",
				(lot_id, date_vente, quantite, prix_unitaire, client),
			)
			# also create recette row for bookkeeping
			montant = quantite * prix_unitaire
			cur.execute(
				"INSERT INTO recettes(type_recette, montant, date_recette, lot_id, client) VALUES('Vente', %s, %s, %s, %s)",
				(montant, date_vente, lot_id, client),
			)
			conn.commit()
	finally:
		conn.close()


def get_lot_counters(lot_id: int) -> Dict[str, int]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute("SELECT nombre_initial FROM lots WHERE id=%s", (lot_id,))
			base = cur.fetchone()
			if not base:
				return {"initial": 0, "mortalites": 0, "vendus": 0, "restants": 0}
			cur.execute("SELECT COALESCE(SUM(quantite),0) AS q FROM mortalites WHERE lot_id=%s", (lot_id,))
			morts = cur.fetchone()["q"]
			cur.execute("SELECT COALESCE(SUM(quantite),0) AS q FROM ventes_animaux WHERE lot_id=%s", (lot_id,))
			vendus = cur.fetchone()["q"]
			restants = base["nombre_initial"] - morts - vendus
			return {"initial": base["nombre_initial"], "mortalites": morts, "vendus": vendus, "restants": restants}
	finally:
		conn.close()

def record_slaughter(
    lot_id: int, 
    date_abattage: str, 
    quantite: int, 
    poids_unitaire: Optional[float] = None
) -> None:
    """
    Enregistre un événement d'abattage (slaughter) pour un lot.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Cette table (abattages) doit exister dans votre base de données.
            cur.execute(
                """
                INSERT INTO abattages (lot_id, date_abattage, quantite, poids_unitaire)
                VALUES (%s, %s, %s, %s)
                """,
                (lot_id, date_abattage, quantite, poids_unitaire)
            )
            conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'abattage du lot {lot_id} : {e}")
        if conn:
            conn.rollback()
        raise 
    finally:
        if conn:
            conn.close()


def list_mortalites(lot_id: int) -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute(
				"SELECT id, date_event, quantite, motif FROM mortalites WHERE lot_id=%s ORDER BY date_event DESC, id DESC",
				(lot_id,),
			)
			return cur.fetchall()
	finally:
		conn.close()


def list_ventes(lot_id: int) -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute(
				"SELECT id, date_vente, quantite, prix_unitaire, client FROM ventes_animaux WHERE lot_id=%s ORDER BY date_vente DESC, id DESC",
				(lot_id,),
			)
			return cur.fetchall()
	finally:
		conn.close()


