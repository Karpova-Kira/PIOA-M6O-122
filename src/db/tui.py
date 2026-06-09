from .backend.errors import (
    TableAlreadyExistsError, TableNotFoundError,
    MissingColumnError, UnknownColumnError
)
from .backend.file import FileDatabase
from .backend.memory import MemoryDatabase
from .backend.csv_file import CSVFileDatabase

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

    def _parse_input_value(self, raw: str) -> any:
            if raw.isdigit() or (raw.startswith(('-', '+')) and raw[1:].isdigit()):
                return int(raw)
            return raw

    def _add_record(self) -> None:

        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return

        print(f"\nДобавление записи в таблицу '{self.current_table_name}'")
        
        try:
            columns = self.db.get_schema(self.current_table_name)
        except Exception as e:
            print(f"Ошибка при получении схемы: {e}")
            return
        
        record = {}
        for column in columns:
            col_lower = column.lower().strip()
            
            while True:
                raw_val = input(f"Введите значение для '{column}': ").strip()
                
                if col_lower in ('sex', 'gender', 'пол'):
                    val_check = raw_val.lower()
                    if val_check in ('m', 'f', 'м', 'ж'):
                        record[column] = 'm' if val_check in ('m', 'м') else 'f'
                        break
                    else:
                        print("Ошибка: для этого поля допустимы только значения 'm' или 'f' (м/ж)!")
                

                elif col_lower in ('age', 'возраст'):
                    parsed_val = self._parse_input_value(raw_val)
                    if isinstance(parsed_val, int):
                        if parsed_val >= 0:
                            record[column] = parsed_val
                            break
                        else:
                            print("Ошибка: возраст не может быть отрицательным!")
                    else:
                        print("Ошибка: возраст должен быть целым числом!")
                else:
                    if not raw_val:
                        print("Ошибка: значение не может быть пустым.")
                        continue
                    
                    record[column] = self._parse_input_value(raw_val)
                    break            

        try:
            self.db.insert_record(self.current_table_name, record)
            print(f"Запись успешно добавлена: {record}")
        except (MissingColumnError, UnknownColumnError) as exc:
            print(f"Ошибка: {exc}")

    def _print_records(self, records: list) -> None:

        if not records:
            print("Записи не найдены.")
            return

        for record in records:
            print(record)



    def _create_table(self) -> None:

        print("\n=== Создание таблицы ===")
        name = self._read_string("Название таблицы: ")

        print("Введите названия полей через запятую (например: id,name,age)")
        columns_input = input("Поля: ").strip()
        
        if not columns_input:
           print("Ошибка: нужно указать хотя бы одно поле.")
           return
        
        columns = tuple(col.strip() for col in columns_input.split(",") if col.strip())

        if not columns:
            print("Ошибка: таблица должна иметь хотя бы одно поле.")
            return

        try:
            self.db.create_table(name, columns)
            self.current_table_name = name
            print(f"Таблица '{name}' создана и выбрана для работы.")
            print(f"Поля таблицы: {', '.join(columns)}")
        except TableAlreadyExistsError as exc:
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
        except Exception as e:
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
        
        columns = self.db.get_schema(self.current_table_name)
        print(f"\nОбновление записи в таблице '{self.current_table_name}'")

        key_column = input(f"Выберите ключевое поле для поиска записи {columns}: ").strip()
        if key_column not in columns:
            print("Ошибка: такого поля нет в таблице.")
            return
            
        raw_key_value = input(f"Введите значение поля '{key_column}': ").strip()
        key_value = self._parse_input_value(raw_key_value)

        search_filter = {key_column: key_value}
        existing_records = self.db.select_records(self.current_table_name, **search_filter)
        if not existing_records:
            print("Ошибка: запись с такими критериями не найдена.")
            return
        
        existing = existing_records[0]
        print(f"Текущие данные: {existing}")
        print("Оставьте поле пустым, чтобы не изменять его.")

        changes = {}
        for column in columns:
            if column == key_column:
                continue
            raw_val = input(f"Новое {column} (было: {existing.get(column, '')}): ").strip()
            if raw_val:
                changes[column] = self._parse_input_value(raw_val)

        if not changes:
            print("Ничего не изменено.")
            return

        try:
            updated = self.db.update_record(self.current_table_name, key_column, key_value, **changes)
            if updated:
                print(f"Запись обновлена: {updated}")
            else:
                print("Ошибка при обновлении.")
        except Exception as exc:
            print(f"Ошибка: {exc}")
        
    def _delete_record(self) -> None:

        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        print(f"\nУдаление записи из таблицы '{self.current_table_name}'")

        try:
            columns = self.db.get_schema(self.current_table_name)            
            key_column = input(f"Выберите ключевое поле для поиска записи {columns}: ").strip()
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
                print(f"\nСтруктура таблицы '{self.current_table_name}':")
                print(f"Поля: {', '.join(columns)}")
            except Exception as e:
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


