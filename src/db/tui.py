from .backend.memory import StudentTable
from .backend.errors import InvalidAgeError, DuplicateIDError

class Student_tui:

    def __init__(self):
        self.current_table: StudentTable | None = None
        self.current_table_name: str | None = None

    def _print_menu(self) -> None:
        print("\n=== База студентов ===")
        print("1. Создать таблицу")
        print("2. Выбрать/сменить таблицу")
        print("3. Добавить запись")
        print("4. Показать все записи")
        print("5. Найти записи по фильтру")
        print("6. Обновить запись")
        print("7. Удалить запись")
        print("0. Выход")



    def _read_int(self, prompt: str) -> int:
        
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            
            except ValueError:
                print("Ошибка: введите целое число.")



    def _add_student(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        print("\nДобавление записи")

        student_id = self._read_int("id: ")
        first_name = input("first_name: ").strip()
        second_name = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()
        try:
            record = self.current_table.create_record(
                student_id, first_name, second_name, age, sex)
            print(f"Запись добавлена: {record}")

        except (InvalidAgeError, DuplicateIDError, ValueError) as exc:
            print(f"Ошибка: {exc}")



    def _print_records(self, records: list) -> None:

        if not records:
            print("Записи не найдены.")
            return

        for record in records:
            print(record)



    def _create_table(self) -> None:

        print("\n=== Создание таблицы ===")
        name = input("Название таблицы: ").strip()

        if not name:
            print("Ошибка: название таблицы не может быть пустым.")
            return
        try:
            self.current_table = StudentTable.create_table(name)
            self.current_table_name = name
            print(f"Таблица '{name}' создана и выбрана для работы.")
        except ValueError as exc:
            print(f"Ошибка: {exc}")


    def _select_table(self) -> None:

        tables = StudentTable.list_tables()
        if not tables:
            print("Нет созданных таблиц. Сначала создайте таблицу (пункт 1).")
            return
        print("\nДоступные таблицы:")
        for i, name in enumerate(tables, 1):
            print(f"  {i}. {name}")

        try:
            
            choice = int(input("Выберите номер таблицы: "))
            table_name = tables[choice - 1]
            self.current_table = StudentTable(table_name)
            self.current_table_name = table_name 
            print(f"Выбрана таблица: '{self.current_table_name}'")
        except (ValueError, IndexError):
            print("Неверный выбор!")


    def _show_all_students(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        print(f"\nСписок записей в таблице '{self.current_table_name}'")
        records = self.current_table.get_all()
        self._print_records(records)


    def _read_optional_int(self, prompt: str) -> int | None:

        while True:
            raw = input(prompt).strip()

            if raw == "":
                return None

            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")



    def _find_students_by_filter(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        print(f"\nПоиск по фильтру в таблице '{self.current_table_name}' (Enter = пропустить поле)")

        student_id = self._read_optional_int("id: ")
        first_name = input("first_name: ").strip() or None
        second_name = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex_input = input("sex: ").strip()

        sex = sex_input.lower() if sex_input else None

        records = self.current_table.select_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex,
        )

        self._print_records(records)


    def _update_student(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        print(f"\nОбновление записи в таблице '{self.current_table}'")

        student_id = self._read_int("Введите ID студента: ")
        existing = self.current_table.select_record(student_id=student_id)
        if not existing:
            print(f"Ошибка: студент с ID= {student_id} не найден")
            return
        
        print(f"Текущие данные: {existing[0]}")
        print("\nОставьте поле пустым, чтобы не менять")

        new_first_name = input(f"Новое имя (было: {existing[0][1]}): ").strip()
        new_second_name = input(f"Новая фамилия (было: {existing[0][2]}): ").strip()
        new_age = input(f"Новый возраст (было: {existing[0][3]}): ").strip()
        new_sex = input(f"Новый пол (было: {existing[0][4]}): ").strip()


        changes = {}
        if new_first_name:
            changes['first_name'] = new_first_name
        if new_second_name:
            changes['second_name'] = new_second_name
        if new_age:
            try:
                age_int = int(new_age)
                if age_int < 0:
                    print("Ошибка: возраст не может быть отрицательным")
                    return
                changes['age'] = age_int
            except ValueError:
                print("Ошибка: возраст должен быть целым числом")
                return
        if new_sex:
            if new_sex not in ["M", "m", "F", "f"]:
                print("Ошибка: пол должен быть 'M' или 'F'")
                return
            changes['sex'] = new_sex


        if not changes:
            print("Ничего не изменено")
            return
        
        
        try:
            updated =  self.current_table.update_record(student_id, **changes)
            if updated:
                print(f"Запись обновлена: {updated}")
            else:
                print("Ошибка при обновлении")
        except ValueError as exc:
            print(f"Ошибка: {exc}")


    def _delete_student(self) -> None:

        if self.current_table is None:
            print("Ошибка: сначала создайте или выберите таблицу.")
            return
        
        print(f"\nУдаление записи из таблицы '{self.current_table}'")

        all_records = self.current_table.get_all()
        if not all_records:
            print("Таблица пуста.")
            return
        
        print("\nВсе записи:")
        for record in all_records:
            print(f"  ID: {record[0]} - {record[1]} {record[2]}")
        

        student_id = self._read_int("\nВведите ID записи: ")
        
        existing = self.current_table.select_record(student_id=student_id)
        if not existing:
            print(f"Запись с ID={student_id} не найден.")
            return
        
        print(f"\nЗапись для удаления: {existing[0]}")
        confirm = input("Вы уверены? (y/n): ").strip().lower()
        
        if confirm == 'y' or confirm == 'yes' or confirm == 'да':
            deleted = self.current_table.delete_record(student_id)
            if deleted:
                print(f"Запись с ID={student_id} успешно удалена.")
            else:
                print("Ошибка при удалении")
        else:
            print("Удаление отменено.")



    def run(self) -> None:

        while True:
            self._print_menu()

            action = input("Выберите действие: ").strip()

            if action == "1":
                self._create_table()

            elif action == "2":
                self._select_table()

            elif action == "3":
                self._add_student()

            elif action == "4":
                self._show_all_students()

            elif action == "5":
                self._find_students_by_filter()
            
            elif action == "6":
                self._update_student()
            
            elif action == "7":
                self._delete_student()

            elif action == "0":
                print("Выход из программы.")
                break

            else:
                print("Неизвестная команда. Повторите ввод.")

def run() -> None:
    app = Student_tui()
    app.run()