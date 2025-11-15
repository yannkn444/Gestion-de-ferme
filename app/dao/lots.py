from typing import List, Dict, Optional, Tuple

from app.db import get_connection


def list_lots(search: Optional[str] = None) -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			base_select = (
				"""
				SELECT l.id, l.type_animal, l.date_arrivee, l.nombre_initial, l.poids_moyen, l.source, l.statut, l.remarque,
				  COALESCE(m.q,0) AS morts,
				  COALESCE(v.q,0) AS vendus,
				  (l.nombre_initial - COALESCE(m.q,0) - COALESCE(v.q,0)) AS restants
				FROM lots l
				LEFT JOIN (
				  SELECT lot_id, SUM(quantite) AS q FROM mortalites GROUP BY lot_id
				) m ON m.lot_id = l.id
				LEFT JOIN (
				  SELECT lot_id, SUM(quantite) AS q FROM ventes_animaux GROUP BY lot_id
				) v ON v.lot_id = l.id
				"""
			)
			if search:
				like = f"%{search}%"
				cur.execute(
					base_select
					+ " WHERE l.type_animal LIKE %s OR l.source LIKE %s OR l.statut LIKE %s ORDER BY l.id DESC",
					(like, like, like),
				)
			else:
				cur.execute(base_select + " ORDER BY l.id DESC")
			return cur.fetchall()
	finally:
		conn.close()


def create_lot(
	type_animal: str,
	date_arrivee: str,
	nombre_initial: int,
	poids_moyen: Optional[float],
	source: Optional[str],
	remarque: Optional[str],
) -> int:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"""
				INSERT INTO lots(type_animal, date_arrivee, nombre_initial, poids_moyen, source, remarque)
				VALUES(%s,%s,%s,%s,%s,%s)
				""",
				(type_animal, date_arrivee, nombre_initial, poids_moyen, source, remarque),
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
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute(
				"SELECT id, type_animal, date_arrivee, nombre_initial, poids_moyen, source, statut, remarque FROM lots WHERE id=%s",
				(id_,),
			)
			return cur.fetchone()
	finally:
		conn.close()


def close_lot(id_: int, statut: str = "Vendu") -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute("UPDATE lots SET statut=%s WHERE id=%s", (statut, id_))
			conn.commit()
	finally:
		conn.close()


def list_active_lots() -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute(
				"SELECT id, type_animal, date_arrivee, nombre_initial FROM lots WHERE statut='Actif' ORDER BY id DESC"
			)
			return cur.fetchall()
	finally:
		conn.close()


