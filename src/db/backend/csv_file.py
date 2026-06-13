
import csv
from pathlib import Path
from typing import Any

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError, TableAlreadyExistsError
from .table import Table


class CSVFileDatabase(Database):
    """База данных, которая хранит таблицы в CSV-файлах."""

    def __init__(self, directory: str = "data_csv") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._tables = {}
            
    def create_table(self, table_name: str, columns: dict[str, str]) -> None:
        table_path = self._get_table_path(table_name)
        
        if table_path.exists() or table_name in self._tables:
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует.")

        table = Table(table_name, columns)
        
        self._tables[table_name] = table
        self._save_table(table_name, table)

    def list_tables(self) -> list[str]:
        return [p.stem for p in self.directory.glob("*.csv")]

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _parse_value(self, value: str) -> Any:
        val_strip = value.strip()
        if val_strip.isdigit() or (val_strip.startswith(('-', '+')) and val_strip[1:].isdigit()):
            return int(val_strip)
        return value

    def _load_table(self, table_name: str) -> Table:
        
        if table_name in self._tables:
            return self._tables[table_name]

        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")

        try:
            with table_path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if len(rows) < 2:
                    raise InvalidStorageDataError(
                        "Файл таблицы пуст или имеет некорректную структуру."
                    )
                
                col_names = rows[0]
                col_types = rows[1]

                if len(col_names) != len(col_types):
                    raise InvalidStorageDataError(
                        f"Ошибка структуры CSV: количество заголовков ({len(col_names)}) "
                        f"не совпадает с количеством типов ({len(col_types)})."
                    )
                
                if any(not name.strip() for name in col_names):
                    raise InvalidStorageDataError("Ошибка структуры CSV: заголовок содержит пустые имена колонок.")
                
                columns = {name: t for name, t in zip(col_names, col_types)}
                
                table = Table(table_name, columns)
                records = []
                
                for row in rows[2:]:
                    if not row or all(not cell for cell in row):
                        continue
                    if len(row) != len(col_names):
                        raise InvalidStorageDataError(f"Ошибка в строке: количество значений не соответствует схеме.")
                    record = {}
                    for i, col_name in enumerate(col_names):
                        val = row[i] 
                        if columns[col_name] == "int" and val != "":
                            try:
                                record[col_name] = int(val)
                            except ValueError:
                                raise InvalidStorageDataError(f"Поле '{col_name}' должно быть int, получено: '{val}'.")
    
                        else:
                            record[col_name] = str(val)
                    records.append(record)
                    
                table.records = records
                
                self._tables[table_name] = table
                return table
                
        except OSError as error:
            raise InvalidStorageDataError(f"Ошибка ввода-вывода при чтении '{table_name}': {error}") from error
        except (csv.Error, IndexError, ValueError) as error:
            raise InvalidStorageDataError(f"Ошибка парсинга CSV-файла '{table_name}': {error}") from error
       
    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        try:
            with table_path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                
                col_names = list(table.columns.keys())
                col_types = list(table.columns.values())
                
                writer.writerow(col_names)
                writer.writerow(col_types)
                
                for record in table.records:
                    row = [str(record.get(column, "")) for column in table.columns]
                    writer.writerow(row)
        except OSError as error:
            raise InvalidStorageDataError(f"Ошибка ввода-вывода при записи '{table_name}': {error}") from error

    def _get_table_path(self, table_name: str) -> Path:
        clean_name = Path(table_name).name
        return self.directory / f"{clean_name}.csv"

    def get_csv_content(self, table_name: str) -> str:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        
        with table_path.open("r", encoding="utf-8") as file:
            return file.read()