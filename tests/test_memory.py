import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError

class TestMemory(unittest.TestCase):

    def setUp(self):
        # Создаём новую таблицу с уникальным именем для каждого теста
        import uuid
        self.table_name = f"TestTable_{uuid.uuid4().hex[:8]}"
        self.table = StudentTable.create_table(self.table_name)
    
    def tearDown(self):
        # Удаляем таблицу после теста (через внутренний словарь)
        import uuid
        from src.db.backend.memory import StudentTable as ST
        if self.table_name in ST._tables:
            del ST._tables[self.table_name]
            if self.table_name in ST._id_counters:
                del ST._id_counters[self.table_name]
    
    def test_create_record(self):
        record = self.table.create_record(1, "John", "Doe", 20, "M")
        self.assertEqual(record[0], 1)
        self.assertEqual(record[1], "John")
        self.assertEqual(record[2], "Doe")
        self.assertEqual(record[3], 20)
        self.assertEqual(record[4], "M")
    
    def test_create_record_negative_age(self):
        with self.assertRaises(InvalidAgeError):
            self.table.create_record(1, "John", "Doe", -5, "M")
    
    def test_create_record_duplicate_id(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with self.assertRaises(DuplicateIDError):
            self.table.create_record(1, "Jane", "Smith", 22, "F")
    
    def test_create_record_invalid_sex(self):
        with self.assertRaises(ValueError):
            self.table.create_record(1, "John", "Doe", 20, "X")
    
    def test_select_record_all(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        records = self.table.select_record()
        self.assertEqual(len(records), 2)
    
    def test_select_record_by_id(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        records = self.table.select_record(student_id=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "John")
    
    def test_select_record_by_sex(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        records = self.table.select_record(sex="F")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Jane")
    
    def test_update_record(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        updated = self.table.update_record(1, first_name="Jonathan", age=21)
        self.assertEqual(updated[1], "Jonathan")
        self.assertEqual(updated[3], 21)
    
    def test_update_record_not_found(self):
        result = self.table.update_record(999, first_name="Test")
        self.assertIsNone(result)
    
    def test_delete_record(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        result = self.table.delete_record(1)
        self.assertTrue(result)
        records = self.table.select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Jane")
    
    def test_delete_record_not_found(self):
        result = self.table.delete_record(999)
        self.assertFalse(result)
    
    def test_get_all(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        records = self.table.get_all()
        self.assertEqual(len(records), 2)
    
    def test_create_table_duplicate(self):
        with self.assertRaises(ValueError):
            StudentTable.create_table(self.table_name)
    
    def test_list_tables(self):
        tables = StudentTable.list_tables()
        self.assertIn(self.table_name, tables)

if __name__ == "__main__":
    unittest.main()    
