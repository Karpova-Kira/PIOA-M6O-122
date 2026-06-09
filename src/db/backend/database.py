from abc import ABC, abstractmethod
from typing import Any

from .errors import TableAlreadyExistsError
from .table import Table


class Database(ABC):
    """Общий интерфейс базы данных."""

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(
                f"Таблица '{table_name}' уже существует."
            )

        self._save_table(table_name, Table(columns))

    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        table = self._load_table(table_name)
        table.insert_record(record)
        self._save_table(table_name, table)

    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.select_records(**filters)
    
    def update_record(self, table_name: str, key_column: str, key_value: Any, **kwargs: Any) -> dict[str, Any] | None:
        table = self._load_table(table_name)
        result = table.update_record(key_column, key_value, **kwargs)
        if result is not None:
            self._save_table(table_name, table)
        return result

    def delete_record(self, table_name: str, key_column: str, key_value: Any) -> bool:
        table = self._load_table(table_name)
        result = table.delete_record(key_column, key_value)
        if result:
            self._save_table(table_name, table)
        return result

    def get_all_records(self, table_name: str) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.get_all()

    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        """Проверяет наличие таблицы."""


    @abstractmethod
    def _load_table(self, table_name: str) -> Table:
        """Загружает таблицу."""

    @abstractmethod
    def _save_table(self, table_name: str, table: Table) -> None:
        """Сохраняет таблицу."""

    def table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы."""
        return self._table_exists(table_name)
    
    def get_schema(self, table_name: str) -> tuple[str, ...]:
        """Возвращает схему таблицы (список полей)."""
        table = self._load_table(table_name)
        return table.columns