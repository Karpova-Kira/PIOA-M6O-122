import unittest
from src.db.backend.table import Table
from src.db.backend.errors import MissingColumnError, UnknownColumnError, DuplicateIDError


class TestTable(unittest.TestCase):

    def setUp(self) -> None:
        self.columns = {"id": "int", "name": "str", "age": "int"}
        self.table = Table("students", self.columns)

    def test_insert_record_valid(self):
        record = {"id": 1, "name": "Ivan", "age": 20}
        self.table.insert_record(record)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0]["name"], "Ivan")
        self.assertEqual(self.table.records[0]["age"], 20)

    def test_insert_record_duplicate_id(self):
        table = Table(self.student_schema)
        table.insert_record({"id": 1, "name": "John", "age": 20})
        with self.assertRaises(DuplicateIDError):
            table.insert_record({"id": 1, "name": "Jane", "age": 22})
    
    def test_insert_record_duplicate_id(self) -> None:
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        with self.assertRaises(DuplicateIDError):
            self.table.insert_record({"id": 1, "name": "Petr", "age": 22})
    
    def test_insert_record_missing_column(self) -> None:
        with self.assertRaises(MissingColumnError):
            self.table.insert_record({"id": 2, "name": "Anna"})

    def test_select_records_with_filter(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        self.table.insert_record({"id": 2, "name": "Anna", "age": 22})
        
        results = self.table.select_records(age=22)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Anna")
    
    def test_update_record(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        
        updated = self.table.update_record("id", 1, age=21)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["age"], 21)
        self.assertEqual(self.table.records[0]["age"], 21)

    def test_delete_record(self) -> None:
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        self.assertEqual(len(self.table.records), 1)
        
        deleted = self.table.delete_record("id", 1)
        self.assertTrue(deleted)
        self.assertEqual(len(self.table.records), 0)


if __name__ == "__main__":
    unittest.main()