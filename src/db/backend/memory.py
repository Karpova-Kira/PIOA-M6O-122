type StudentRecord = tuple[int, str, str, int, str]

Student: list[StudentRecord] = []

def create_record(
    student_id: int,   # Уникальный идентификатор записи
    first_name: str,   # Имя
    second_name: str,  # Фамилия
    age: int,          # Возраст
    sex: str,          # Пол
) -> StudentRecord:

    sex = sex.lower()

    if sex not in ['м', 'ж']:
        raise ValueError("Пол должен быть 'м' или 'ж'")
    
    if age < 0:
        raise ValueError("Поле age не может быть отрицательным.")
    
    if any(record[0] == student_id for record in Student):
        raise ValueError(f"Запись с id={student_id} уже существует.")

    new_record: StudentRecord = (
        student_id,
        first_name.strip(),
        second_name.strip(),
        age,
        sex.strip(),
    )

    Student.append(new_record)
    return new_record


def select_record(
    student_id: int | None = None,   # Фильтр по идентификатору
    first_name: str | None = None,   # Фильтр по имени
    second_name: str | None = None,  # Фильтр по фамилии
    age: int | None = None,          # Фильтр по возрасту
    sex: str | None = None,          # Фильтр по полу
) -> list[StudentRecord]:
    
    if sex is not None:
        sex = sex.lower()

    if (
        student_id is None
        and first_name is None
        and second_name is None
        and age is None
        and sex is None
    ):
        return Student.copy()
    result: list[StudentRecord] = []

    for record in Student:
        if student_id is not None and record[0] != student_id:
            continue

        if first_name is not None and record[1] != first_name:
            continue

        if second_name is not None and record[2] != second_name:
            continue

        if age is not None and record[3] != age:
            continue

        if sex is not None and record[4] != sex:
            continue
        result.append(record)
    return result

def update_record(student_id: int, **kwargs) -> StudentRecord | None:
    
    for i, record in enumerate(Student):
        if record[0] == student_id:
            updated = list(record)

            if "first_name" in kwargs:
                updated[1] = kwargs["first_name"]
                
            if "second_name" in kwargs:
                updated[2] = kwargs["second_name"]

            if "age" in kwargs:
                age = kwargs["age"]
                if age < 0:
                    raise ValueError("Возраст не может быть менбше нуля")
                updated[3] = age

            if "sex" in kwargs:
                sex = kwargs["sex"].lower()
                if sex not in ["м", "ж"]:
                    raise ValueError("Пол должен быть только 'ж' или 'м'")
                updated[4] = sex
        
            Student[i] = tuple(updated)
            return Student[i]
    
    return None

def delete_record(student_id: int) -> bool:
    
    for i, record in enumerate(Student):
        if record[0] == student_id:
            del Student[i]
            return True
    return False