import os
from dataclasses import dataclass
from dotenv import load_dotenv


def _load_env() -> None:
	# Load from .env if present, else allow system env; also allow config.env.example copied to .env
	load_dotenv(override=False)


@dataclass
class AppConfig:
	db_host: str
	db_port: int
	db_name: str
	db_user: str
	db_password: str
	app_locale: str
	currency: str


def get_config() -> AppConfig:
	_load_env()
	return AppConfig(
		db_host=os.getenv("DB_HOST", "localhost"),
		db_port=int(os.getenv("DB_PORT", "3306")),
		db_name=os.getenv("DB_NAME", "gestion_elevage"),
		db_user=os.getenv("DB_USER", "root"),
		db_password=os.getenv("DB_PASSWORD", ""),
		app_locale=os.getenv("APP_LOCALE", "fr_CM"),
		currency=os.getenv("CURRENCY", "XAF"),
	)


