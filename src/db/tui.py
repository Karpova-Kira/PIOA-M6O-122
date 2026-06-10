from .backend.memory import MemoryDatabase, Table
from .backend.errors import DatabaseError, TableAlreadyExistsError, TableNotFoundError
from typing import Any

class DatabaseTUI:

    def __init__(self):
        self.db = MemoryDatabase()
        self.current_table: Table | None = None  
        self.current_table_name: str | None = None

    def _print_menu(self) -> None:
        print("\n=== База данных ===")
        if self.current_table_name:
            print(f" Активная таблица: [{self.current_table_name}]")
        else:
            print(" Активная таблица: [Не выбрана]")
        print("-----------------------------------")
        print("1. Создать таблицу")
        print("2. Выбрать/сменить таблицу")
        print("3. Показать список таблиц")
        print("4. Добавить запись")
        print("5. Показать все записи")
        print("6. Найти записи по фильтру")
        print("7. Обновить запись")
        print("8. Удалить запись")
        print("9. Показать схему таблицы")
        print("0. Выход")

    def _parse_value(self, raw: str) -> Any:
        if raw.isdigit():
            return int(raw)
        if raw.startswith('-') and raw[1:].isdigit():
            return int(raw)
        return raw


    def _add_record(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        print("\nДобавление записи")

        columns = self.current_table.get_schema()
        record = {}

        for column in columns:
            while True:
                raw_val = input(f"Введите значение для '{column}': ").strip()
                if not raw_val:
                    print("Ошибка: поле не может быть пустым.")
                    continue

                parsed_val = self._parse_value(raw_val)

                if column in ('age', 'возраст'):
                    if not isinstance(parsed_val, int) or parsed_val < 0:
                        print("Ошибка: возраст должен быть целым неотрицательным числом!")
                        continue

                if column in ('sex', 'gender', 'пол'):
                    val_lower = str(parsed_val).lower()
                    if val_lower in ('m', 'f', 'м', 'ж'):
                        parsed_val = 'm' if val_lower in ('m', 'м') else 'f'
                    else:
                        print("Ошибка: допустимы только значения 'm' или 'f' (м/ж)!")
                        continue

                record[column] = parsed_val
                break
        
        try:
            new_rec = self.current_table.create_record(record)
            print(f"Запись успешно добавлена: {new_rec}")
        except Exception as e:
            print(f"Ошибка СУБД: {e}")


    def _print_records(self, records: list) -> None:

        if not records:
            print("Записи не найдены.")
            return

        columns = self.current_table.get_schema()
        header = " | ".join(f"{col.upper():<12}" for col in columns)
        print("-" * len(header))
        print(header)
        print("-" * len(header))

        for rec in records:
            row = " | ".join(f"{str(rec.get(col, '')):<12}" for col in columns)
            print(row)



    def _create_table(self) -> None:

        print("\n=== Создание таблицы ===")
        name = input("Название таблицы: ").strip()

        if not name:
            print("Ошибка: название таблицы не может быть пустым.")
            return
        raw_columns = input("Введите имена колонок через запятую: ")
        columns = [col.strip() for col in raw_columns.split(",") if col.strip()]

        if not columns:
            print("Ошибка: таблица должна иметь хотя бы одну колонку!")
            return
        
        try:
            self.current_table = self.db.create_table(name, columns)
            self.current_table_name = name
            print(f"Таблица '{name}' создана: {columns}")
        except ValueError as exc:
            print(f"Ошибка: {exc}")


    def _select_table(self) -> None:

        tables = self.db.list_tables()
        if not tables:
            print("Нет созданных таблиц. Сначала создайте таблицу (пункт 1).")
            return
        print("\nДоступные таблицы:")
        for i, name in enumerate(tables, 1):
            print(f"  {i}. {name}")

        try:
            
            choice = int(input("Выберите номер таблицы: "))
            if 1 <= choice <= len(tables):
                t_name = tables[choice - 1]
                self.current_table = self.db.get_table(t_name)
                self.current_table_name = t_name
                print(f"Выбрана таблица: '{t_name}'")
            else:
                print("Ошибка: неверный номер.")
        except (ValueError, TableNotFoundError) as exc:
            print(f"Ошибка: {exc}")

    def _show_tables(self) -> None:
        tables = self.db.list_tables()
        if not tables:
            print("В базе данных пока нет таблиц.")
            return
        print("\n=== Список таблиц в БД ===")
        for name in tables:
            print(f" - {name}")

    def _show_all_records(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        print(f"\nСписок записей в таблице '{self.current_table_name}'")
        self._print_records(self.current_table.get_all())


    def _find_records_by_filter(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        print(f"\nПоиск по фильтру в таблице '{self.current_table_name}' (Enter = пропустить поле)")

        columns = self.current_table.get_schema()
        filters = {}

        for column in columns:
            raw = input(f"Фильтр для '{column}': ").strip()
            if raw:
                filters[column] = self._parse_value(raw)

        records = self.current_table.select_record(filters)
        self._print_records(records)

    def _update_record(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        columns = self.current_table.get_schema()
        if 'id' not in columns:
            print("Ошибка: обновление поддерживается только в таблицах с полем 'id'.")
            return

        record_id = self._parse_value(input("Введите ID записи для обновления: ").strip())
        existing = self.current_table.select_record({'id': record_id})

        if not existing:
            print(f"Ошибка: запись   с ID= {record_id} не найден")
            return
        
        print(f"Текущие данные: {existing[0]}")
        print("\nОставьте поле пустым, чтобы не менять")

        changes = {}
        for column in columns:
            if column == 'id':
                continue
            raw = input(f"Новое значение для '{column}' (было: {existing[0][column]}): ").strip()
            if raw:
                parsed_val = self._parse_value(raw)
                
                if column in ('age', 'возраст') and (not isinstance(parsed_val, int) or parsed_val < 0):
                    print("Ошибка: некорректный возраст. Изменения отменены.")
                    return
                if column in ('sex', 'gender', 'пол'):
                    val_lower = str(parsed_val).lower()
                    if val_lower in ('m', 'f', 'м', 'ж'):
                        parsed_val = 'm' if val_lower in ('m', 'м') else 'f'
                    else:
                        print("Ошибка: некорректный пол. Изменения отменены.")
                        return

                changes[column] = parsed_val


        if not changes:
            print("Ничего не изменено")
            return
        
        updated = self.current_table.update_record(record_id, changes)
        print(f"Запись успешно обновлена: {updated}")
        
        

    def _delete_record(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        columns = self.current_table.get_schema()
        if 'id' not in columns:
            print("Ошибка: удаление поддерживается только в таблицах с полем 'id'.")
            return

        record_id = self._parse_value(input("Введите ID записи для удаления: ").strip())
        existing = self.current_table.select_record({'id': record_id})

        if not existing:
            print(f"Запись с ID={record_id} не найдена.")
            return
        
        print(f"\nЗапись для удаления: {existing[0]}")
        confirm = input("Вы уверены? (y/n): ").strip().lower()
        
        if confirm in ('y', 'yes', 'да'):
            deleted = self.current_table.delete_record(record_id)
            if deleted:
                print(f"Запись с ID={record_id} успешно удалена.")
            else:
                print("Ошибка при удалении")
        else:
            print("Удаление отменено.")


    def _show_schema(self) -> None:
        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        print(f"\n=== Схема таблицы '{self.current_table_name}' ===")
        columns = self.current_table.get_schema()
        print(f"Колонки: {', '.join(columns)}")


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
                self._find_records_by_filter()
            
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