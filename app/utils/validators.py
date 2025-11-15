from datetime import datetime


def is_valid_date(date_str: str) -> bool:
	try:
		datetime.strptime(date_str, "%Y-%m-%d")
		return True
	except Exception:
		return False


def parse_positive_float(value: str) -> float:
	val = float(value)
	if val <= 0:
		raise ValueError("La valeur doit être > 0")
	return val


def parse_non_negative_int(value: str) -> int:
	val = int(value)
	if val < 0:
		raise ValueError("La valeur doit être >= 0")
	return val


