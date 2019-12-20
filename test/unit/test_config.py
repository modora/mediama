import unittest
import mediama.config as config


class TestSourceNormalizer(unittest.TestCase):
    def test_empty_source_list(self):
        sources = []
        self.assertListEqual([], config.normalize_sources(sources))

    def test_list_of_strings(self):
        sources = ["s0", "s1", "s2"]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
            {"name": "s2", "id": "src_2", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_sources(sources))

    def test_list_of_dicts(self):
        sources = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_sources(sources))

    def test_mixed_source_types(self):
        sources = [
            "s0",
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_sources(sources))

    def test_unknown_keys_in_source(self):
        sources = [
            {"name": "s0", "id": "src_0", "kwargs": {}, "foo": "bar", "hello": "world"},
            {"name": "s1", "id": "src_1", "kwargs": {}, "p": "np"},
        ]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_sources(sources))

    def test_only_name_in_source(self):
        sources = [
            {"name": "s0"},
            {"name": "s1"},
        ]
        expected = [
            {"name": "s0", "id": "src_0", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_sources(sources))

    def test_given_keys_in_source(self):
        sources = [
            {"name": "s0", "id": 'custom_id'},
            {"name": "s1", "kwargs":{'foo':'bar'}},
        ]
        expected = [
            {"name": "s0", "id": "custom_id", "kwargs": {}},
            {"name": "s1", "id": "src_1", "kwargs": {'foo':'bar'}},
        ]
        self.assertListEqual(expected, config.normalize_sources(sources))

    def test_name_missing(self):
        sources = [
            {"id": "src_0"}
        ]
        with self.assertRaises(KeyError):
            config.normalize_sources(sources)

class TestPreNormalizer(unittest.TestCase):
    def test_empty_pre_list(self):
        pres = []
        self.assertListEqual([], config.normalize_pres(pres))

    def test_list_of_strings(self):
        pres = ["p0", "p1", "p2"]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
            {"name": "p2", "id": "pre_2", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_pres(pres))

    def test_list_of_dicts(self):
        pres = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_pres(pres))

    def test_mixed_pre_types(self):
        pres = [
            "p0",
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_pres(pres))

    def test_unknown_keys_in_pre(self):
        pres = [
            {"name": "p0", "id": "pre_0", "kwargs": {}, "foo": "bar", "hello": "world"},
            {"name": "p1", "id": "pre_1", "kwargs": {}, "p": "np"},
        ]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_pres(pres))

    def test_only_name_in_pre(self):
        pres = [
            {"name": "p0"},
            {"name": "p1"},
        ]
        expected = [
            {"name": "p0", "id": "pre_0", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_pres(pres))

    def test_given_keys_in_pre(self):
        pres = [
            {"name": "p0", "id": 'custom_id'},
            {"name": "p1", "kwargs":{'foo':'bar'}},
        ]
        expected = [
            {"name": "p0", "id": "custom_id", "kwargs": {}},
            {"name": "p1", "id": "pre_1", "kwargs": {'foo':'bar'}},
        ]
        self.assertListEqual(expected, config.normalize_pres(pres))

    def test_name_missing(self):
        pres = [
            {"id": "pre_0"}
        ]
        with self.assertRaises(KeyError):
            config.normalize_pres(pres)

class TestPostNormalizer(unittest.TestCase):
    def test_empty_post_list(self):
        posts = []
        self.assertListEqual([], config.normalize_posts(posts))

    def test_list_of_strings(self):
        posts = ["p0", "p1", "p2"]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
            {"name": "p2", "id": "post_2", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_posts(posts))

    def test_list_of_dicts(self):
        posts = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_posts(posts))

    def test_mixed_post_types(self):
        posts = [
            "p0",
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_posts(posts))

    def test_unknown_keys_in_post(self):
        posts = [
            {"name": "p0", "id": "post_0", "kwargs": {}, "foo": "bar", "hello": "world"},
            {"name": "p1", "id": "post_1", "kwargs": {}, "p": "np"},
        ]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_posts(posts))

    def test_only_name_in_post(self):
        posts = [
            {"name": "p0"},
            {"name": "p1"},
        ]
        expected = [
            {"name": "p0", "id": "post_0", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {}},
        ]
        self.assertListEqual(expected, config.normalize_posts(posts))

    def test_given_keys_in_post(self):
        posts = [
            {"name": "p0", "id": 'custom_id'},
            {"name": "p1", "kwargs":{'foo':'bar'}},
        ]
        expected = [
            {"name": "p0", "id": "custom_id", "kwargs": {}},
            {"name": "p1", "id": "post_1", "kwargs": {'foo':'bar'}},
        ]
        self.assertListEqual(expected, config.normalize_posts(posts))

    def test_name_missing(self):
        posts = [
            {"id": "post_0"}
        ]
        with self.assertRaises(KeyError):
            config.normalize_posts(posts)

class TestDuplicateIdFilter(unittest.TestCase):
    def test_duplicates(self):
        tasks = [
            {"id": "t0"}, {'id': "t1"}, {'id': 't0'}, {'id': 't4'}
        ]
        expected = [
            {"id": "t0"}, {'id': "t1"}, {'id': 't4'}
        ]
        self.assertListEqual(expected, config.filter_duplicate_ids(tasks))

    def test_no_duplicates(self):
        tasks = [
            {"id": "t0"}, {'id': "t1"}, {'id': 't4'}
        ]
        expected = [
            {"id": "t0"}, {'id': "t1"}, {'id': 't4'}
        ]
        self.assertListEqual(expected, config.filter_duplicate_ids(tasks))
