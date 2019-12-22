import unittest
import unittest.mock as mock
from pathlib import Path
import sys, importlib
from textwrap import dedent

import mediama.utils as utils

# A trivial test suite!!
class TestGetProjectRoot(unittest.TestCase):
    def test_function(self):
        expected = Path(__file__).parent.parent.parent
        result = utils.get_project_root()
        self.assertEqual(expected, result)


class TestDiscoverModules(unittest.TestCase):
    def test_search_dir_empty(self):
        search_dir = Path("/null")

        path_mock = mock.MagicMock(return_value=search_dir)
        path_mock.iterdir.return_value = []

        expected = []
        mod_paths = sorted(
            [path.return_value for path in utils.discover_modules(path_mock)]
        )

        self.assertListEqual(expected, mod_paths)

    def test_no_py_files(self):
        search_dir = Path("/null")
        file2 = search_dir / "file2.js"
        file3 = search_dir / "file3.c"

        file2_mock = mock.MagicMock(return_value=file2)
        file2_mock.is_file.return_value = True
        file2_mock.suffix = ".js"

        file3_mock = mock.MagicMock(return_value=file3)
        file3_mock.is_file.return_value = True
        file3_mock.suffix = ".c"

        path_mock = mock.MagicMock(return_value=search_dir)
        path_mock.iterdir.return_value = [file2_mock, file3_mock]

        expected = []
        mod_paths = sorted(
            [path.return_value for path in utils.discover_modules(path_mock)]
        )

        self.assertListEqual(expected, mod_paths)

    def test_one_py(self):
        search_dir = Path("/null")
        file1 = search_dir / "file1.js"

        file1_mock = mock.MagicMock(return_value=file1)
        file1_mock.is_file.return_value = True
        file1_mock.suffix = ".py"

        path_mock = mock.MagicMock(return_value=search_dir)
        path_mock.iterdir.return_value = [file1_mock]

        expected = [file1]
        mod_paths = sorted(
            [path.return_value for path in utils.discover_modules(path_mock)]
        )

        self.assertListEqual(expected, mod_paths)

    def test_two_py(self):
        search_dir = Path("/null")
        file2 = search_dir / "file2.py"
        file3 = search_dir / "file3.py"

        file2_mock = mock.MagicMock(return_value=file2)
        file2_mock.is_file.return_value = True
        file2_mock.suffix = ".py"

        file3_mock = mock.MagicMock(return_value=file3)
        file3_mock.is_file.return_value = True
        file3_mock.suffix = ".py"

        path_mock = mock.MagicMock(return_value=search_dir)
        path_mock.iterdir.return_value = [file2_mock, file3_mock]

        expected = [file2, file3]
        mod_paths = sorted(
            [path.return_value for path in utils.discover_modules(path_mock)]
        )

        self.assertListEqual(expected, mod_paths)

    def test_one_pkg(self):
        search_dir = Path("/mod_dir")
        sub_dir = search_dir / "subdir"

        subdir_mock = mock.MagicMock(return_value=sub_dir)
        subdir_mock.is_file.return_value = False
        subdir_mock.is_dir.return_value = True
        subdir_mock.iterdir.return_value = ["b.py", "__init__.py"]

        path_mock = mock.MagicMock(return_value=search_dir)
        path_mock.iterdir.return_value = [subdir_mock]

        expected = [sub_dir]

        mod_paths = sorted(
            [path.return_value for path in utils.discover_modules(path_mock)]
        )

        self.assertListEqual(expected, mod_paths)

    def test_two_pkg(self):
        search_dir = Path("/mod_dir")
        sub_dir1 = search_dir / "subdir1"
        sub_dir2 = search_dir / "subdir2"

        subdir1_mock = mock.MagicMock(return_value=sub_dir1)
        subdir1_mock.is_file.return_value = False
        subdir1_mock.is_dir.return_value = True
        subdir1_mock.iterdir.return_value = ["a.py", "__init__.py"]

        subdir2_mock = mock.MagicMock(return_value=sub_dir2)
        subdir2_mock.is_file.return_value = False
        subdir2_mock.is_dir.return_value = True
        subdir2_mock.iterdir.return_value = ["b.py", "__init__.py"]

        path_mock = mock.MagicMock(return_value=search_dir)
        path_mock.iterdir.return_value = [subdir1_mock, subdir2_mock]

        expected = sorted([sub_dir1, sub_dir2])

        mod_paths = sorted(
            [path.return_value for path in utils.discover_modules(path_mock)]
        )

        self.assertListEqual(expected, mod_paths)

    def test_subdir_no_init(self):
        search_dir = Path("/mod_dir")
        sub_dir = search_dir / "subdir"

        subdir_mock = mock.MagicMock(return_value=sub_dir)
        subdir_mock.is_file.return_value = False
        subdir_mock.is_dir.return_value = True
        subdir_mock.iterdir.return_value = ["b.py", "a.py"]

        path_mock = mock.MagicMock(return_value=search_dir)
        path_mock.iterdir.return_value = [subdir_mock]

        expected = []

        mod_paths = list(utils.discover_modules(path_mock))

        self.assertListEqual(expected, mod_paths)

    def test_mix(self):
        search_dir = Path("/mod_dir")
        file1 = search_dir / "file1.py"
        file2 = search_dir / "file2.js"
        file3 = search_dir / "file3.c"
        sub_dir1 = search_dir / "subdir1"
        sub_dir2 = search_dir / "subdir2"

        file1_mock = mock.MagicMock(return_value=file1)
        file1_mock.is_file.return_value = True
        file1_mock.suffix = ".py"

        file2_mock = mock.MagicMock(return_value=file2)
        file2_mock.is_file.return_value = True
        file2_mock.suffix = ".js"

        file3_mock = mock.MagicMock(return_value=file3)
        file3_mock.is_file.return_value = True
        file3_mock.suffix = ".c"

        subdir1_mock = mock.MagicMock(return_value=sub_dir1)
        subdir1_mock.is_file.return_value = False
        subdir1_mock.is_dir.return_value = True
        subdir1_mock.iterdir.return_value = ["a.py", "__init__.py"]

        subdir2_mock = mock.MagicMock(return_value=sub_dir2)
        subdir2_mock.is_file.return_value = False
        subdir2_mock.is_dir.return_value = True
        subdir2_mock.iterdir.return_value = ["b.py", "__init__.py"]

        path_mock = mock.MagicMock(return_value=search_dir)
        path_mock.iterdir.return_value = [
            subdir1_mock,
            subdir2_mock,
            file1_mock,
            file2_mock,
            file3_mock,
        ]

        expected = sorted([sub_dir1, sub_dir2, file1])

        mod_paths = sorted(
            [path.return_value for path in utils.discover_modules(path_mock)]
        )

        self.assertListEqual(expected, mod_paths)


