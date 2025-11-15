from pathlib import Path
import pandas as pd

from app.db import get_connection


def export_query_to_csv(query: str, params: tuple, out_path: Path) -> None:
	conn = get_connection()
	try:
		df = pd.read_sql(query, conn, params=params)
		df.to_csv(out_path, index=False, encoding="utf-8-sig")
	finally:
		conn.close()


def export_query_to_excel(query: str, params: tuple, out_path: Path, sheet_name: str = "Feuille1") -> None:
	conn = get_connection()
	try:
		df = pd.read_sql(query, conn, params=params)
		df.to_excel(out_path, index=False, sheet_name=sheet_name)
	finally:
		conn.close()


def export_table_csv(table: str, out_path: Path) -> None:
	export_query_to_csv(f"SELECT * FROM {table}", (), out_path)


def export_table_excel(table: str, out_path: Path) -> None:
	export_query_to_excel(f"SELECT * FROM {table}", (), out_path, sheet_name=table)


