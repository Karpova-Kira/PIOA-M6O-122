from .backend.errors import (
    TableAlreadyExistsError, TableNotFoundError,
    MissingColumnError, UnknownColumnError, InvalidStorageDataError
)
from src.db.backend.file import FileDatabase
from src.db.backend.memory import MemoryDatabase
from .backend.csv_file import CSVFileDatabase

class StudentTUI:

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
        print("\n=== База студентов ===")
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

    def _add_record(self) -> None:

        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return

        print(f"\nДобавление записи в таблицу '{self.current_table_name}'")
        
        try:
            if hasattr(self.db, 'get_schema'):
                schema = self.db.get_schema(self.current_table_name)
            elif hasattr(self.db, '_load_table'):
                table = self.db._load_table(self.current_table_name)
                schema = table.columns
            else:
                print("Предупреждение: не удалось получить схему таблицы.")
                print("Используются стандартные поля: id, first_name, second_name, age, sex")
                schema = ("id", "first_name", "second_name", "age", "sex")
        except Exception as e:
            print(f"Не удалось получить схему таблицы: {e}")
            schema = ("id", "first_name", "second_name", "age", "sex")
        
        record = {}
        for column in schema:
            if column == "id":
                record[column] = self._read_int(f"{column}: ")
            elif column in ["age", "year"]:
                record[column] = self._read_int(f"{column}: ")
            elif column in ["sex", "gender"]:
                value = self._read_string(f"{column} (M/F): ")
                record[column] = value.upper()
            else:
                record[column] = self._read_string(f"{column}: ")

        try:
            self.db.insert_record(self.current_table_name, record)
            print(f"Запись добавлена: {record}")
        except (MissingColumnError, UnknownColumnError, ValueError) as exc:
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
            columns = ("id", "first_name", "second_name", "age", "sex")
            print(f"Использованы стандартные поля: {', '.join(columns)}")
        else:
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
        print("Для файловой базы данных таблицы — это файлы в папке 'data/'")
        print("In-memory база данных не сохраняет таблицы между запусками.")
        
        if hasattr(self.db, 'tables'):
            tables = list(self.db.tables.keys())
            if tables:
                for name in tables:
                    print(f"  - {name}")
            else:
                print("Нет созданных таблиц.")
        else:
            print("Используется файловая БД. Проверьте папку 'data/' для просмотра таблиц.")

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

        filters = {}
        
        student_id = self._read_optional_int("id: ")
        if student_id is not None:
            filters["id"] = student_id
        
        first_name = input("first_name: ").strip()
        if first_name:
            filters["first_name"] = first_name
        
        second_name = input("second_name: ").strip()
        if second_name:
            filters["second_name"] = second_name
        
        age = self._read_optional_int("age: ")
        if age is not None:
            filters["age"] = age
        
        sex = input("sex: ").strip()
        if sex:
            filters["sex"] = sex.upper()

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

        record_id = self._read_int("Введите ID записи: ")

        try:
            # Сначала проверим, существует ли запись
            existing = self.db.select_records(self.current_table_name, id=record_id)
            if not existing:
                print(f"Ошибка: запись с ID={record_id} не найдена.")
                return

            print(f"Текущие данные: {existing[0]}")
            print("\nОставьте поле пустым, чтобы не менять")

            changes = {}
            
            new_first_name = input(f"Новое имя (было: {existing[0].get('first_name', '')}): ").strip()
            if new_first_name:
                changes["first_name"] = new_first_name
            
            new_second_name = input(f"Новая фамилия (было: {existing[0].get('second_name', '')}): ").strip()
            if new_second_name:
                changes["second_name"] = new_second_name
            
            new_age = input(f"Новый возраст (было: {existing[0].get('age', '')}): ").strip()
            if new_age:
                try:
                    age_int = int(new_age)
                    if age_int < 0:
                        print("Ошибка: возраст не может быть отрицательным")
                        return
                    changes["age"] = age_int
                except ValueError:
                    print("Ошибка: возраст должен быть целым числом")
                    return
            
            new_sex = input(f"Новый пол (было: {existing[0].get('sex', '')}): ").strip()
            if new_sex:
                sex_upper = new_sex.upper()
                if sex_upper not in ["M", "F"]:
                    print("Ошибка: пол должен быть 'M' или 'F'")
                    return
                changes["sex"] = sex_upper

            if not changes:
                print("Ничего не изменено")
                return

            updated = self.db.update_record(self.current_table_name, record_id, **changes)
            if updated:
                print(f"Запись обновлена: {updated}")
            else:
                print("Ошибка при обновлении")
        except (TableNotFoundError, UnknownColumnError, ValueError) as exc:
            print(f"Ошибка: {exc}")

    

    def _delete_record(self) -> None:

        if self.current_table_name is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        print(f"\nУдаление записи из таблицы '{self.current_table_name}'")

        try:
            all_records = self.db.get_all_records(self.current_table_name)
            if not all_records:
                print("Таблица пуста.")
                return
            
            print("\nВсе записи:")
            for record in all_records:
                print(f"  ID: {record.get('id')} - {record.get('first_name', '')} {record.get('second_name', '')}")
            

            record_id = self._read_int("\nВведите ID записи: ")
            
            existing = self.db.select_records(self.current_table_name, id=record_id)
            if not existing:
                print(f"Запись с ID={record_id} не найден.")
                return
            
            print(f"\nЗапись для удаления: {existing[0]}")
            confirm = input("Вы уверены? (y/n): ").strip().lower()
            
            if confirm in ['y', 'yes', 'да']:
                deleted = self.db.delete_record(self.current_table_name, record_id)
                if deleted:
                    print(f"Запись с ID={record_id} успешно удалена.")
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
            
            print(f"\nСтруктура таблицы '{self.current_table_name}'")
            try:
                columns = self.db.get_schema(self.current_table_name)
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
    app = StudentTUI()
    app.run()


