from .backend.memory import create_record, select_record, update_record, delete_record

def _print_menu() -> None:
    print("\n=== База студентов ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("4. Обновить запись")
    print("5. Удалить запись")
    print("0. Выход")



def _read_int(prompt: str) -> int:
     while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        
        except ValueError:
            print("Ошибка: введите целое число.")



def _add_student() -> None:
    print("\nДобавление записи")

    student_id = _read_int("id: ")
    first_name = input("first_name: ").strip()
    second_name = input("second_name: ").strip()
    age = _read_int("age: ")
    sex = input("sex: ").strip()
    try:
        record = create_record(student_id, first_name, second_name, age, sex)
        print(f"Запись добавлена: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")



def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
    if not records:
        print("Записи не найдены.")
        return

    for record in records:
        print(record)



def _show_all_students() -> None:
    print("\nСписок записей")
    _print_records(select_record())



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
    print("\nПоиск по фильтру (Enter = пропустить поле)")

    student_id = _read_optional_int("id: ")
    first_name = input("first_name: ").strip() or None
    second_name = input("second_name: ").strip() or None
    age = _read_optional_int("age: ")
    sex_input = input("sex: ").strip()

    sex = sex_input.lower() if sex_input else None

    records = select_record(
        student_id=student_id,
        first_name=first_name,
        second_name=second_name,
        age=age,
        sex=sex,
    )

    _print_records(records)

def _update_student() -> None:
    print("\nОбновление записи")

    student_id = _read_int("Введите ID студента: ")
    existing = select_record(student_id=student_id)
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
        updated = update_record(student_id, **changes)
        if updated:
            print(f"Запись обновлена: {updated}")
        else:
            print("Ошибка при обновлении")
    except ValueError as exc:
        print(f"Ошибка: {exc}")

def _delete_student() -> None:
    print("\nУдаление записи")

    all_students = select_record()
    if not all_students:
        print("База данных пуста.")
        return
    
    print("\nВсе студенты:")
    for student in all_students:
        print(f"  ID: {student[0]} - {student[1]} {student[2]}")
    

    student_id = _read_int("\nВведите ID студента: ")
    
    existing = select_record(student_id=student_id)
    if not existing:
        print(f"Студент с ID={student_id} не найден.")
        return
    
    print(f"\nСтудент для удаления: {existing[0]}")
    confirm = input("Вы уверены? (y/n): ").strip().lower()
    
    if confirm == 'y' or confirm == 'yes' or confirm == 'да':
        deleted = delete_record(student_id)
        if deleted:
            print(f"Запись с ID={student_id} успешно удалена.")
        else:
            print("Ошибка при удалении")
    else:
        print("Удаление отменено.")



def run() -> None:
    while True:
        _print_menu()

        action = input("Выберите действие: ").strip()

        if action == "1":
            _add_student()

        elif action == "2":
            _show_all_students()

        elif action == "3":
            _find_students_by_filter()
        
        elif action == "4":
            _update_student()
        
        elif action == "5":
            _delete_student()

        elif action == "0":
            print("Выход из программы.")
            break

        else:
            print("Неизвестная команда. Повторите ввод.")

