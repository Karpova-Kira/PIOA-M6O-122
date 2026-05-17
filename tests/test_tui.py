import unittest
from unittest.mock import patch
from io import StringIO
from src.db.tui import Student_tui
from src.db.backend.memory import TABLES, create_table, create_record, select_record


class TestTUIAdvanced(unittest.TestCase):

    def setUp(self):
        TABLES.clear()
        self.app = Student_tui()
        
    @patch('builtins.input')
    def test_read_int_valid(self, mock_input):
        mock_input.return_value = "42"
        result = self.app._read_int("Введите число: ")
        self.assertEqual(result, 42)
    
    @patch('builtins.input')
    def test_read_int_invalid_then_valid(self, mock_input):
        mock_input.side_effect = ["abc", "25"]
        result = self.app._read_int("Введите число: ")
        self.assertEqual(result, 25)
    
    @patch('builtins.input')
    def test_read_optional_int_empty(self, mock_input):
        mock_input.return_value = ""
        result = self.app._read_optional_int("Введите возраст: ")
        self.assertIsNone(result)
    
    @patch('builtins.input')
    def test_read_optional_int_valid(self, mock_input):
        mock_input.return_value = "30"
        result = self.app._read_optional_int("Введите возраст: ")
        self.assertEqual(result, 30)
    
    @patch('builtins.input')
    def test_read_optional_int_invalid_then_valid(self, mock_input):
        mock_input.side_effect = ["abc", "18"]
        result = self.app._read_optional_int("Введите возраст: ")
        self.assertEqual(result, 18)
        
    def test_print_records_empty_captures_output(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._print_records([])
            self.assertIn("Записи не найдены", mock_stdout.getvalue())
    
    def test_print_records_non_empty_captures_output(self):
        records = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._print_records(records)
            output = mock_stdout.getvalue()
            self.assertIn("John", output)
            self.assertIn("Jane", output)
            self.assertIn("Doe", output)
    
    def test_print_menu_contains_menu_items(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._print_menu()
            output = mock_stdout.getvalue()
            self.assertIn("=== База студентов ===", output)
            self.assertIn("1. Создать таблицу", output)
            self.assertIn("2. Выбрать/сменить таблицу", output)
            self.assertIn("3. Добавить запись", output)
            self.assertIn("0. Выход", output)
    
    
    def test_current_table_initially_none(self):
        new_app = Student_tui()
        self.assertIsNone(new_app.current_table)
    
    @patch('builtins.input')
    def test_current_table_changes_after_create(self, mock_input):
        mock_input.return_value = "TestTable"
        self.app._create_table()
        self.assertEqual(self.app.current_table, "TestTable")
    
    @patch('builtins.input')
    def test_select_table_changes_current_table(self, mock_input):
        create_table("Table1")
        create_table("Table2")
        
        mock_input.return_value = "2"
        self.app._select_table()
        
        self.assertEqual(self.app.current_table, "Table2")
    
    @patch('builtins.input')
    def test_create_table_does_not_overwrite_existing(self, mock_input):
        create_table("Existing")
        mock_input.return_value = "Existing"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._create_table()
            self.assertIn("уже существует", mock_stdout.getvalue())
    
    
    @patch('builtins.input')
    def test_add_student_with_valid_data(self, mock_input):
        create_table("Students")
        self.app.current_table = "Students"
        
        mock_input.side_effect = ["1", "John", "Doe", "20", "M"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._add_student()
            self.assertIn("Запись добавлена", mock_stdout.getvalue())
        
        records = select_record("Students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "John")
    
    @patch('builtins.input')
    def test_add_student_negative_age_error(self, mock_input):
        create_table("Students")
        self.app.current_table = "Students"
        
        mock_input.side_effect = ["1", "John", "Doe", "-5", "M"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._add_student()
            output = mock_stdout.getvalue()
            self.assertIn("Ошибка", output)
            self.assertIn("отрицательным", output)
    
    @patch('builtins.input')
    def test_update_student_success(self, mock_input):
        create_table("Students")
        self.app.current_table = "Students"
        
        create_record("Students", 1, "John", "Doe", 20, "M")
        mock_input.side_effect = ["1", "", "Smith", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._update_student()
            output = mock_stdout.getvalue()
            self.assertIn("Запись обновлена", output)
        
        record = select_record("Students", student_id=1)[0]
        self.assertEqual(record[2], "Smith")
    
    @patch('builtins.input')
    def test_delete_student_with_confirmation(self, mock_input):
        create_table("Students")
        self.app.current_table = "Students"
        
        create_record("Students", 1, "John", "Doe", 20, "M")
        create_record("Students", 2, "Jane", "Smith", 22, "F")
        
        mock_input.side_effect = ["1", "y"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._delete_student()
            output = mock_stdout.getvalue()
            self.assertIn("успешно удалена", output)
        
        records = select_record("Students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Jane")
    
    @patch('builtins.input')
    def test_delete_student_cancelled(self, mock_input):
        create_table("Students")
        self.app.current_table = "Students"
        
        create_record("Students", 1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["1", "n"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._delete_student()
            output = mock_stdout.getvalue()
            self.assertIn("Удаление отменено", output)
        
        records = select_record("Students")
        self.assertEqual(len(records), 1)
    
    @patch('builtins.input')
    def test_delete_student_not_found(self, mock_input):
        create_table("Students")
        self.app.current_table = "Students"
        mock_input.side_effect = ["999"]
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._delete_student()
            output = mock_stdout.getvalue()
            self.assertTrue(
                len(output) > 0,
                f"Должен быть какой-то вывод. Получено: {output}"
            )

    
    @patch('builtins.input')
    def test_show_all_students_with_table(self, mock_input):
        create_table("Students")
        self.app.current_table = "Students"
        
        create_record("Students", 1, "John", "Doe", 20, "M")
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.app._show_all_students()
            output = mock_stdout.getvalue()
            self.assertIn("John", output)

    def test_read_optional_int_valid(self):
        with patch('builtins.input', return_value="25"):
            result = self.app._read_optional_int("Введите: ")
            self.assertEqual(result, 25)

    def test_read_optional_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=["abc", "18"]):
            result = self.app._read_optional_int("Введите: ")
            self.assertEqual(result, 18)

    def test_current_table_none_after_init(self):
        self.assertIsNone(self.app.current_table)

    def test_current_table_set_after_create(self):
        with patch('builtins.input', return_value="NewTable"):
            self.app._create_table()
            self.assertEqual(self.app.current_table, "NewTable")

    def test_select_table_works(self):
        create_table("Table1")
        create_table("Table2")
        with patch('builtins.input', return_value="2"):
            self.app._select_table()
            self.assertEqual(self.app.current_table, "Table2")

    def test_create_duplicate_table_fails(self):
        create_table("Existing")
        with patch('builtins.input', return_value="Existing"):
            with patch('sys.stdout', new_callable=StringIO) as mock:
                self.app._create_table()
                self.assertIn("уже существует", mock.getvalue())

    def test_add_student_without_table_shows_error(self):
        self.app.current_table = None
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._add_student()
            self.assertIn("сначала создайте или выберите таблицу", mock.getvalue())

    def test_show_all_without_table_shows_error(self):
        self.app.current_table = None
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._show_all_students()
            self.assertIn("сначала создайте или выберите таблицу", mock.getvalue())

    def test_update_without_table_shows_error(self):
        self.app.current_table = None
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._update_student()
            self.assertIn("сначала создайте или выберите таблицу", mock.getvalue())

    def test_delete_without_table_shows_error(self):
        self.app.current_table = None
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._delete_student()
            self.assertIn("сначала создайте или выберите таблицу", mock.getvalue())

    def test_find_by_filter_without_table_shows_error(self):
        self.app.current_table = None
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._find_students_by_filter()
            self.assertIn("сначала создайте или выберите таблицу", mock.getvalue())

    def test_has_current_table_attribute(self):
        self.assertTrue(hasattr(self.app, 'current_table'))

    def test_app_can_be_created(self):
        app = Student_tui()
        self.assertIsNotNone(app)

    def test_select_table_empty_list(self):
        TABLES.clear()
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._select_table()
            self.assertIn("Нет созданных таблиц", mock.getvalue())

    def test_select_table_invalid_choice(self):
        create_table("Table1")
        create_table("Table2")
        
        with patch('builtins.input', return_value="99"):
            with patch('sys.stdout', new_callable=StringIO) as mock:
                self.app._select_table()
                self.assertIn("Неверный выбор", mock.getvalue())

    def test_select_table_valid_choice(self):
        create_table("Table1")
        create_table("Table2")
        create_table("Table3")
        
        with patch('builtins.input', return_value="2"):
            self.app._select_table()
            self.assertEqual(self.app.current_table, "Table2")

    def test_show_all_with_empty_table(self):
        create_table("Students")
        self.app.current_table = "Students"
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._show_all_students()
            self.assertIn("Записи не найдены", mock.getvalue())

    def test_show_all_with_data(self):
        create_table("Students")
        self.app.current_table = "Students"
        create_record("Students", 1, "John", "Doe", 20, "M")
        create_record("Students", 2, "Jane", "Smith", 22, "F")
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._show_all_students()
            output = mock.getvalue()
            self.assertIn("John", output)
            self.assertIn("Jane", output)

    def test_add_student_duplicate_id(self):
        create_table("Students")
        self.app.current_table = "Students"
        create_record("Students", 1, "John", "Doe", 20, "M")
        
        with patch('builtins.input', side_effect=["1", "Jane", "Smith", "22", "F"]):
            with patch('sys.stdout', new_callable=StringIO) as mock:
                self.app._add_student()
                self.assertIn("уже существует", mock.getvalue())
        
        records = select_record("Students")
        self.assertEqual(len(records), 1)

    def test_add_student_invalid_sex(self):
        create_table("Students")
        self.app.current_table = "Students"
        
        with patch('builtins.input', side_effect=["1", "John", "Doe", "20", "X"]):
            with patch('sys.stdout', new_callable=StringIO) as mock:
                self.app._add_student()
                self.assertIn("Пол должен быть", mock.getvalue())
        
        records = select_record("Students")
        self.assertEqual(len(records), 0)

    def test_update_student_negative_age(self):
        create_table("Students")
        self.app.current_table = "Students"
        create_record("Students", 1, "John", "Doe", 20, "M")
        
        with patch('builtins.input', side_effect=["1", "", "", "-5", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock:
                self.app._update_student()
                self.assertIn("не может быть отрицательным", mock.getvalue())
        
        record = select_record("Students", student_id=1)[0]
        self.assertEqual(record[3], 20)

    def test_delete_student_not_found_message(self):
        create_table("Students")
        self.app.current_table = "Students"
        
        with patch('builtins.input', return_value="999"):
            with patch('sys.stdout', new_callable=StringIO) as mock:
                self.app._delete_student()
                output = mock.getvalue()
                self.assertTrue("не найден" in output or "не найдена" in output or "Таблица пуста" in output)

    def test_find_by_filter_with_data(self):
        create_table("Students")
        self.app.current_table = "Students"
        create_record("Students", 1, "John", "Doe", 20, "M")
        create_record("Students", 2, "Jane", "Smith", 22, "F")
        
        with patch('builtins.input', side_effect=["", "", "", "", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock:
                self.app._find_students_by_filter()
                output = mock.getvalue()
                self.assertIn("John", output)
                self.assertIn("Jane", output)

if __name__ == "__main__":
    unittest.main()