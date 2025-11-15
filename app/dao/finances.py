from typing import List, Dict, Optional, Tuple

from app.db import get_connection


# Dépenses
def list_depenses(start: Optional[str] = None, end: Optional[str] = None, lot_id: Optional[int] = None) -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			query = "SELECT id, type_depense, description, montant, date_depense, lot_id FROM depenses"
			conds = []
			params: Tuple = ()
			if start:
				conds.append("date_depense >= %s")
				params += (start,)
			if end:
				conds.append("date_depense <= %s")
				params += (end,)
			if lot_id:
				conds.append("(lot_id = %s)")
				params += (lot_id,)
			if conds:
				query += " WHERE " + " AND ".join(conds)
			query += " ORDER BY date_depense DESC, id DESC"
			cur.execute(query, params)
			return cur.fetchall()
	finally:
		conn.close()


def create_depense(type_depense: str, montant: float, date_depense: str, description: Optional[str], lot_id: Optional[int]) -> int:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"INSERT INTO depenses(type_depense, description, montant, date_depense, lot_id) VALUES(%s,%s,%s,%s,%s)",
				(type_depense, description, montant, date_depense, lot_id),
			)
			conn.commit()
			return cur.lastrowid
	finally:
		conn.close()


def update_depense(id_: int, type_depense: str, montant: float, date_depense: str, description: Optional[str], lot_id: Optional[int]) -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"UPDATE depenses SET type_depense=%s, description=%s, montant=%s, date_depense=%s, lot_id=%s WHERE id=%s",
				(type_depense, description, montant, date_depense, lot_id, id_),
			)
			conn.commit()
	finally:
		conn.close()


def delete_depense(id_: int) -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM depenses WHERE id=%s", (id_,))
			conn.commit()
	finally:
		conn.close()


# Recettes
def list_recettes(start: Optional[str] = None, end: Optional[str] = None, lot_id: Optional[int] = None) -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			query = "SELECT id, type_recette, montant, date_recette, lot_id, client FROM recettes"
			conds = []
			params: Tuple = ()
			if start:
				conds.append("date_recette >= %s")
				params += (start,)
			if end:
				conds.append("date_recette <= %s")
				params += (end,)
			if lot_id:
				conds.append("(lot_id = %s)")
				params += (lot_id,)
			if conds:
				query += " WHERE " + " AND ".join(conds)
			query += " ORDER BY date_recette DESC, id DESC"
			cur.execute(query, params)
			return cur.fetchall()
	finally:
		conn.close()


def create_recette(type_recette: str, montant: float, date_recette: str, lot_id: Optional[int], client: Optional[str]) -> int:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"INSERT INTO recettes(type_recette, montant, date_recette, lot_id, client) VALUES(%s,%s,%s,%s,%s)",
				(type_recette, montant, date_recette, lot_id, client),
			)
			conn.commit()
			return cur.lastrowid
	finally:
		conn.close()


def update_recette(id_: int, type_recette: str, montant: float, date_recette: str, lot_id: Optional[int], client: Optional[str]) -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"UPDATE recettes SET type_recette=%s, montant=%s, date_recette=%s, lot_id=%s, client=%s WHERE id=%s",
				(type_recette, montant, date_recette, lot_id, client, id_),
			)
			conn.commit()
	finally:
		conn.close()


def delete_recette(id_: int) -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM recettes WHERE id=%s", (id_,))
			conn.commit()
	finally:
		conn.close()


# Résumé
def summary(start: Optional[str] = None, end: Optional[str] = None, lot_id: Optional[int] = None) -> Dict[str, float]:
	deps = list_depenses(start, end, lot_id)
	recs = list_recettes(start, end, lot_id)
	total_dep = sum(d.get("montant", 0) for d in deps)
	total_rec = sum(r.get("montant", 0) for r in recs)
	return {"depenses": float(total_dep), "recettes": float(total_rec), "solde": float(total_rec - total_dep)}


