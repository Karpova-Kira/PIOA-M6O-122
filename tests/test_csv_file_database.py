import unittest
import shutil
from pathlib import Path
from src.db.backend.csv_file import CSVFileDatabase
from src.db.backend.errors import TableAlreadyExistsError

class TestCSVFileDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = "test_data_csv"
        self.db = CSVFileDatabase(self.test_dir)
        self.db.create_table("students", {"id": "int", "name": "str", "age": "int"})

    def tearDown(self) -> None:
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_create_table(self) -> None:
        table_name = "courses"
        schema = {"course_id": "int", "title": "str"}
        
        self.db.create_table(table_name, schema)
        self.assertIn(table_name, self.db.list_tables())
        
        table_file = Path(self.test_dir) / f"{table_name}.csv"
        self.assertTrue(table_file.exists())

    def test_create_table_already_exists(self) -> None:
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", {"id": "int", "name": "str", "age": "int"})

    def test_insert_and_select(self) -> None:
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        records = self.db.select_records("students")
        self.assertEqual(records[0]["age"], 20)
        self.assertIsInstance(records[0]["age"], int)

    def test_negative_numbers_parsing(self) -> None:
        self.db.create_table("balance", {"account": "int", "amount": "int"})
        self.db.insert_record("balance", {"account": 1, "amount": -100})
        
        db2 = CSVFileDatabase(self.test_dir)
        records = db2.select_records("balance")
        self.assertEqual(records[0]["amount"], -100)

    def test_data_persists_between_instances(self) -> None:
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        
        db2 = CSVFileDatabase(self.test_dir)
        records = db2.select_records("students")
        self.assertEqual(records[0]["id"], 1)

    def test_select_with_filters(self) -> None:
        self.db.insert_record("students", {"id": 2, "name": "Anna", "age": 22})
        res = self.db.select_records("students", id=2)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], 2)

    def test_update_record(self) -> None:
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        updated = self.db.update_record("students", "id", 1, age=25)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["age"], 25)

    def test_delete_record(self) -> None:
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        deleted = self.db.delete_record("students", "id", 1)
        self.assertTrue(deleted)
        self.assertEqual(len(self.db.select_records("students")), 0)

    def test_update_record_validation(self) -> None:
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        with self.assertRaises(TypeError):
            self.db.update_record("students", "id", 1, age="не_число")

    def test_select_all_records_with_empty_filters(self) -> None:
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Anna", "age": 22})
        
        all_records = self.db.select_records("students")
        self.assertEqual(len(all_records), 2)

    def test_clear_database_cache(self) -> None:
        self.assertIn("students", self.db.list_tables())
        table_file = self.db._get_table_path("students")
        if table_file.exists():
            table_file.unlink()
            
        self.db._tables.clear()
        self.assertNotIn("students", self.db.list_tables())

    def test_list_tables_empty_directory(self) -> None:
        empty_db = CSVFileDatabase("test_data_csv_empty")
        self.assertEqual(empty_db.list_tables(), [])
        
        import shutil
        from pathlib import Path
        if Path("test_data_csv_empty").exists():
            shutil.rmtree("test_data_csv_empty")

    def test_get_csv_content_success_and_failure(self) -> None:
        from src.db.backend.errors import TableNotFoundError

        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        content = self.db.get_csv_content("students")
        
        self.assertIn("id,name,age", content)
        self.assertIn("int,str,int", content)
        self.assertIn("1,Ivan,20", content)

        with self.assertRaises(TableNotFoundError):
            self.db.get_csv_content("non_existent_table_abc")

    def test_load_table_non_existent_raises_error(self) -> None:
        """Проверяет, что внутренний метод _load_table честно кидает ошибку, если файла нет."""
        from src.db.backend.errors import TableNotFoundError
        
        self.db._tables.clear()
        
        with self.assertRaises(TableNotFoundError):
            self.db._load_table("ghost_table")

if __name__ == "__main__":
    unittest.main()