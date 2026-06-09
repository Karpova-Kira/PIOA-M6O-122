
import csv
from pathlib import Path
from typing import Any

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class CSVFileDatabase(Database):
    """База данных, которая хранит таблицы в CSV-файлах."""

    def __init__(self, directory: str = "data_csv") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

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
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )

        try:
            with table_path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if len(rows) < 1:
                    raise InvalidStorageDataError(
                        "Файл таблицы пуст или имеет некорректную структуру."
                    )
                
                columns = tuple(rows[0])
                
                records = []
                for row in rows[1:]:
                    if not row or all(not cell for cell in row):
                        continue
                    
                    record = {}
                    for i, column in enumerate(columns):
                        if i < len(row):
                            record[column] = self._parse_value(row[i])
                        else:
                            record[column] = ""
                    records.append(record)
                
                return Table(columns, records)
                
        except (csv.Error, IndexError) as error:
            raise InvalidStorageDataError(
                f"Ошибка при чтении CSV-файла '{table_name}': {error}") from error
                
       
    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)

        with table_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            
            writer.writerow(table.columns)
            
            for record in table.records:
                row = [str(record.get(column, "")) for column in table.columns]
                writer.writerow(row)

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"

    def get_csv_content(self, table_name: str) -> str:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        
        with table_path.open("r", encoding="utf-8") as file:
            return file.read()