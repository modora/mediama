import unittest
import unittest.mock as mock
from pathlib import Path
import importlib
from textwrap import dedent


import mediama.managers as managers


@mock.patch("mediama.managers.discover_modules")
@mock.patch("mediama.managers.import_module_from_path")
@mock.patch("mediama.managers.get_subclasses_from_module")
class TestBaseTaskManager_discover_tasks(unittest.TestCase):
    def test_no_search_dir(
        self,
        get_subclasses_from_module_mock,
        import_module_from_path_mock,
        discover_modules_mock,
    ):
        cfg = {"search_dirs": []}
        varpool = mock.Mock(cfg)
        mgr = managers.BaseTaskManager(cfg, varpool)

        discover_modules_mock.return_value = iter(())
        tasks = mgr._discover_tasks(managers.Task)
        expected = {}

        self.assertDictEqual(expected, tasks)
        discover_modules_mock.assert_not_called()
        import_module_from_path_mock.assert_not_called()
        get_subclasses_from_module_mock.assert_not_called()

    def test_nonexistent_dirs(
        self,
        get_subclasses_from_module_mock,
        import_module_from_path_mock,
        discover_modules_mock,
    ):
        d = Path("/tasks")
        cfg = {"search_dirs": [d]}
        varpool = mock.Mock(cfg)
        mgr = managers.BaseTaskManager(cfg, varpool)

        discover_modules_mock.return_value = iter(())

        tasks = mgr._discover_tasks(managers.Task)
        expected = {}

        self.assertDictEqual(expected, tasks)
        discover_modules_mock.assert_not_called()
        import_module_from_path_mock.assert_not_called()
        get_subclasses_from_module_mock.assert_not_called()

    @mock.patch("mediama.managers.Path.exists", return_value=True)
    def test_empty_dir(
        self,
        path_exists_mock,
        get_subclasses_from_module_mock,
        import_module_from_path_mock,
        discover_modules_mock,
    ):
        d = Path("/tasks")
        cfg = {"search_dirs": [d]}
        varpool = mock.Mock(cfg)
        mgr = managers.BaseTaskManager(cfg, varpool)

        discover_modules_mock.return_value = iter(())

        tasks = mgr._discover_tasks(managers.Task)
        expected = {}

        self.assertDictEqual(expected, tasks)
        discover_modules_mock.assert_called_once()
        import_module_from_path_mock.assert_not_called()
        get_subclasses_from_module_mock.assert_not_called()

    @mock.patch("mediama.managers.Path.exists", return_value=True)
    def test_no_task_in_module(
        self,
        path_exists_mock,
        get_subclasses_from_module_mock,
        import_module_from_path_mock,
        discover_modules_mock,
    ):
        d = Path("/tasks")
        f = d / "test_mod.py"
        cfg = {"search_dirs": [d]}
        varpool = mock.Mock(cfg)
        mgr = managers.BaseTaskManager(cfg, varpool)

        discover_modules_mock.return_value = iter((f,))
        get_subclasses_from_module_mock.return_value = iter(())

        tasks = mgr._discover_tasks(managers.Task)
        expected = {}

        self.assertDictEqual(expected, tasks)
        discover_modules_mock.assert_called_once()
        import_module_from_path_mock.assert_called_once()
        get_subclasses_from_module_mock.assert_called_once()

    @mock.patch("mediama.managers.Path.exists", return_value=True)
    def test_single_task_in_module(
        self,
        path_exists_mock,
        get_subclasses_from_module_mock,
        import_module_from_path_mock,
        discover_modules_mock,
    ):
        d = Path("/tasks")
        f = d / "mod.py"
        cfg = {"search_dirs": [d]}
        varpool = mock.Mock(cfg)
        mgr = managers.BaseTaskManager(cfg, varpool)

        def get_subclasses_from_module_mock_return_value():
            class SomeTask(managers.Task):
                pass

            yield SomeTask

        discover_modules_mock.return_value = iter((f,))
        get_subclasses_from_module_mock.return_value = (
            get_subclasses_from_module_mock_return_value()
        )

        tasks = mgr._discover_tasks(managers.Task)
        expected = set(("SomeTask",))

        self.assertSetEqual(expected, set(tasks.keys()))
        discover_modules_mock.assert_called_once()
        import_module_from_path_mock.assert_called_once()
        get_subclasses_from_module_mock.assert_called_once()
