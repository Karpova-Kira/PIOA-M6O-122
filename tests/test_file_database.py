import unittest
import shutil
import json
from pathlib import Path
from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableAlreadyExistsError, InvalidStorageDataError

class TestFileDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = "test_data_json"
        self.db = FileDatabase(self.test_dir)

    def tearDown(self) -> None:
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_create_table(self) -> None:
        """Тест успешного создания таблицы."""
        self.db.create_table("students", {"id": "int", "name": "str"})
        self.assertIn("students", self.db.list_tables())
        self.assertTrue((Path(self.test_dir) / "students.json").exists())

    def test_create_table_already_exists(self) -> None:
        """Тест уникальности имени таблицы."""
        self.db.create_table("students", {"id": "int", "name": "str"})
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", {"id": "int", "name": "str"})

    def test_insert_and_select_record(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str"})
        self.db.insert_record("students", {"id": 1, "name": "Ivan"})
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Ivan")

    def test_delete_nonexistent_record(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str"})
        deleted = self.db.delete_record("students", "id", 999)
        self.assertFalse(deleted)

    def test_data_persists_between_instances(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str"})
        self.db.insert_record("students", {"id": 1, "name": "Ivan"})
        
        db2 = FileDatabase(self.test_dir)
        records = db2.select_records("students")
        self.assertEqual(records[0]["id"], 1)

    def test_corrupted_json_file(self) -> None:
        """Проверяет реакцию СУБД на поврежденный файл конфигурации/JSON."""
        self.db.create_table("students", {"id": "int", "name": "str"})
        file_path = Path(self.test_dir) / "students.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("{invalid json...")
            
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("students")

    def test_update_record_validation(self) -> None:
        self.db.create_table("students", {"id": "int", "age": "int"})
        self.db.insert_record("students", {"id": 1, "age": 20})
        with self.assertRaises(TypeError):
            self.db.update_record("students", "id", 1, age="строка")