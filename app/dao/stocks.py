from typing import List, Dict, Optional

from app.db import get_connection


def list_stocks() -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute(
				"SELECT id, nom_produit, type_produit, quantite, unite, COALESCE(seuil_alerte, 0) AS seuil_alerte, date_ajout FROM stocks ORDER BY nom_produit ASC"
			)
			return cur.fetchall()
	finally:
		conn.close()


def create_product(nom_produit: str, type_produit: str, quantite: int, unite: Optional[str], seuil: Optional[int]) -> int:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"INSERT INTO stocks(nom_produit, type_produit, quantite, unite, seuil) VALUES(%s,%s,%s,%s,%s)",
				(nom_produit, type_produit, quantite, unite, seuil),
			)
			conn.commit()
			return cur.lastrowid
	finally:
		conn.close()


def add_entry(stock_id: int, qty: int) -> None:
	if qty <= 0:
		raise ValueError("Quantité doit être positive")
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute("UPDATE stocks SET quantite = quantite + %s WHERE id=%s", (qty, stock_id))
			conn.commit()
	finally:
		conn.close()


def add_exit(stock_id: int, qty: int) -> None:
	if qty <= 0:
		raise ValueError("Quantité doit être positive")
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			# validate available qty
			cur.execute("SELECT quantite FROM stocks WHERE id=%s", (stock_id,))
			row = cur.fetchone()
			if not row:
				raise ValueError("Article introuvable")
			if row[0] < qty:
				raise ValueError("Stock insuffisant")
			cur.execute("UPDATE stocks SET quantite = quantite - %s WHERE id=%s", (qty, stock_id))
			conn.commit()
	finally:
		conn.close()


def set_threshold(stock_id: int, seuil: int) -> None:
	if seuil < 0:
		raise ValueError("Seuil invalide")
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute("UPDATE stocks SET seuil=%s WHERE id=%s", (seuil, stock_id))
			conn.commit()
	finally:
		conn.close()


