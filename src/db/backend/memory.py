
from .errors import TableAlreadyExistsError, UnknownColumnError, MissingColumnError, TableNotFoundError
from typing import Any, Optional




class Table:

    def __init__(self, table_name: str, columns: list[str]) -> None:
        self.table_name = table_name
        self.columns = [col.strip().lower() for col in columns]
        self._records: list[dict[str, Any]] = []
        
    def get_schema(self) -> list[str]:
        return self.columns

    def create_record(self, record: dict[str, Any]) -> dict[str, Any]:
        clean_record = {k.strip().lower(): v for k, v in record.items()}
        for key in clean_record:
            if key not in self.columns:
                raise UnknownColumnError(f"Колонка '{key}' отсутствует в схеме таблицы.")

        for col in self.columns:
            if col not in clean_record:
                raise MissingColumnError(f"Пропущена обязательная колонка: '{col}'.")

        if 'id' in clean_record:
            for rec in self._records:
                if 'id' in rec and rec['id'] == clean_record['id']:
                    raise ValueError(f"Запись с id={clean_record['id']} уже существует.")

        self._records.append(clean_record)
        return clean_record
        

    def select_record(self, filters: dict[str, Any]) -> list[dict[str, Any]]:

        clean_filters = {k.strip().lower(): v for k, v in filters.items() if v is not None}

        for key in clean_filters:
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестная колонка в фильтре: '{key}'.")

        if not clean_filters:
            return [rec.copy() for rec in self._records]

        result = []
        for rec in self._records:
            match = True
            for k, v in clean_filters.items():
                if isinstance(rec[k], str) and isinstance(v, str):
                    if rec[k].lower() != v.lower():
                        match = False
                        break
                elif rec[k] != v:
                    match = False
                    break
            if match:
                result.append(rec.copy())

        return result
        

    def get_all(self) -> list[dict[str, Any]]:
        return [rec.copy() for rec in self._records]

    
    def update_record(self, record_id:Any, changes: dict[str, Any]) -> Optional[dict[str, Any]]:
        if 'id' not in self.columns:
            raise UnknownColumnError("В таблице нет колонки 'id' для обновления.")

        clean_changes = {k.strip().lower(): v for k, v in changes.items() if v is not None}
        for key in clean_changes:
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестная колонка '{key}'.")

        for rec in self._records:
            if rec.get('id') == record_id:
                for k, v in clean_changes.items():
                    rec[k] = v
                return rec.copy()
        return None

    def delete_record(self, record_id: int) -> bool:
        if 'id' not in self.columns:
            raise UnknownColumnError("В таблице нет колонки 'id' для удаления.")

        for i, rec in enumerate(self._records):
            if rec.get('id') == record_id:
                del self._records[i]
                return True
        return False

class MemoryDatabase:

    def __init__(self) -> None:
        self.tables: dict[str, Table] = {}

    def create_table(self, table_name: str, columns: list[str]) -> Table:
        name_clean = table_name.strip()
        if self._table_exists(name_clean):
            raise TableAlreadyExistsError(f"Таблица '{name_clean}' уже существует.")
        if not columns:
            raise ValueError("Таблица должна содержать хотя бы одну領колонку.")

        new_table = Table(name_clean, columns)
        self.tables[name_clean] = new_table
        return new_table

    def get_table(self, table_name: str) -> Table:
        name_clean = table_name.strip()
        if not self._table_exists(name_clean):
            raise TableNotFoundError(f"Таблица '{name_clean}' не найдена.")
        return self.tables[name_clean]

    def list_tables(self) -> list[str]:
        return list(self.tables.keys())

    def _table_exists(self, table_name: str) -> bool:
        return table_name in self.tables

    def clear(self) -> None:
        self.tables.clear()