import tempfile
import unittest
from pathlib import Path

from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError, InvalidStorageDataError


class TestFileDatabase(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = FileDatabase(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_create_table(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.assertTrue(self.db._table_exists("students"))
    
    def test_create_table_already_exists(self):
        self.db.create_table("students", ("id", "name"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", ("id", "name"))
    
    def test_insert_and_select_record(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
    
    def test_data_persists_between_instances(self):
        db1 = FileDatabase(self.temp_dir.name)
        db1.create_table("students", ("id", "name"))
        db1.insert_record("students", {"id": 1, "name": "John"})
        
        db2 = FileDatabase(self.temp_dir.name)
        records = db2.select_records("students")
        
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
    
    def test_select_with_filters(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Jane", "age": 22})
        
        records = self.db.select_records("students", name="Jane")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 2)
    
    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")
    
    def test_update_record(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        
        updated = self.db.update_record("students","id", 1, name="Jonathan", age=21)
        
        self.assertEqual(updated["name"], "Jonathan")
        self.assertEqual(updated["age"], 21)
        
        records = self.db.select_records("students", id=1)
        self.assertEqual(records[0]["name"], "Jonathan")
    
    def test_delete_record(self):
        self.db.create_table("students", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "John"})
        self.db.insert_record("students", {"id": 2, "name": "Jane"})
        
        result = self.db.delete_record("students","id", 1)
        self.assertTrue(result)
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Jane")
    
    def test_delete_nonexistent_record(self):
        self.db.create_table("students", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "John"})
        
        result = self.db.delete_record("students", "id", 999)
        self.assertFalse(result)
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)


    def test_corrupted_json_file(self):
        self.db.create_table("students", ("id", "name"))
        json_path = Path(self.temp_dir.name) / "students.json"
        
        json_path.write_text("[1, 2, 3]", encoding="utf-8")
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("students")
            
        json_path.write_text("{broken json", encoding="utf-8")
        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records("students")


if __name__ == "__main__":
    unittest.main()