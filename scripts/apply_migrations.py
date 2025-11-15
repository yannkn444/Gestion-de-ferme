import os
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


def run_sql_file(cursor, sql_path: Path) -> None:
	with sql_path.open("r", encoding="utf-8") as f:
		sql = f.read()
	for stmt in [s.strip() for s in sql.split(';') if s.strip()]:
		cursor.execute(stmt)


def main():
	root = Path(__file__).resolve().parents[1]
	load_dotenv()

	db_host = os.getenv("DB_HOST", "localhost")
	db_port = int(os.getenv("DB_PORT", "3306"))
	db_user = os.getenv("DB_USER", "root")
	db_password = os.getenv("DB_PASSWORD", "")

	conn = mysql.connector.connect(host=db_host, port=db_port, user=db_user, password=db_password)
	cursor = conn.cursor()
	try:
		# ensure db exists
		cursor.execute("CREATE DATABASE IF NOT EXISTS gestion_elevage CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
		cursor.execute("USE gestion_elevage")
		for file in sorted((root / "migrations").glob("*.sql")):
			print(f"Applying: {file.name}")
			run_sql_file(cursor, file)
		conn.commit()
		print("Migrations appliquées.")
	except Exception:
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

