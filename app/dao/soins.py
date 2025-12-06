from typing import List, Dict, Optional

from app.db import get_connection


def list_soins(lot_id: Optional[int] = None) -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			if lot_id:
				cur.execute(
					"""
					SELECT s.id, s.lot_id, s.date_soin, s.type_soin, s.description, s.cout, s.effectue_par,
					       l.type_animal
					FROM soins s
					JOIN lots l ON l.id = s.lot_id
					WHERE s.lot_id=%s
					ORDER BY s.date_soin DESC, s.id DESC
					""",
					(lot_id,),
				)
			else:
				cur.execute(
					"""
					SELECT s.id, s.lot_id, s.date_soin, s.type_soin, s.description, s.cout, s.effectue_par,
					       l.type_animal
					FROM soins s
					JOIN lots l ON l.id = s.lot_id
					ORDER BY s.date_soin DESC, s.id DESC
					"""
				)
			return cur.fetchall()
	finally:
		conn.close()


def create_soin(lot_id: int, date_soin: str, type_soin: str, description: Optional[str], cout: float, effectue_par: Optional[str]) -> int:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"INSERT INTO soins(lot_id, date_soin, type_soin, description, cout, effectue_par) VALUES(%s,%s,%s,%s,%s,%s)",
				(lot_id, date_soin, type_soin, description, cout, effectue_par),
			)
			conn.commit()
			return cur.lastrowid
	finally:
		conn.close()


def update_soin(id_: int, lot_id: int, date_soin: str, type_soin: str, description: Optional[str], cout: float, effectue_par: Optional[str]) -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"""
				UPDATE soins
				SET lot_id=%s, date_soin=%s, type_soin=%s, description=%s, cout=%s, effectue_par=%s
				WHERE id=%s
				""",
				(lot_id, date_soin, type_soin, description, cout, effectue_par, id_),
			)
			conn.commit()
	finally:
		conn.close()


def delete_soin(id_: int) -> None:
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM soins WHERE id=%s", (id_,))
			conn.commit()
	finally:
		conn.close()