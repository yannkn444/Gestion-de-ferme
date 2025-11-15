import os
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


def run_sql_file(cursor, sql_path: Path) -> None:
	with sql_path.open("r", encoding="utf-8") as f:
		sql = f.read()
	# naive split by ';' while keeping simple. This assumes statements end with ';' and no procedures.
	statements = [s.strip() for s in sql.split(';') if s.strip()]
	for stmt in statements:
		cursor.execute(stmt)


def main():
	project_root = Path(__file__).resolve().parents[1]
	load_dotenv()  # load .env if present

	db_host = os.getenv("DB_HOST", "localhost")
	db_port = int(os.getenv("DB_PORT", "3306"))
	db_user = os.getenv("DB_USER", "root")
	db_password = os.getenv("DB_PASSWORD", "")

	# Connect without database to allow CREATE DATABASE
	conn = mysql.connector.connect(host=db_host, port=db_port, user=db_user, password=db_password)
	cursor = conn.cursor()
	try:
		sql_file = project_root / "migrations" / "001_init.sql"
		if not sql_file.exists():
			raise FileNotFoundError(f"Migration introuvable: {sql_file}")
		run_sql_file(cursor, sql_file)
		conn.commit()
		print("Base de données initialisée avec succès.")
	except Exception as e:
		conn.rollback()
		raise
	finally:
		cursor.close()
		conn.close()


if __name__ == "__main__":
	try:
		main()
	except Exception as ex:
		print(f"Erreur: {ex}")
		sys.exit(1)

