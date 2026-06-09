from typing import Any

from .errors import MissingColumnError, UnknownColumnError


class Table:
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

        if "id" in record:
            current_id = record["id"]
            for existing_record in self.records:
                if existing_record.get("id") == current_id:
                    from .errors import DuplicateIDError  
                    raise DuplicateIDError(f"Запись с id={current_id} уже существует.")

        if "age" in record:
            try:
                age_val = int(record["age"])
                if age_val < 0 or age_val > 150:
                    from .errors import InvalidAgeError
                    raise InvalidAgeError(f"Недопустимый возраст: {age_val}")
            except (ValueError, TypeError):
                from .errors import InvalidAgeError
                raise InvalidAgeError("Поле 'age' должно быть числом.")
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
    
    def update_record(self, key_column: str, key_value: Any, **kwargs: Any) -> dict[str, Any] | None:
        if key_column not in self.columns:
            raise UnknownColumnError(f"Ключевое поле '{key_column}' не найдено в схеме.")
        for key in kwargs:
            if key not in self.columns:
                raise UnknownColumnError(
                    f"Поле '{key}' не определено в структуре таблицы.")

        for i, record in enumerate(self.records):
            if record.get(key_column) == key_value:
                updated_record = record.copy()
                updated_record.update(kwargs)
                self.records[i] = updated_record
                return updated_record.copy()
        return None

    def delete_record(self, key_column: str, key_value: Any) -> bool:
        if key_column not in self.columns:
            raise UnknownColumnError(f"Ключевое поле '{key_column}' не найдено в схеме.")
        initial_count = len(self.records)
        self.records = [rec for rec in self.records if rec.get(key_column) != key_value]
        return len(self.records) < initial_count
        
        

    def get_all(self) -> list[dict[str, Any]]:
        return [record.copy() for record in self.records]