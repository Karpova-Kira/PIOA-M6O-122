import unittest
from unittest.mock import patch
from io import StringIO
from src.db.tui import Student_tui
from src.db.backend.memory import StudentTable


class TestTUIAdvanced(unittest.TestCase):

    def setUp(self):
        # Очищаем таблицы через внутренний словарь
        StudentTable._tables.clear()
        StudentTable._id_counters.clear()
        self.app = Student_tui()
    
    @patch('builtins.input')
    def test_read_int_valid(self, mock_input):
        mock_input.return_value = "42"
        result = self.app._read_int("Enter: ")
        self.assertEqual(result, 42)
    
    @patch('builtins.input')
    def test_read_int_invalid_then_valid(self, mock_input):
        mock_input.side_effect = ["abc", "10"]
        result = self.app._read_int("Enter: ")
        self.assertEqual(result, 10)
    
    @patch('builtins.input')
    def test_read_optional_int_empty(self, mock_input):
        mock_input.return_value = ""
        result = self.app._read_optional_int("Enter: ")
        self.assertIsNone(result)
    
    @patch('builtins.input')
    def test_read_optional_int_valid(self, mock_input):
        mock_input.return_value = "25"
        result = self.app._read_optional_int("Enter: ")
        self.assertEqual(result, 25)
    
    def test_print_records_empty(self):
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._print_records([])
            self.assertIn("Записи не найдены", mock.getvalue())
    
    def test_print_records_non_empty(self):
        records = [(1, "John", "Doe", 20, "M")]
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._print_records(records)
            self.assertIn("John", mock.getvalue())
    
    def test_print_menu(self):
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._print_menu()
            output = mock.getvalue()
            self.assertIn("=== База студентов ===", output)
    
    @patch('builtins.input')
    def test_create_table(self, mock_input):
        mock_input.return_value = "TestTable"
        self.app._create_table()
        self.assertEqual(self.app.current_table_name, "TestTable")
        self.assertIsNotNone(self.app.current_table)
    
    @patch('builtins.input')
    def test_create_table_empty_name(self, mock_input):
        mock_input.return_value = ""
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._create_table()
            self.assertIn("название таблицы не может быть пустым", mock.getvalue())
    
    @patch('builtins.input')
    def test_add_student_no_table(self, mock_input):
        self.app.current_table = None
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._add_student()
            self.assertIn("сначала создайте или выберите таблицу", mock.getvalue())
    
    @patch('builtins.input')
    def test_show_all_no_table(self, mock_input):
        self.app.current_table = None
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._show_all_students()
            self.assertIn("сначала создайте или выберите таблицу", mock.getvalue())

    @patch('builtins.input')
    def test_select_table_with_tables(self, mock_input):
        StudentTable.create_table("Table1")
        StudentTable.create_table("Table2")
        
        mock_input.return_value = "2"
        self.app._select_table()
        
        self.assertEqual(self.app.current_table_name, "Table2")
        self.assertIsNotNone(self.app.current_table)

    @patch('builtins.input')
    def test_select_table_invalid_choice(self, mock_input):
        StudentTable.create_table("Table1")
        StudentTable.create_table("Table2")
        
        mock_input.return_value = "99"
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._select_table()
            self.assertIn("Неверный выбор", mock.getvalue())

    @patch('builtins.input')
    def test_select_table_non_number(self, mock_input):
        StudentTable.create_table("Table1")
        
        mock_input.return_value = "abc"
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._select_table()
            self.assertIn("Неверный выбор", mock.getvalue())

    @patch('builtins.input')
    def test_add_student_success(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        mock_input.side_effect = ["1", "John", "Doe", "20", "M"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._add_student()
            self.assertIn("Запись добавлена", mock.getvalue())
        
        records = self.app.current_table.get_all()
        self.assertEqual(len(records), 1)

    @patch('builtins.input')
    def test_add_student_duplicate_id(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["1", "Jane", "Smith", "22", "F"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._add_student()
            self.assertIn("уже существует", mock.getvalue())

    @patch('builtins.input')
    def test_add_student_negative_age(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        mock_input.side_effect = ["1", "John", "Doe", "-5", "M"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._add_student()
            self.assertIn("Ошибка", mock.getvalue())

    @patch('builtins.input')
    def test_update_student_success(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["1", "Jonathan", "", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._update_student()
            self.assertIn("Запись обновлена", mock.getvalue())
        
        record = self.app.current_table.select_record(student_id=1)[0]
        self.assertEqual(record[1], "Jonathan")

    @patch('builtins.input')
    def test_update_student_not_found(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        mock_input.side_effect = ["999"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._update_student()
            self.assertIn("не найден", mock.getvalue())

    @patch('builtins.input')
    def test_delete_student_success(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["1", "y"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._delete_student()
            self.assertIn("успешно удалена", mock.getvalue())
        
        records = self.app.current_table.get_all()
        self.assertEqual(len(records), 0)

    @patch('builtins.input')
    def test_find_students_by_filter_by_name(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        self.app.current_table.create_record(2, "Jane", "Smith", 22, "F")
        
        mock_input.side_effect = ["", "Jane", "", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._find_students_by_filter()
            output = mock.getvalue()
            self.assertIn("Jane", output)
            self.assertNotIn("John", output)

    @patch('builtins.input')
    def test_find_students_by_filter_by_id(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        self.app.current_table.create_record(2, "Jane", "Smith", 22, "F")
        
        mock_input.side_effect = ["1", "", "", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._find_students_by_filter()
            output = mock.getvalue()
            self.assertIn("John", output)
            self.assertNotIn("Jane", output)


    @patch('builtins.input')
    def test_delete_student_cancelled(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["1", "n"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._delete_student()
            self.assertIn("Удаление отменено", mock.getvalue())
        
        records = self.app.current_table.get_all()
        self.assertEqual(len(records), 1)

    @patch('builtins.input')
    def test_find_students_by_filter_all_empty(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        self.app.current_table.create_record(2, "Jane", "Smith", 22, "F")
        
        mock_input.side_effect = ["", "", "", "", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._find_students_by_filter()
            output = mock.getvalue()
            self.assertIn("John", output)
            self.assertIn("Jane", output)

    @patch('builtins.input')
    def test_find_students_by_filter_by_sex(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        self.app.current_table.create_record(2, "Jane", "Smith", 22, "F")
        
        mock_input.side_effect = ["", "", "", "", "F"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._find_students_by_filter()
            output = mock.getvalue()
            self.assertIn("Jane", output)
            self.assertNotIn("John", output)

    @patch('builtins.input')
    def test_find_students_by_filter_by_age(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        self.app.current_table.create_record(2, "Jane", "Smith", 22, "F")
        
        mock_input.side_effect = ["", "", "", "20", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._find_students_by_filter()
            output = mock.getvalue()
            self.assertIn("John", output)
            self.assertNotIn("Jane", output)

    @patch('builtins.input')
    def test_show_all_students_with_data(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        self.app.current_table.create_record(2, "Jane", "Smith", 22, "F")
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._show_all_students()
            output = mock.getvalue()
            self.assertIn("John", output)
            self.assertIn("Jane", output)

    @patch('builtins.input')
    def test_show_all_students_empty_table(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._show_all_students()
            self.assertIn("Записи не найдены", mock.getvalue())

    @patch('builtins.input')
    def test_create_table_value_error(self, mock_input):
        StudentTable.create_table("Existing")
        mock_input.return_value = "Existing"
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._create_table()
            self.assertIn("уже существует", mock.getvalue())

    @patch('builtins.input')
    def test_select_table_empty_list(self, mock_input):
        StudentTable._tables.clear()
        StudentTable._id_counters.clear()
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._select_table()
            self.assertIn("Нет созданных таблиц", mock.getvalue())

    @patch('builtins.input')
    def test_update_student_with_sex_change(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["1", "", "", "", "F"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._update_student()
            self.assertIn("Запись обновлена", mock.getvalue())
        
        record = self.app.current_table.select_record(student_id=1)[0]
        self.assertEqual(record[4], "F")


    @patch('builtins.input')
    def test_update_student_negative_age(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["1", "", "", "-5", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._update_student()
            self.assertIn("не может быть отрицательным", mock.getvalue())

    @patch('builtins.input')
    def test_update_student_invalid_age_type(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["1", "", "", "abc", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._update_student()
            self.assertIn("должен быть целым числом", mock.getvalue())

    @patch('builtins.input')
    def test_delete_student_empty_table(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._delete_student()
            self.assertIn("Таблица пуста", mock.getvalue())

    @patch('builtins.input')
    def test_find_students_by_filter_no_results(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        self.app.current_table.create_record(1, "John", "Doe", 20, "M")
        
        mock_input.side_effect = ["", "", "", "99", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._find_students_by_filter()
            self.assertIn("Записи не найдены", mock.getvalue())

    @patch('builtins.input')
    def test_read_optional_int_invalid_then_valid(self, mock_input):
        mock_input.side_effect = ["abc", ""]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            result = self.app._read_optional_int("Enter: ")
            self.assertIsNone(result)
            self.assertIn("введите целое число", mock.getvalue())

    @patch('builtins.input')
    def test_create_table_with_whitespace_name(self, mock_input):
        mock_input.return_value = "   "
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._create_table()
            self.assertIn("название таблицы не может быть пустым", mock.getvalue())

    @patch('builtins.input')
    def test_add_student_with_empty_fields(self, mock_input):
        StudentTable.create_table("Students")
        self.app.current_table = StudentTable("Students")
        self.app.current_table_name = "Students"
        
        mock_input.side_effect = ["1", "", "", "20", "M"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.app._add_student()
            self.assertIn("Запись добавлена", mock.getvalue())

    @patch('builtins.input')
    def test_run_invalid_choice(self, mock_input):
        mock_input.side_effect = ["99", "0"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            try:
                self.app.run()
            except SystemExit:
                pass
            output = mock_out.getvalue()
            self.assertIn("Неизвестная команда", output)

if __name__ == "__main__":
    unittest.main()