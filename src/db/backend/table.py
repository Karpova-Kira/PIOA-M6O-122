from typing import Any

from .errors import MissingColumnError, UnknownColumnError


class Table:
    """Таблица с фиксированным набором колонок."""

    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []

        if records is not None:
            for record in records:
                self.insert_record(record)

    def insert_record(self, record: dict[str, Any]) -> None:
        """Добавляет запись, если она соответствует схеме таблицы."""
        missing_columns = [column for column in self.columns if column not in record]
        if missing_columns:
            raise MissingColumnError(
                f"Отсутствует поле '{missing_columns[0]}' в записи."
            )

        extra_columns = [column for column in record if column not in self.columns]
        if extra_columns:
            raise UnknownColumnError(
                f"Поле '{extra_columns[0]}' не определено в структуре таблицы."
            )

        self.records.append(record.copy())

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        """Возвращает записи, удовлетворяющие всем переданным фильтрам."""
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )

        if not filters:
            return [record.copy() for record in self.records]

        result: list[dict[str, Any]] = []
        for record in self.records:
            if all(record.get(key) == value for key, value in filters.items()):
                result.append(record.copy())

        return result
    
    def update_record(self, record_id: int, **kwargs: Any) -> dict[str, Any] | None:
        """Обновляет запись по ID (ID должен быть в данных)."""
        for i, record in enumerate(self.records):
            if record.get("id") == record_id:
                # Проверяем, что обновляемые поля существуют в схеме
                for key in kwargs:
                    if key not in self.columns:
                        raise UnknownColumnError(
                            f"Поле '{key}' не определено в структуре таблицы."
                        )
                # Обновляем запись
                updated_record = record.copy()
                updated_record.update(kwargs)
                self.records[i] = updated_record
                return updated_record.copy()
        return None

    def delete_record(self, record_id: int) -> bool:
        """Удаляет запись по ID."""
        for i, record in enumerate(self.records):
            if record.get("id") == record_id:
                del self.records[i]
                return True
        return False

    def get_all(self) -> list[dict[str, Any]]:
        """Возвращает все записи."""
        return [record.copy() for record in self.records]