
from .errors import DuplicateIDError, InvalidAgeError 
from typing import Optional

type StudentRecord = tuple[int, str, str, int, str]



class StudentTable:

    _tables: dict[str, list[StudentRecord]] = {}
    _id_counters: dict[str, int] = {}

    def __init__(self, table_name) -> None:
        self.table_name = table_name
        if table_name not in StudentTable._tables:
            StudentTable._tables[table_name] = []
            StudentTable._id_counters[table_name] = 1
        self._student = StudentTable._tables[table_name]
        self._id_counter = StudentTable._id_counters[table_name]

    @classmethod
    def create_table(cls, table_name: str) -> 'StudentTable':
        if table_name in cls._tables:
            raise ValueError(f"Таблица '{table_name}' уже существует.")
        return cls(table_name)

    @classmethod
    def list_tables(cls) -> list[str]:
        return list(cls._tables.keys())


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

        sex_upper = sex.upper()
        if sex_upper not in ["M", "F"]:
            raise ValueError("Пол должен быть 'M' или 'F'")


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
 
        if sex is not None:
            sex = sex.upper()

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
    

    def get_all(self) -> list[StudentRecord]:
        return self._student.copy()

    
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
    
    
