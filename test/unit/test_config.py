import unittest
from pyfakefs.fake_filesystem_unittest import TestCase
from pathlib import Path

import mediama.config as config
import mediama.utils as utils


class TestSourceNormalizer(unittest.TestCase):
    def test_empty_source_list(self):
        sources = []
        config.normalize_sources(sources)
        self.assertListEqual([], sources)

    def test_list_of_strings(self):
        sources = ["s0", "s1", "s2"]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
            {"name": "s2", "id": "src_2", "kwargs": {}},
        ]
        config.normalize_sources(sources)
        self.assertListEqual(expected, sources)

    def test_list_of_dicts(self):
        sources = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        config.normalize_sources(sources)
        self.assertListEqual(expected, sources)

    def test_mixed_source_types(self):
        sources = [
            "s0",
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        config.normalize_sources(sources)
        self.assertListEqual(expected, sources)

    def test_unknown_keys_in_source(self):
        sources = [
            {"name": "s0", "id": "src_0", "kwargs": {}, "foo": "bar", "hello": "world"},
            {"name": "s1", "id": "src_1", "kwargs": {}, "p": "np"},
        ]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        config.normalize_sources(sources)
        self.assertListEqual(expected, sources)

    def test_only_name_in_source(self):
        sources = [
            {"name": "s0"},
            {"name": "s1"},
        ]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        config.normalize_sources(sources)
        self.assertListEqual(expected, sources)

    def test_given_keys_in_source(self):
        sources = [
            {"name": "s0", "id": "custom_id"},
            {"name": "s1", "kwargs": {"foo": "bar"}},
        ]
        expected = [
            {"name": "s0", "id": "custom_id", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {"foo": "bar"}},
        ]
        config.normalize_sources(sources)
        self.assertListEqual(expected, sources)

    def test_name_missing(self):
        sources = [{"id": "src_0"}]
        with self.assertRaises(KeyError):
            config.normalize_sources(sources)


class TestPreNormalizer(unittest.TestCase):
    def test_empty_pre_list(self):
        pres = []
        config.normalize_pres(pres)
        self.assertListEqual([], pres)

    def test_list_of_strings(self):
        pres = ["p0", "p1", "p2"]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
            {"name": "p2", "id": "pre_2", "kwargs": {}},
        ]
        config.normalize_pres(pres)
        self.assertListEqual(expected, pres)

    def test_list_of_dicts(self):
        pres = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        config.normalize_pres(pres)
        self.assertListEqual(expected, pres)

    def test_mixed_pre_types(self):
        pres = [
            "p0",
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        config.normalize_pres(pres)
        self.assertListEqual(expected, pres)

    def test_unknown_keys_in_pre(self):
        pres = [
            {"name": "p0", "id": "pre_0", "kwargs": {}, "foo": "bar", "hello": "world"},
            {"name": "p1", "id": "pre_1", "kwargs": {}, "p": "np"},
        ]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        config.normalize_pres(pres)
        self.assertListEqual(expected, pres)

    def test_only_name_in_pre(self):
        pres = [
            {"name": "p0"},
            {"name": "p1"},
        ]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        config.normalize_pres(pres)
        self.assertListEqual(expected, pres)

    def test_given_keys_in_pre(self):
        pres = [
            {"name": "p0", "id": "custom_id"},
            {"name": "p1", "kwargs": {"foo": "bar"}},
        ]
        expected = [
            {"name": "p0", "id": "custom_id", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {"foo": "bar"}},
        ]
        config.normalize_pres(pres)
        self.assertListEqual(expected, pres)

    def test_name_missing(self):
        pres = [{"id": "pre_0"}]
        with self.assertRaises(KeyError):
            config.normalize_pres(pres)


class TestPostNormalizer(unittest.TestCase):
    def test_empty_post_list(self):
        posts = []
        config.normalize_posts(posts)
        self.assertListEqual([], posts)

    def test_list_of_strings(self):
        posts = ["p0", "p1", "p2"]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
            {"name": "p2", "id": "post_2", "kwargs": {}},
        ]
        config.normalize_posts(posts)
        self.assertListEqual(expected, posts)

    def test_list_of_dicts(self):
        posts = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        config.normalize_posts(posts)
        self.assertListEqual(expected, posts)

    def test_mixed_post_types(self):
        posts = [
            "p0",
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        config.normalize_posts(posts)
        self.assertListEqual(expected, posts)

    def test_unknown_keys_in_post(self):
        posts = [
            {
                "name": "p0",
                "id": "post_0",
                "kwargs": {},
                "foo": "bar",
                "hello": "world",
            },
            {"name": "p1", "id": "post_1", "kwargs": {}, "p": "np"},
        ]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        config.normalize_posts(posts)
        self.assertListEqual(expected, posts)

    def test_only_name_in_post(self):
        posts = [
            {"name": "p0"},
            {"name": "p1"},
        ]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        config.normalize_posts(posts)
        self.assertListEqual(expected, posts)

    def test_given_keys_in_post(self):
        posts = [
            {"name": "p0", "id": "custom_id"},
            {"name": "p1", "kwargs": {"foo": "bar"}},
        ]
        expected = [
            {"name": "p0", "id": "custom_id", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {"foo": "bar"}},
        ]
        config.normalize_posts(posts)
        self.assertListEqual(expected, posts)

    def test_name_missing(self):
        posts = [{"id": "post_0"}]
        with self.assertRaises(KeyError):
            config.normalize_posts(posts)


class TestDuplicateIdFilter(unittest.TestCase):
    def test_duplicates(self):
        tasks = [{"id": "t0"}, {"id": "t1"}, {"id": "t0"}, {"id": "t4"}]
        expected = [{"id": "t0"}, {"id": "t1"}, {"id": "t4"}]
        config.filter_duplicate_ids(tasks)
        self.assertListEqual(expected, tasks)

    def test_no_duplicates(self):
        tasks = [{"id": "t0"}, {"id": "t1"}, {"id": "t4"}]
        expected = [{"id": "t0"}, {"id": "t1"}, {"id": "t4"}]
        config.filter_duplicate_ids(tasks)
        self.assertListEqual(expected, tasks)


class TestConfigDiscovery(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_user_specified_config(self):
        self.fail()

    def test_system_specified_config(self):
        self.fail()

    def test_no_config(self):
        expected = utils.get_project_root().joinpath(
            "mediama", "default_config.json"
        )
        self.assertEqual(expected, config.discover_config())

    def test_python_config(self):
        self.fail()

class TestConfigLoader(TestCase):
    def test_json(self):
        self.fail()
    def test_json_with_comments(self):
        self.fail()
    def test_python(self):
        self.fail()
