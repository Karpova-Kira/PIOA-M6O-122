from typing import Any

from .errors import MissingColumnError, UnknownColumnError, DuplicateIDError


class Table:
    def __init__(self, name: str, columns: dict[str, str] | tuple[str, ...] | list[str]):
        self.name = name
        
        if isinstance(columns, (tuple, list)):
            self.columns = {col: "str" for col in columns}
        else:
            self.columns = columns  
            
        self.records: list[dict[str, Any]] = []

    def _validate_record(self, record: dict[str, Any], is_update: bool = False) -> None:
        for col in record:
            if col not in self.columns:
                raise UnknownColumnError(f"Колонка '{col}' отсутствует в структуре таблицы.")

        if not is_update:
            for col in self.columns:
                if col not in record:
                    raise MissingColumnError(f"Пропущена обязательная колонка '{col}'.")

        for col, value in record.items():
            expected_type = self.columns[col]
            if expected_type == "int":
                if not isinstance(value, int):
                    raise TypeError(f"Поле '{col}' должно иметь тип int, получено {type(value).__name__}.")
            elif expected_type == "str":
                if not isinstance(value, str):
                    raise TypeError(f"Поле '{col}' должно иметь тип str, получено {type(value).__name__}.")

    def insert_record(self, record: dict[str, Any]) -> None:
        
        for col in record:
            if col not in self.columns:
               
                raise UnknownColumnError(f"Колонка '{col}' не определена в структуре таблицы.")
        clean_record = record.copy()

        for col, val in clean_record.items():
            if self.columns.get(col) == "int":
                try:
                    clean_record[col] = int(val)
                except (ValueError, TypeError):
                    raise TypeError(f"Поле '{col}' должно быть типа int.")
            else:
                clean_record[col] = str(val)

        self._validate_record(clean_record, is_update=False)

        if self.columns:
            pk_column = list(self.columns.keys())[0]
            pk_value = clean_record.get(pk_column)
            for existing in self.records:
                if existing.get(pk_column) == pk_value:
                    raise DuplicateIDError(f"Запись с ключевым полем {pk_column}={pk_value} уже существует.")

        self.records.append(clean_record)

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
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
        
        target_record = None
        target_index = -1
        for i, rec in enumerate(self.records):
            if rec.get(key_column) == key_value:
                target_record = rec
                target_index = i
                break

        if target_record is None:
            return None

        updated_project = target_record.copy()
        
        for col, val in kwargs.items():
            if col not in self.columns:
                raise UnknownColumnError(f"Поле '{col}' отсутствует в схеме таблицы.")
            if self.columns[col] == "int":
                try:
                    updated_project[col] = int(val)
                except (ValueError, TypeError):
                    raise TypeError(f"Значение '{val}' для колонки '{col}' должно быть типа int.")
            else:
                updated_project[col] = str(val)

        self._validate_record(updated_project, is_update=True)

        pk_column = list(self.columns.keys())[0]
        if updated_project.get(pk_column) != target_record.get(pk_column):
            new_pk = updated_project.get(pk_column)
            for existing in self.records:
                if existing.get(pk_column) == new_pk:
                    from .errors import DuplicateIDError
                    raise DuplicateIDError(f"Запись с ключевым полем {pk_column}={new_pk} уже существует.")

        self.records[target_index] = updated_project
        return updated_project.copy()
        

    def delete_record(self, key_column: str, key_value: Any) -> bool:
        if key_column not in self.columns:
            raise UnknownColumnError(f"Ключевое поле '{key_column}' не найдено в схеме.")
        initial_count = len(self.records)
        self.records = [rec for rec in self.records if rec.get(key_column) != key_value]
        return len(self.records) < initial_count
        
        

    def get_all(self) -> list[dict[str, Any]]:
        return [record.copy() for record in self.records]