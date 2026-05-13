import unittest
from src.db.backend.memory import StudentTable, create_table, list_tables, _get_table, TABLES, create_record, select_record, update_record, delete_record
from src.db.backend.errors import InvalidAgeError, DuplicateIDError

class TestMemory(unittest.TestCase):

    def setUp(self):
        self.student_table = StudentTable()
        self.assertIsInstance(self.student_table, StudentTable)

        global TABLES
        TABLES.clear()

    def test_create_record(self):
        cases = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
            (11, "Jack", "Thomas", 18, "M"),
            (12, "Kathy", "Jackson", 23, "F"),
            ]

        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.student_table.create_record(*test_data)
                self.assertEqual(record, test_data)

    def test_create_record_negative_age(self):
        cases = [
            (1, "John", "Doe", -1, "M"),
            (2, "Jane", "Smith", -5, "F"),
            (3, "Alice", "Johnson", -10, "F"),
        ]
        error_message = "Поле age не может быть отрицательным."

        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(InvalidAgeError) as context:
                    self.student_table.create_record(*test_data)

        self.assertEqual(str(context.exception), error_message)

    def test_create_record_duplicate_id(self):
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        error_message = "Запись с id=1 уже существует."

        self.student_table.create_record(*test_data_1)

        with self.assertRaises(DuplicateIDError) as context:
            self.student_table.create_record(*test_data_2)

        self.assertEqual(str(context.exception), error_message)

    def test_select_record(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        cases = [
            {
                "name": "Выбор без фильтров",
                "filters": {},
                "expected": test_datas,
            },
            {
                "name": "Фильтр по ID",
                "filters": {"student_id": 1},
                "expected": [test_datas[0]],
            },
            {
                "name": "Фильтр по имени",
                "filters": {"first_name": "Jane"},
                "expected": [test_datas[1]],
            },
            {
                "name": "Фильтр по фамилии",
                "filters": {"second_name": "Johnson"},
                "expected": [test_datas[2]],
            },
            {
                "name": "Фильтр по возрасту",
                "filters": {"age": 20},
                "expected": [test_datas[0], test_datas[6]],
            },
            {
                "name": "Фильтр по полу",
                "filters": {"sex": "F"},
                "expected": [
                    test_datas[1],
                    test_datas[2],
                    test_datas[5],
                    test_datas[7],
                    test_datas[9],
                ],
            },
        ]

        for case in cases:
            with self.subTest(
                case=case["name"], filters=case["filters"], expected=case["expected"]
            ):
                records = self.student_table.select_record(**case["filters"])
                self.assertEqual(records, case["expected"])

    def test_create_table(self):
        table_name = "test_table"
        create_table(table_name)
        self.assertIn(table_name, list_tables())
    
    def test_create_table_duplicate(self):
        table_name = "test_table"
        create_table(table_name)
        
        with self.assertRaises(ValueError) as context:
            create_table(table_name)
        self.assertIn("уже существует", str(context.exception))
    
    def test_list_tables(self):
        self.assertEqual(list_tables(), [])
        create_table("table1")
        create_table("table2")
        tables = list_tables()
        self.assertIn("table1", tables)
        self.assertIn("table2", tables)
        self.assertEqual(len(tables), 2)
    
    def test_update_record(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        updated = self.student_table.update_record(1, first_name="Jonathan", age=21)
        self.assertEqual(updated[1], "Jonathan")
        self.assertEqual(updated[3], 21)
        
        record = self.student_table.select_record(student_id=1)[0]
        self.assertEqual(record[1], "Jonathan")
        self.assertEqual(record[3], 21)
    
    def test_update_record_not_found(self):
        result = self.student_table.update_record(999, first_name="Test")
        self.assertIsNone(result)
    
    def test_update_record_negative_age(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        with self.assertRaises(ValueError) as context:
            self.student_table.update_record(1, age=-5)
        self.assertIn("не может быть меньше нуля", str(context.exception))
    
    def test_update_record_invalid_sex(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        with self.assertRaises(ValueError) as context:
            self.student_table.update_record(1, sex="X")
        self.assertIn("Пол должен быть", str(context.exception))
    
    def test_delete_record(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        
        result = self.student_table.delete_record(1)
        self.assertTrue(result)
        
        records = self.student_table.select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 2)
    
    def test_delete_record_not_found(self):
        result = self.student_table.delete_record(999)
        self.assertFalse(result)
    
    def test_multiple_tables_independent(self):
        create_table("table1")
        create_table("table2")
        
        table1 = StudentTable()
        table2 = StudentTable()
        
        record1 = table1.create_record(1, "John", "Doe", 20, "M")
        record2 = table2.create_record(1, "Jane", "Smith", 22, "F")
        
        self.assertEqual(record1[1], "John")
        self.assertEqual(record2[1], "Jane")
        
        self.assertEqual(len(table1.select_record()), 1)
        self.assertEqual(len(table2.select_record()), 1)

    def test_get_table_exists(self):
        """Тест _get_table с существующей таблицей"""
        create_table("TestTable")
        table = _get_table("TestTable")
        self.assertIsNotNone(table)
        self.assertEqual(type(table), list)

    def test_get_table_not_exists(self):
        """Тест _get_table с несуществующей таблицей"""
        with self.assertRaises(ValueError) as context:
            _get_table("NonExistent")
        self.assertIn("не существует", str(context.exception))

    def test_update_record_with_sex(self):

        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(1, sex="F")
        
        self.assertEqual(updated[4], "F")
        record = self.student_table.select_record(student_id=1)[0]
        self.assertEqual(record[4], "F")

    def test_update_record_multiple_fields(self):
        
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        updated = self.student_table.update_record(
            1, 
            first_name="Jonathan", 
            second_name="Smith", 
            age=25, 
            sex="F"
        )
        
        self.assertEqual(updated[1], "Jonathan")
        self.assertEqual(updated[2], "Smith")
        self.assertEqual(updated[3], 25)
        self.assertEqual(updated[4], "F")

    def test_update_record_only_second_name(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(1, second_name="Smith")
        
        self.assertEqual(updated[1], "John")
        self.assertEqual(updated[2], "Smith")
        self.assertEqual(updated[3], 20)
        self.assertEqual(updated[4], "M")

    def test_delete_multiple_records_sequentially(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.student_table.create_record(3, "Bob", "Brown", 21, "M")
        
        self.assertTrue(self.student_table.delete_record(2))
        self.assertTrue(self.student_table.delete_record(1))
        
        records = self.student_table.select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 3)

    def test_delete_record_empty_table(self):
        result = self.student_table.delete_record(1)
        self.assertFalse(result)

    def test_select_record_multiple_filters(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "John", "Smith", 20, "M")
        self.student_table.create_record(3, "Jane", "Doe", 22, "F")
        
        results = self.student_table.select_record(first_name="John", second_name="Doe")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 1)
        
        results = self.student_table.select_record(first_name="John", age=20)
        self.assertEqual(len(results), 2)

    def test_select_record_with_none_filters(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        results = self.student_table.select_record(first_name=None)
        self.assertEqual(len(results), 1)

    def test_create_record_sex_normalization_m(self):
        record1 = self.student_table.create_record(1, "John", "Doe", 20, "M")
        record2 = self.student_table.create_record(2, "John", "Doe", 20, "m")
        record3 = self.student_table.create_record(3, "John", "Doe", 20, "м")
        
        self.assertEqual(record1[4], "M")
        self.assertEqual(record2[4], "m")
        self.assertEqual(record3[4], "м")

    def test_create_record_invalid_sex(self):

        """Тест создания записи с некорректным полом"""
        record = self.student_table.create_record(1, "John", "Doe", 20, "X")
        self.assertEqual(record[4], "X")

    def test_create_record_missing_table(self):
        with self.assertRaises(ValueError) as context:
            create_record("NonExistent", 1, "John", "Doe", 20, "M")
        self.assertIn("не существует", str(context.exception))

    def test_select_record_missing_table(self):
        with self.assertRaises(ValueError) as context:
            select_record("NonExistent")
        self.assertIn("не существует", str(context.exception))

    def test_update_record_missing_table(self):
        with self.assertRaises(ValueError) as context:
            update_record("NonExistent", 1, first_name="John")
        self.assertIn("не существует", str(context.exception))

    def test_delete_record_missing_table(self):
        with self.assertRaises(ValueError) as context:
            delete_record("NonExistent", 1)
        self.assertIn("не существует", str(context.exception))

    def test_update_record_no_changes(self):
        create_table("TestTable")
        create_record("TestTable", 1, "John", "Doe", 20, "M")
        result = update_record("TestTable", 1)
        self.assertIsNotNone(result) 

    def test_free_create_record_negative_age(self):
        create_table("TestTable")
        with self.assertRaises(ValueError) as context:
            create_record("TestTable", 1, "John", "Doe", -5, "M")
        self.assertIn("отрицательным", str(context.exception))

    def test_free_create_record_duplicate_id(self):
        create_table("TestTable")
        create_record("TestTable", 1, "John", "Doe", 20, "M")
        with self.assertRaises(ValueError) as context:
            create_record("TestTable", 1, "Jane", "Smith", 22, "F")
        self.assertIn("уже существует", str(context.exception))

    def test_free_update_record_negative_age(self):
        create_table("TestTable")
        create_record("TestTable", 1, "John", "Doe", 20, "M")
        with self.assertRaises(ValueError) as context:
            update_record("TestTable", 1, age=-5)
        self.assertIn("не может быть меньше нуля", str(context.exception))

    def test_free_delete_record_success(self):
        create_table("TestTable")
        create_record("TestTable", 1, "John", "Doe", 20, "M")
        create_record("TestTable", 2, "Jane", "Smith", 22, "F")
        
        result = delete_record("TestTable", 1)
        self.assertTrue(result)
        
        records = select_record("TestTable")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 2)

    def test_free_delete_record_not_found(self):
        create_table("TestTable")
        result = delete_record("TestTable", 999)
        self.assertFalse(result)

    def test_free_select_record_with_sex_filter(self):
        create_table("TestTable")
        create_record("TestTable", 1, "John", "Doe", 20, "M")
        create_record("TestTable", 2, "Jane", "Smith", 22, "F")
        
        results = select_record("TestTable", sex="F")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Jane")


if __name__ == "__main__":
    unittest.main()    
