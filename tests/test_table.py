import unittest
from src.db.backend.table import Table
from src.db.backend.errors import MissingColumnError, UnknownColumnError


class TestTable(unittest.TestCase):
    
    def test_insert_record_valid(self):
        table = Table(("id", "name", "age"))
        table.insert_record({"id": 1, "name": "John", "age": 20})
        self.assertEqual(len(table.records), 1)
    
    def test_insert_record_missing_column(self):
        table = Table(("id", "name", "age"))
        with self.assertRaises(MissingColumnError):
            table.insert_record({"id": 1, "name": "John"})
    
    def test_select_records_with_filter(self):
        table = Table(("id", "name", "age"))
        table.insert_record({"id": 1, "name": "John", "age": 20})
        table.insert_record({"id": 2, "name": "Jane", "age": 22})
        
        records = table.select_records(name="Jane")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 2)
    
    def test_update_record(self):
        table = Table(("id", "name", "age"))
        table.insert_record({"id": 1, "name": "John", "age": 20})
        
        updated = table.update_record("id", 1, name="Jonathan", age=21)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Jonathan")
        self.assertEqual(updated["age"], 21)

    def test_update_record_unknown_fields(self):
        table = Table(("id", "name"))
        table.insert_record({"id": 1, "name": "John"})
        with self.assertRaises(UnknownColumnError):
            table.update_record("id", 1, unknown_field="test")
        with self.assertRaises(UnknownColumnError):
            table.update_record("wrong_key", 1, name="Test")
    
    def test_delete_record(self):
        table = Table(("id", "name", "age"))
        table.insert_record({"id": 1, "name": "John", "age": 20})
        table.insert_record({"id": 2, "name": "Jane", "age": 22})
        
        result = table.delete_record("id", 1)
        self.assertTrue(result)
        self.assertEqual(len(table.records), 1)
        self.assertEqual(table.records[0]["id"], 2)


if __name__ == "__main__":
    unittest.main()