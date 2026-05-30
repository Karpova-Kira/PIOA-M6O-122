import tempfile
import unittest
from pathlib import Path

from src.db.backend.csv_file import CSVFileDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError, InvalidStorageDataError


class TestCSVFileDatabase(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = CSVFileDatabase(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_create_table(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.assertTrue(self.db._table_exists("students"))
        
        csv_path = Path(self.temp_dir.name) / "students.csv"
        self.assertTrue(csv_path.exists())
    
    def test_create_table_already_exists(self):
        self.db.create_table("students", ("id", "name"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", ("id", "name"))
    
    def test_data_persists_between_instances(self):
        db1 = CSVFileDatabase(self.temp_dir.name)
        db1.create_table("students", ("id", "name"))
        db1.insert_record("students", {"id": 1, "name": "John"})
        
        db2 = CSVFileDatabase(self.temp_dir.name)
        records = db2.select_records("students")
        
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
    
    def test_insert_and_select(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
        self.assertEqual(records[0]["age"], 20)
    
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
        
        updated = self.db.update_record("students", 1, name="Jonathan", age=21)
        self.assertEqual(updated["name"], "Jonathan")
        self.assertEqual(updated["age"], 21)
        
        records = self.db.select_records("students", id=1)
        self.assertEqual(records[0]["name"], "Jonathan")
    
    def test_delete_record(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Jane", "age": 22})
        
        result = self.db.delete_record("students", 1)
        self.assertTrue(result)
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Jane")
    
    def test_delete_nonexistent_record(self):
        self.db.create_table("students", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "John"})
        
        result = self.db.delete_record("students", 999)
        self.assertFalse(result)
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
    
    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")
    
    def test_csv_content_format(self):
        self.db.create_table("students", ("id", "name", "age"))
        self.db.insert_record("students", {"id": 1, "name": "John", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Jane", "age": 22})
        
        content = self.db.get_csv_content("students")
        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]
        
        self.assertGreaterEqual(len(lines), 1)
        
        self.assertIn("id", lines[0])
        self.assertIn("name", lines[0])
        self.assertIn("age", lines[0])
        
        all_content = " ".join(lines)
        self.assertIn("John", all_content)
        self.assertIn("Jane", all_content)
    
    def test_empty_csv_file(self):
        self.db.create_table("students", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "John"})
        
        csv_path = Path(self.temp_dir.name) / "students.csv"
        csv_path.write_text("", encoding="utf-8")
        
        new_db = CSVFileDatabase(self.temp_dir.name)
        with self.assertRaises(InvalidStorageDataError):
            new_db.select_records("students")


if __name__ == "__main__":
    unittest.main()