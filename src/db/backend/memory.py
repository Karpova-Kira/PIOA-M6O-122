
from .errors import DuplicateIDError, InvalidAgeError 
from typing import Optional

type StudentRecord = tuple[int, str, str, int, str]

TABLES: dict[str, list[StudentRecord]] = {}

ID_COUNTERS: dict[str, int] = {}


def create_table(table_name: str) -> None:
    if table_name in TABLES:
        raise ValueError(f"Таблица '{table_name}' уже существует.")
    TABLES[table_name] = []
    ID_COUNTERS[table_name] = 1
    print(f"Таблица '{table_name}' создана.")


def list_tables() -> list[str]:
    return list(TABLES.keys())


def _get_table(table_name: str) -> list[StudentRecord]:
    if table_name not in TABLES:
        raise ValueError(f"Таблица '{table_name}' не существует.")
    return TABLES[table_name]


class StudentTable:

    def __init__(self) -> None:
        self._student: list[StudentRecord] = []

    def create_record(
        self,
        student_id: int,
        first_name: str,
        second_name: str,
        age: int,
        sex: str,
    ) -> StudentRecord:

        if age < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")

        if any(record[0] == student_id for record in self._student):
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._student.append(new_record)
        return new_record

    def select_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
    ) -> list[StudentRecord]:

        if (
            student_id is None
            and first_name is None
            and second_name is None
            and age is None
            and sex is None
        ):
            return self._student.copy()

        result: list[StudentRecord] = []

        for record in self._student:
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
    
    def update_record(self, record_id: int, **kwargs) -> StudentRecord | None:
        for i, record in enumerate(self._student):
            if record[0] == record_id:
                updated = list(record)

                if "first_name" in kwargs:
                    updated[1] = kwargs["first_name"]
                if "second_name" in kwargs:
                    updated[2] = kwargs["second_name"]
                if "age" in kwargs:
                    age = kwargs["age"]
                    if age < 0:
                        raise ValueError("Возраст не может быть меньше нуля")
                    updated[3] = age
                if "sex" in kwargs:
                    sex = kwargs["sex"].upper()
                    if sex not in ["M", "F"]:
                        raise ValueError("Пол должен быть 'M' или 'F'")
                    updated[4] = sex

                self._student[i] = tuple(updated)
                return self._student[i]
        return None

    def delete_record(self, record_id: int) -> bool:
        for i, record in enumerate(self._student):
            if record[0] == record_id:
                del self._student[i]
                return True
        return False
    
    
def create_record(
    table_name: str,
    student_id: int,   # Уникальный идентификатор записи
    first_name: str,   # Имя
    second_name: str,  # Фамилия
    age: int,          # Возраст
    sex: str,          # Пол
) -> StudentRecord:

    table = _get_table(table_name)
    sex = sex.lower()

    if sex not in ['m', 'f']:
        raise ValueError("Пол должен быть 'm' или 'f'")
    
    if age < 0:
        raise ValueError("Поле age не может быть отрицательным.")
    
    if any(record[0] == student_id for record in table):
        raise ValueError(f"Запись с id={student_id} уже существует в таблице '{table_name}'.")

    new_record: StudentRecord = (
        student_id,
        first_name.strip(),
        second_name.strip(),
        age,
        sex.strip(),
    )

    table.append(new_record)
    return new_record


def select_record(
    table_name: str,
    student_id: Optional[int] = None,   # Фильтр по идентификатору
    first_name: Optional[str] = None,   # Фильтр по имени
    second_name: Optional[str] = None,  # Фильтр по фамилии
    age: Optional[int] = None,          # Фильтр по возрасту
    sex: Optional[str] = None,          # Фильтр по полу
) -> list[StudentRecord]:
    
    table = _get_table(table_name)
    if sex is not None:
        sex = sex.lower()

    if (
        student_id is None
        and first_name is None
        and second_name is None
        and age is None
        and sex is None
    ):
        return table.copy()
    result: list[StudentRecord] = []

    for record in table:
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

def update_record(table_name: str, student_id: int, **kwargs) -> StudentRecord | None:
    
    table = _get_table(table_name)
    for i, record in enumerate(table):
        if record[0] == student_id:
            updated = list(record)

            if "first_name" in kwargs:
                updated[1] = kwargs["first_name"]
                
            if "second_name" in kwargs:
                updated[2] = kwargs["second_name"]

            if "age" in kwargs:
                age = kwargs["age"]
                if age < 0:
                    raise ValueError("Возраст не может быть меньше нуля")
                updated[3] = age

            if "sex" in kwargs:
                sex = kwargs["sex"].lower()
                if sex not in ["м", "ж"]:
                    raise ValueError("Пол должен быть только 'ж' или 'м'")
                updated[4] = sex
        
            table[i] = tuple(updated)
            return table[i]
    
    return None

def delete_record(table_name: str, student_id: int) -> bool:
    
    table = _get_table(table_name)
    for i, record in enumerate(table):
        if record[0] == student_id:
            del table[i]
            return True
    return False