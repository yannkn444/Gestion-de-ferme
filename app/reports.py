from typing import Dict, List, Optional

from app.db import get_connection


def kpis_by_lot(lot_id: int) -> Dict[str, float]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute("SELECT nombre_initial, poids_moyen FROM lots WHERE id=%s", (lot_id,))
			lot = cur.fetchone() or {"nombre_initial": 0, "poids_moyen": None}
			cur.execute("SELECT COALESCE(SUM(quantite),0) AS morts FROM mortalites WHERE lot_id=%s", (lot_id,))
			morts = cur.fetchone()["morts"]
			cur.execute("SELECT COALESCE(SUM(quantite),0) AS vendus FROM ventes_animaux WHERE lot_id=%s", (lot_id,))
			vendus = cur.fetchone()["vendus"]
			cur.execute("SELECT COALESCE(SUM(cout),0) AS cout_soins FROM soins WHERE lot_id=%s", (lot_id,))
			cout_soins = float(cur.fetchone()["cout_soins"])
			cur.execute("SELECT COALESCE(SUM(montant),0) AS depenses FROM depenses WHERE lot_id=%s", (lot_id,))
			depenses = float(cur.fetchone()["depenses"])
			cur.execute("SELECT COALESCE(SUM(montant),0) AS recettes FROM recettes WHERE lot_id=%s", (lot_id,))
			recettes = float(cur.fetchone()["recettes"])
			restants = lot["nombre_initial"] - morts - vendus
			mortalite_pct = (morts / lot["nombre_initial"]) * 100 if lot["nombre_initial"] else 0.0
			marge = recettes - depenses
			return {
				"initial": float(lot["nombre_initial"]),
				"morts": float(morts),
				"vendus": float(vendus),
				"restants": float(restants),
				"mortalite_pct": float(mortalite_pct),
				"depenses": depenses,
				"recettes": recettes,
				"marge": marge,
			}
	finally:
		conn.close()


def monthly_summary(year: int, month: int) -> Dict[str, float]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute(
				"SELECT COALESCE(SUM(montant),0) AS s FROM depenses WHERE YEAR(date_depense)=%s AND MONTH(date_depense)=%s",
				(year, month),
			)
			dep = float(cur.fetchone()["s"]) 
			cur.execute(
				"SELECT COALESCE(SUM(montant),0) AS s FROM recettes WHERE YEAR(date_recette)=%s AND MONTH(date_recette)=%s",
				(year, month),
			)
			rec = float(cur.fetchone()["s"]) 
			return {"depenses": dep, "recettes": rec, "solde": rec - dep}
	finally:
		conn.close()


def lots_overview() -> List[Dict]:
	conn = get_connection()
	try:
		with conn.cursor(dictionary=True) as cur:
			cur.execute(
				"""
				SELECT l.id, l.type_animal, l.nombre_initial,
				  COALESCE(m.q,0) AS morts,
				  COALESCE(v.q,0) AS vendus,
				  (l.nombre_initial - COALESCE(m.q,0) - COALESCE(v.q,0)) AS restants
				FROM lots l
				LEFT JOIN (SELECT lot_id, SUM(quantite) AS q FROM mortalites GROUP BY lot_id) m ON m.lot_id=l.id
				LEFT JOIN (SELECT lot_id, SUM(quantite) AS q FROM ventes_animaux GROUP BY lot_id) v ON v.lot_id=l.id
				ORDER BY l.id DESC
				"""
			)
			rows = cur.fetchall()
			for r in rows:
				r["mortalite_pct"] = (r["morts"] / r["nombre_initial"]) * 100 if r["nombre_initial"] else 0.0
			return rows
	finally:
		conn.close()