class TestGetSubclassFromModule(unittest.TestCase):
    @staticmethod
    def create_module_from_string(s, g):
        # Dynmically create a module
        # https://stackoverflow.com/a/53080237

        test_spec = importlib.util.spec_from_loader("test_mod", loader=None)
        test_module = importlib.util.module_from_spec(test_spec)

        exec(dedent(s), g)

        return test_module

    @mock.patch(
        "mediama.utils.dir", return_value=("TestClass1", "TestClass2", "SubClass1")
    )
    def test_one_subclass(self, mock_dir):
        # Assume module has these classes below
        class TestClass1:
            pass

        class TestClass2:
            pass

        class SubClass1(TestClass1):
            pass

        # END CODE

        mock_mod = mock.MagicMock()
        get_attr_side_effect = (TestClass1, TestClass2, SubClass1)
        with mock.patch(
            "mediama.utils.getattr", side_effect=get_attr_side_effect
        ) as mock_getattr:
            results = {
                obj.__name__
                for obj in utils.get_subclasses_from_module(mock_mod, TestClass1)
            }
            self.assertEqual(mock_getattr.call_count, len(get_attr_side_effect))
        mock_dir.assert_called_once()

        expected = {"SubClass1"}
        self.assertSetEqual(expected, results)

    @mock.patch(
        "mediama.utils.dir", return_value=("TestClass1", "TestClass2")
    )
    def test_no_subclass(self, mock_dir):
        # Assume module has these classes below
        class TestClass1:
            pass

        class TestClass2:
            pass

        # END CODE

        mock_mod = mock.MagicMock()

        get_attr_side_effect = (TestClass1, TestClass2)
        with mock.patch(
            "mediama.utils.getattr", side_effect=get_attr_side_effect
        ) as mock_getattr:
            results = {
                obj.__name__
                for obj in utils.get_subclasses_from_module(mock_mod, TestClass1)
            }
            self.assertEqual(mock_getattr.call_count, len(get_attr_side_effect))
        mock_dir.assert_called_once()

        expected = set()
        self.assertSetEqual(expected, results)
    @mock.patch(
        "mediama.utils.dir", return_value=("TestClass1", "TestClass2", "SubClass1", "SubClassA")
    )
    def test_two_subclass(self, mock_dir):
        # Assume module has these classes below
        class TestClass1:
            pass

        class TestClass2:
            pass

        class SubClass1(TestClass1):
            pass

        class SubClassA(TestClass1):
            pass

        # END CODE

        mock_mod = mock.MagicMock()

        get_attr_side_effect = (TestClass1, TestClass2, SubClass1, SubClassA)
        with mock.patch(
            "mediama.utils.getattr", side_effect=get_attr_side_effect
        ) as mock_getattr:
            results = {
                obj.__name__
                for obj in utils.get_subclasses_from_module(mock_mod, TestClass1)
            }
            self.assertEqual(mock_getattr.call_count, len(get_attr_side_effect))
        mock_dir.assert_called_once()

        expected = {"SubClass1", "SubClassA"}
        self.assertSetEqual(expected, results)
