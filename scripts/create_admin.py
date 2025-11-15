import os
import sys
from getpass import getpass

import bcrypt
from dotenv import load_dotenv

from app.db import get_connection, init_connection_pool


def main():
	load_dotenv()
	name = os.getenv("ADMIN_NAME") or input("Nom Admin: ")
	email = os.getenv("ADMIN_EMAIL") or input("Email Admin: ")
	password = os.getenv("ADMIN_PASSWORD") or getpass("Mot de passe Admin: ")

	password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

	init_connection_pool()
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute("USE gestion_elevage")
			cur.execute("SELECT id FROM utilisateurs WHERE email=%s", (email,))
			row = cur.fetchone()
			if row:
				print("Un utilisateur avec cet email existe déjà.")
			else:
				cur.execute(
					"INSERT INTO utilisateurs(nom, email, mot_de_passe, role) VALUES(%s,%s,%s,%s)",
					(name, email, password_hash, "Admin"),
				)
				conn.commit()
				print("Administrateur créé avec succès.")
	finally:
		conn.close()


if __name__ == "__main__":
	try:
		main()
	except Exception as ex:
		print(f"Erreur: {ex}")
		sys.exit(1)

