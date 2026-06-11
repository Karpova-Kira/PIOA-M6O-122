from .backend.errors import (
    TableAlreadyExistsError, TableNotFoundError,
    MissingColumnError, UnknownColumnError, InvalidStorageDataError, DuplicateIDError
)
from .backend.file import FileDatabase
from .backend.memory import MemoryDatabase
from .backend.csv_file import CSVFileDatabase
from typing import Any

class DatabaseTUI:

    def __init__(self, skip_db_choice: bool = False):
        self.current_table_name: str | None = None

        if not skip_db_choice:
            print("\n=== Выбор типа базы данных ===")
            print("1. In-memory (данные не сохраняются)")
            print("2. File database (JSON) — данные сохраняются в папке 'data/'")
            print("3. File database (CSV) — данные сохраняются в папке 'data_csv/'")
            
            choice = input("Выберите тип (1, 2 или 3): ").strip()
            
            if choice == "2":
                self.db = FileDatabase()
                print("Используется JSON-файловая база данных. Данные сохраняются в папке 'data/'")
            elif choice == "3":
                self.db = CSVFileDatabase()
                print("Используется CSV-файловая база данных. Данные сохраняются в папке 'data_csv/'")
            else:
                self.db = MemoryDatabase()
                print("Используется in-memory база данных. Данные будут потеряны после закрытия программы.")
        else:
            self.db = MemoryDatabase()
    

    def _print_menu(self) -> None:
        print("\n=== База данных ===")
        print("1. Создать таблицу")
        print("2. Выбрать/сменить таблицу")
        print("3. Показать все таблицы")
        print("4. Добавить запись")
        print("5. Показать все записи")
        print("6. Найти записи по фильтру")
        print("7. Обновить запись")
        print("8. Удалить запись")
        print("9. Показать структуру таблицы")
        print("0. Выход")



    def _read_int(self, prompt: str) -> int:
        
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_string(self, prompt: str) -> str:
        while True:
            raw = input(prompt).strip()
            if raw:
                return raw
            print("Ошибка: поле не может быть пустым.")

    def _print_records(self, records: list[dict[str, Any]]) -> None:
        if not records:
            print("(таблица пуста или записей по фильтру не найдено)")
            return
            
        for idx, record in enumerate(records, start=1):
            row_str = ", ".join(f"{key}: {val}" for key, val in record.items())
            print(f"  {idx}. {row_str}")

    def _parse_input_value(self, raw: str) -> Any:
            if raw.isdigit() or (raw.startswith(('-', '+')) and raw[1:].isdigit()):
                return int(raw)
            return raw

    def _add_record(self) -> None:

        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return

        print(f"\nДобавление записи в таблицу '{self.current_table_name}'")
        
        try:
            schema = self.db.get_schema(self.current_table_name)
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")
            return
        except InvalidStorageDataError as e:
            print(f"Ошибка работы с хранилищем при чтении схемы: {e}")
            return
        
        record = {}
        record = {}
        for col_name, col_type in schema.items():
            while True:
                raw = input(f"  {col_name} ({col_type}): ").strip()
                
                if not raw:
                    record[col_name] = ""
                    break
                if col_type == "int":
                    try:
                        record[col_name] = int(raw)
                        break 
                    except ValueError:
                        print("Ошибка: введите число.")
                else:
                    record[col_name] = raw
                    break

        try:
            self.db.insert_record(self.current_table_name, record)
            print("\n[Успех] Запись успешно добавлена.")
            
        except (UnknownColumnError, MissingColumnError) as e:
            print(f"\n[Ошибка схемы]: {e}")
        except TypeError as e:
            print(f"\n[Ошибка типов данных]: {e}")
        except DuplicateIDError as e:
            print(f"\n[Ошибка уникальности]: {e}")
        except TableNotFoundError as e:
            print(f"\n[Ошибка таблицы]: {e}")
        except InvalidStorageDataError as e:
            print(f"\n[Критическая ошибка диска]: Ошибка при записи файла таблицы: {e}")



    def _create_table(self) -> None:

        print("\n=== Создание таблицы ===")
        name = self._read_string("Название таблицы: ")

        print("Введите поля и типы через запятую (например: id:int,name:str,age:int)")
        columns_input = input("Поля: ").strip()
        
        if not columns_input:
            print("Ошибка: нужно указать хотя бы одно поле.")
            return

        columns = {}
        for item in columns_input.split(","):
            if not item.strip():
                continue
            if ":" in item:
                col_name, col_type = item.split(":", 1)
                col_name = col_name.strip()
                col_type = col_type.strip().lower()
                if col_type not in ("int", "str"):
                    col_type = "str"  
            else:
                col_name = item.strip()
                col_type = "str"  
                
            if col_name:
                columns[col_name] = col_type

        if not columns:
            print("Ошибка: таблица должна иметь хотя бы одно валидное поле.")
            return

        try:
            self.db.create_table(name, columns)
            self.current_table_name = name
            print(f"Таблица '{name}' успешно создана и выбрана.")
            schema_str = ", ".join([f"{k} ({v})" for k, v in columns.items()])
            print(f"Структура: {schema_str}")
        except (TableAlreadyExistsError, InvalidStorageDataError) as exc:
            print(f"Ошибка: {exc}")


    def _select_table(self) -> None:

        print("\n=== Выбор таблицы ===")
        name = input("Введите имя таблицы: ").strip()
        
        if not name:
            print("Ошибка: имя таблицы не может быть пустым.")
            return
        
        if self.db.table_exists(name):
            self.current_table_name = name
            print(f"Выбрана таблица: '{self.current_table_name}'")
        else:
            print(f"Ошибка: таблица '{name}' не найдена.")

    def _show_tables(self) -> None:
        print("\n=== Список таблиц ===")
        try:
            tables = self.db.list_tables()
            if tables:
                for name in tables:
                    print(f"  - {name}")
            else:
                print("Нет созданных таблиц.")
        except InvalidStorageDataError as e:
            print(f"Ошибка при получении списка таблиц: {e}")

    def _show_all_records(self) -> None:
        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
            
        print(f"\nСписок записей в таблице '{self.current_table_name}'")

        try:
            records = self.db.get_all_records(self.current_table_name)
            self._print_records(records)  
        except TableNotFoundError as exc:
            print(f"Ошибка: {exc}")
    
    def _read_optional_int(self, prompt: str) -> int | None:

        while True:
            raw = input(prompt).strip()

            if raw == "":
                return None

            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")



    def _find_records(self) -> None:

        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return

        print(f"\nПоиск по фильтру в таблице '{self.current_table_name}' (Enter = пропустить поле)")
        columns = self.db.get_schema(self.current_table_name)
        filters = {}
        for column in columns:
            raw_val = input(f"{column}: ").strip()
            if raw_val:
                filters[column] = self._parse_input_value(raw_val)

        try:
            records = self.db.select_records(self.current_table_name, **filters)
            self._print_records(records)
        except (TableNotFoundError, UnknownColumnError) as exc:
            print(f"Ошибка: {exc}")

    def _update_record(self) -> None:

        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        print(f"\nОбновление записи в таблице '{self.current_table_name}'")
        try:
            schema = self.db.get_schema(self.current_table_name)
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")
            return
        except InvalidStorageDataError as e:
            print(f"Ошибка работы с хранилищем при чтении схемы: {e}")
            return

        print("Введите имя ключевого поля и его значение для поиска записи:")
        pk_column = input("  Имя ключевого поля (например, id): ").strip()
        if pk_column not in schema:
            print(f"Ошибка: Поля '{pk_column}' нет в структуре этой таблицы.")
            return

        raw_pk_value = input(f"  Значение поля {pk_column}: ").strip()
        
        if schema[pk_column] == "int":
            try:
                key_value = int(raw_pk_value)
            except ValueError:
                print(f"Ошибка: Поле '{pk_column}' должно быть числом.")
                return
        else:
            key_value = raw_pk_value

        print("\nВведите НОВЫЕ значения для полей (оставьте пустым, если менять не нужно):")
        kwargs = {}
        for col_name, col_type in schema.items():
            raw_input = input(f"  {col_name} ({col_type}) [без изменений]: ").strip()
            
            if not raw_input:
                continue  
                
            if col_type == "int":
                try:
                    kwargs[col_name] = int(raw_input)
                except ValueError:
                    kwargs[col_name] = raw_input  
            else:
                kwargs[col_name] = raw_input

        if not kwargs:
            print("Отмена: Не введено ни одного изменения.")
            return

        try:
            updated = self.db.update_record(self.current_table_name, pk_column, key_value, **kwargs)
            
            if updated:
                print("\n[Успех] Запись успешно обновлена.")
                print(f"Обновленная строка: {updated}")
            else:
                print("\n[Внимание] Запись с таким ключом не найдена. Ничего не изменено.")
                
        except (UnknownColumnError, MissingColumnError) as e:
            print(f"\n[Ошибка схемы]: {e}")
        except TypeError as e:
            print(f"\n[Ошибка типов данных]: {e}")
        except DuplicateIDError as e:
            print(f"\n[Ошибка уникальности]: {e}")
        except TableNotFoundError as e:
            print(f"\n[Ошибка таблицы]: {e}")
        except InvalidStorageDataError as e:
            print(f"\n[Критическая ошибка диска]: Ошибка при сохранении изменений: {e}")

    def _delete_record(self) -> None:

        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        print(f"\nУдаление записи из таблицы '{self.current_table_name}'")

        try:
            columns = self.db.get_schema(self.current_table_name)            
            key_column = input(f"Выберите ключевое поле для поиска записи {list(columns.keys())}: ").strip()
            if key_column not in columns:
                print("Ошибка: такого поля нет в таблице.")
                return
                
            raw_key_value = input(f"Введите значение поля '{key_column}': ").strip()
            key_value = self._parse_input_value(raw_key_value)

            search_filter = {key_column: key_value}
            existing = self.db.select_records(self.current_table_name, **search_filter)
            if not existing:
                print(f"Запись не найдена.")
                return
            
            print(f"\nЗапись для удаления: {existing[0]}")
            confirm = input("Вы уверены? (y/n): ").strip().lower()
            
            if confirm in ['y', 'yes', 'да']:
                if self.db.delete_record(self.current_table_name, key_column, key_value):                    
                    print(f"Запись удалена.")
                else:
                    print("Ошибка при удалении")
            else:
                print("Удаление отменено.")
        except TableNotFoundError as exc:
            print(f"Ошибка: {exc}")


    def _show_schema(self) -> None:
            if self.current_table_name is None:
                print("Ошибка: сначала создайте или выберите таблицу.")
                return
            
            try:
                columns = self.db.get_schema(self.current_table_name) 
                if isinstance(columns, (tuple, list)):
                    columns = {col: "str" for col in columns}

                print(f"\nСтруктура таблицы '{self.current_table_name}':")
                schema_str = ", ".join([f"{k} ({v})" for k, v in columns.items()])
                print(f"Поля: {schema_str}")
            except (TableNotFoundError, InvalidStorageDataError) as e:
                print(f"Ошибка: {e}")

    def run(self) -> None:

        while True:
            self._print_menu()

            action = input("Выберите действие: ").strip()

            if action == "1":
                self._create_table()

            elif action == "2":
                self._select_table()

            elif action == "3":
                self._show_tables()

            elif action == "4":
                self._add_record()

            elif action == "5":
                self._show_all_records()

            elif action == "6":
                self._find_records()
            
            elif action == "7":
                self._update_record()
            
            elif action == "8":
                self._delete_record()

            elif action == "9":
                self._show_schema()

            elif action == "0":
                print("Выход из программы.")
                break

            else:
                print("Неизвестная команда. Повторите ввод.")

def run() -> None:
    app = DatabaseTUI()
    app.run()


