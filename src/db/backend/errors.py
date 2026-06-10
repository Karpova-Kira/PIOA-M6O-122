class DatabaseError(Exception):

    """Базовый класс для ошибок, связанных с таблицей Student."""
    pass

class TableNotFoundError(DatabaseError):
    """Таблица не найдена."""
    pass

class TableAlreadyExistsError(DatabaseError):
    """Таблица с таким именем уже существует."""
    pass

class UnknownColumnError(DatabaseError):
    """Попытка использовать несуществующую колонку."""
    pass

class MissingColumnError(DatabaseError):
    """В записи отсутствуют обязательные для таблицы колонки."""
    pass

class DuplicateIDError(DatabaseError):
    """Ошибка, возникающая при попытке создать запись с уже существующим идентификатором."""
    pass