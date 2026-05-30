class StudentTableError(Exception):
    """Базовый класс для ошибок, связанных с таблицей Student."""
    pass


class InvalidAgeError(StudentTableError):
    """Ошибка, возникающая при попытке создать запись с некорректным возрастом."""
    pass


class DuplicateIDError(StudentTableError):
    """Ошибка, возникающая при попытке создать запись с уже существующим идентификатором."""
    pass


class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных."""
    pass


class TableAlreadyExistsError(DatabaseError):
    """Ошибка, возникающая при попытке создать уже существующую таблицу."""
    pass


class TableNotFoundError(DatabaseError):
    """Ошибка, возникающая при обращении к несуществующей таблице."""
    pass


class MissingColumnError(DatabaseError):
    """Ошибка, возникающая при отсутствии обязательного поля в записи."""
    pass


class UnknownColumnError(DatabaseError):
    """Ошибка, возникающая при использовании поля, которого нет в схеме таблицы."""
    pass


class InvalidStorageDataError(DatabaseError):
    """Ошибка, возникающая при чтении повреждённых данных из файла."""
    pass