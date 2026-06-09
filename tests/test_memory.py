import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError


class TestMemoryDatabase(unittest.TestCase):
    
    def setUp(self):
        self.db = MemoryDatabase()
    
    def test_create_table(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.assertTrue(self.db._table_exists("students"))
        self.assertIn("students", self.db.list_tables())
    
    def test_create_table_already_exists(self):
        self.db.create_table("students", ("id", "name"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", ("id", "name"))
    
    def test_access_nonexistent_table_raises_error(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("ghost_table")
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("ghost_table", {"id": 1})

    def test_insert_and_select(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
    
    def test_select_with_filters(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Jane", "age": 22})
        
        records = self.db.select_records("students", name="Jane")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 2)
    
    def test_update_record(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        
        updated = self.db.update_record("students","id", 1, name="Jonathan")
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Jonathan")
    
    def test_delete_record(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        
        result = self.db.delete_record("students","id", 1)
        self.assertTrue(result)
        self.assertEqual(len(self.db.select_records("students")), 0)


if __name__ == "__main__":
    unittest.main()