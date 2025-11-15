import mysql.connector
from mysql.connector import pooling
from typing import Optional

from app.config import get_config


_connection_pool: Optional[pooling.MySQLConnectionPool] = None


def init_connection_pool(pool_size: int = 5) -> None:
	global _connection_pool
	if _connection_pool is not None:
		return
	config = get_config()
	_connection_pool = pooling.MySQLConnectionPool(
		pool_name="farm_pool",
		pool_size=pool_size,
		host=config.db_host,
		port=config.db_port,
		database=config.db_name,
		user=config.db_user,
		password=config.db_password,
		charset="utf8mb4",
		collation="utf8mb4_general_ci",
	)


def get_connection():
	if _connection_pool is None:
		init_connection_pool()
	return _connection_pool.get_connection()


