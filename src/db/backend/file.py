import json
from pathlib import Path
from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class FileDatabase(Database):
    """База данных, которая хранит таблицы в JSON-файлах."""

    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def list_tables(self) -> list[str]:
        return [p.stem for p in self.directory.glob("*.json")]

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                "Файл таблицы содержит некорректный JSON."
            ) from error
        except OSError as error:
            raise InvalidStorageDataError(f"Ошибка ввода-вывода при чтении файла: {error}") from error

        if not isinstance(data, dict):
            raise InvalidStorageDataError("Некорректная структура JSON: корневой элемент должен быть объектом.")

        return self._deserialize_table(data)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        try:
            with table_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self._serialize_table(table),
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
        except OSError as error:
            raise InvalidStorageDataError(f"Ошибка ввода-вывода при записи JSON '{table_name}': {error}") from error
    
    def _get_table_path(self, table_name: str) -> Path:
        clean_name = Path(table_name).name
        return self.directory / f"{clean_name}.json"

    def _serialize_table(self, table: Table) -> dict:
        return {
            "name": table.name,
            "columns": table.columns,
            "records": table.records
        }

    def _deserialize_table(self, data: dict) -> Table:
        if not isinstance(data.get("columns"), dict):
            raise InvalidStorageDataError("Файл поврежден: структура 'columns' отсутствует или не является словарем.")
        
        if not isinstance(data.get("records"), list):
            raise InvalidStorageDataError("Файл поврежден: структура 'records' отсутствует или не является списком.")

        if not all(isinstance(rec, dict) for rec in data["records"]):
            raise InvalidStorageDataError("Файл поврежден: одна из записей в 'records' не является словарем.")
        
        table = Table(data.get("name", "unknown_table"), data["columns"])
        table.records = data["records"]
        return table