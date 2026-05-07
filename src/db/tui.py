from .backend.memory import create_table, list_tables, create_record, select_record, update_record, delete_record

def _print_menu() -> None:
    print("\n=== База студентов ===")
    print("1. Создать таблицу")
    print("2. Выбрать/сменить таблицу")
    print("3. Добавить запись")
    print("4. Показать все записи")
    print("5. Найти записи по фильтру")
    print("6. Обновить запись")
    print("7. Удалить запись")
    print("0. Выход")



def _read_int(prompt: str) -> int:
     
     while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        
        except ValueError:
            print("Ошибка: введите целое число.")



def _add_student() -> None:

    global current_table
    if current_table is None:
        print("Ошибка: сначала создайте или выберите таблицу.")
        return
    print(f"\nДобавление записи в таблицу '{current_table}'")

    student_id = _read_int("id: ")
    first_name = input("first_name: ").strip()
    second_name = input("second_name: ").strip()
    age = _read_int("age: ")
    sex = input("sex: ").strip()
    try:
        record = create_record(current_table, student_id, first_name, second_name, age, sex)
        print(f"Запись добавлена: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")



def _print_records(records: list) -> None:

    if not records:
        print("Записи не найдены.")
        return

    for record in records:
        print(record)

current_table: str | None = None


def _create_table() -> None:

    global current_table
    print("\n=== Создание таблицы ===")
    name = input("Название таблицы: ").strip()

    try:
        create_table(name)
        current_table = name
        print(f"Таблица '{name}' создана и выбрана для работы.")
    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _select_table() -> None:

    global current_table

    tables = list_tables()
    if not tables:
        print("Нет созданных таблиц. Сначала создайте таблицу (пункт 1).")
        return
    print("\nДоступные таблицы:")
    for i, name in enumerate(tables, 1):
        print(f"  {i}. {name}")

    try:
        choice = int(input("Выберите номер таблицы: "))
        current_table = tables[choice - 1]
        print(f"Выбрана таблица: '{current_table}'")
    except (ValueError, IndexError):
        print("Неверный выбор!")


def _show_all_students() -> None:

    global current_table
    if current_table is None:
        print("Ошибка: сначала создайте или выберите таблицу.")
        return
    print(f"\nСписок записей в таблице '{current_table}'")
    _print_records(select_record(current_table))


def _read_optional_int(prompt: str) -> int | None:

    while True:
        raw = input(prompt).strip()

        if raw == "":
            return None

        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")



def _find_students_by_filter() -> None:

    global current_table
    if current_table is None:
        print("Ошибка: сначала создайте или выберите таблицу.")
        return
    
    print(f"\nПоиск по фильтру в таблице '{current_table}' (Enter = пропустить поле)")

    student_id = _read_optional_int("id: ")
    first_name = input("first_name: ").strip() or None
    second_name = input("second_name: ").strip() or None
    age = _read_optional_int("age: ")
    sex_input = input("sex: ").strip()

    sex = sex_input.lower() if sex_input else None

    records = select_record(
        current_table,
        student_id=student_id,
        first_name=first_name,
        second_name=second_name,
        age=age,
        sex=sex,
    )

    _print_records(records)


def _update_student() -> None:

    global current_table
    if current_table is None:
        print("Ошибка: сначала создайте или выберите таблицу.")
        return
    
    print(f"\nОбновление записи в таблице '{current_table}'")

    student_id = _read_int("Введите ID студента: ")
    existing = select_record(current_table, student_id=student_id)
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
        if new_sex not in ['м', 'ж', 'М', 'Ж']:
            print("Ошибка: пол должен быть 'м' или 'ж'")
            return
        changes['sex'] = new_sex


    if not changes:
        print("Ничего не изменено")
        return
    
    
    try:
        updated = update_record(current_table, student_id, **changes)
        if updated:
            print(f"Запись обновлена: {updated}")
        else:
            print("Ошибка при обновлении")
    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _delete_student() -> None:

    global current_table
    if current_table is None:
        print("Ошибка: сначала создайте или выберите таблицу.")
        return
    
    print(f"\nУдаление записи из таблицы '{current_table}'")

    all_records = select_record(current_table)
    if not all_records:
        print("Таблица пуста.")
        return
    
    print("\nВсе записи:")
    for record in all_records:
        print(f"  ID: {record[0]} - {record[1]} {record[2]}")
    

    student_id = _read_int("\nВведите ID записи: ")
    
    existing = select_record(current_table, student_id=student_id)
    if not existing:
        print(f"Запись с ID={student_id} не найден.")
        return
    
    print(f"\nСтудент для удаления: {existing[0]}")
    confirm = input("Вы уверены? (y/n): ").strip().lower()
    
    if confirm == 'y' or confirm == 'yes' or confirm == 'да':
        deleted = delete_record(current_table, student_id)
        if deleted:
            print(f"Запись с ID={student_id} успешно удалена.")
        else:
            print("Ошибка при удалении")
    else:
        print("Удаление отменено.")



def run() -> None:

    global current_table
    while True:
        _print_menu()

        action = input("Выберите действие: ").strip()

        if action == "1":
            _create_table()

        elif action == "2":
            _select_table()

        elif action == "3":
            _add_student()

        elif action == "4":
            _show_all_students()

        elif action == "5":
            _find_students_by_filter()
        
        elif action == "6":
            _update_student()
        
        elif action == "7":
            _delete_student()

        elif action == "0":
            print("Выход из программы.")
            break

        else:
            print("Неизвестная команда. Повторите ввод.")

