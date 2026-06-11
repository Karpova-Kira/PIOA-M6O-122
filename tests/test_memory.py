import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableAlreadyExistsError

class TestMemoryDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.db = MemoryDatabase()

    def test_create_table(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str"})
        self.assertIn("students", self.db.list_tables())

    def test_create_table_already_exists(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str"})
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", {"id": "int", "name": "str"})

    def test_insert_and_select(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str", "age": "int"})
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["age"], 20)

    def test_select_with_filters(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str", "age": "int"})
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Anna", "age": 22})
        res = self.db.select_records("students", age=22)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], 2)

    def test_update_record(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str", "age": "int"})
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        updated = self.db.update_record("students", "id", 1, age=25)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["age"], 25)

    def test_delete_record(self) -> None:
        self.db.create_table("students", {"id": "int", "name": "str", "age": "int"})
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        deleted = self.db.delete_record("students", "id", 1)
        self.assertTrue(deleted)
        self.assertEqual(len(self.db.select_records("students")), 0)