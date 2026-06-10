import unittest
from src.db.backend.memory import MemoryDatabase, Table
from src.db.backend.errors import TableAlreadyExistsError, TableNotFoundError
class TestMemory(unittest.TestCase):

    def setUp(self):
        self.db = MemoryDatabase()
        self.table_name = "test_table"
        self.columns = ["id", "name", "age", "sex"]
        self.table = self.db.create_table(self.table_name, self.columns)
    
    def test_create_record(self):
        record = self.table.create_record({"id": 1, "name": "John", "age": 20, "sex": "M"})
        self.assertEqual(record["id"], 1)
        self.assertEqual(record["name"], "John")
        self.assertEqual(record["age"], 20)
        self.assertEqual(record["sex"], "M")

    def test_create_record_auto_id(self):
        record1 = self.table.create_record({"id": 1, "name": "Alice", "age": 20, "sex": "F"})
        record2 = self.table.create_record({"id": 2, "name": "Bob", "age": 22, "sex": "M"})
        
        self.assertEqual(record1["id"], 1)
        self.assertEqual(record2["id"], 2)

    def test_select_record_by_filter(self):
        self.table.create_record({"id": 1, "name": "John", "age": 20, "sex": "M"})
        self.table.create_record({"id": 2, "name": "Jane", "age": 22, "sex": "F"})
        
        records = self.table.select_record({"sex": "F"})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Jane")
    def test_update_record(self):
        rec = self.table.create_record({"id": 1, "name": "John", "age": 20, "sex": "M"})
        rec_id = rec["id"]
        
        updated = self.table.update_record(rec_id, {"name": "Jonathan", "age": 21})
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Jonathan")
        self.assertEqual(updated["age"], 21)


    def test_update_record_not_found(self):
        result = self.table.update_record(999, {"name": "Test"})
        self.assertIsNone(result)

    def test_delete_record(self):
        rec = self.table.create_record({"id": 1, "name": "John", "age": 20, "sex": "M"})
        rec_id = rec["id"]
        
        result = self.table.delete_record(rec_id)
        self.assertTrue(result)
        self.assertEqual(len(self.table.get_all()), 0)

    def test_delete_record_not_found(self):
        result = self.table.delete_record(999)
        self.assertFalse(result)

    def test_create_table_duplicate(self):
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table(self.table_name, ["id", "col"])

    def test_list_tables(self):
        tables = self.db.list_tables()
        self.assertIn(self.table_name, tables)

    def test_get_table_success(self):
        fetched_table = self.db.get_table(self.table_name)
        self.assertEqual(fetched_table, self.table)

    def test_get_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_table("non_existent_table")

    def test_create_record_empty_dict_error(self):
        from src.db.backend.errors import MissingColumnError
        with self.assertRaises(MissingColumnError):
            self.table.create_record({})

if __name__ == "__main__":
    unittest.main()