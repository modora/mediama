#######
Config
#######

.. contents::
   :depth: 3

A configuration profile is the typically the way settings
are passed into the mediama engine. The following formats are supported:

- .json
- .py

If the config specified is a .py file, then the file module must have some
top-level variable named ``config`` of instance ``dict``. See
::ref:`_example_py_config` for a sample config.

By default, if no configuration file is specified, the engine will attempt to
discover a config in the following locations in the following order

1. user_config
2. system_config
3. built_in_config

.. csv-table::
   :header: "Folder", "Windows", "Linux"

   "User", "%PROGRAMDATA%/mediama/", "$HOME/.config/mediama/"
    "System", "%APPDATA%/mediama/", "/etc/xdg/mediama/"

The built-in config uses these settings:

.. The literalinclude directive takes a path relative to the source directory,
   denoted by "/"

.. literalinclude:: /../../mediama/default_config.json

********
Settings
********

name
====

The name of the profile. This isn't used for anything aside for logging
purposes.

Example
-------

.. code-block:: json

   {
        "name": "profile name"
   }

pres
====

This setting is short for preprocessors. This setting expects a list of task
settings. Task settings can either be specified as a set of key-value pairs or
a string representing the name of the task to run. The order in which tasks are
specified represent the order in which they will be executed.

If specified using key-value pairs, then there must exist some pair,
``"name": "some_name"``. Any unrecongnized task settings will be silently
ignored.

If specified using a string, then all other settings will interpreted as
whatever the program defaults to.

Example
-------

.. code-block:: json

   {
        "pres": [
            {"name": "pre_process_0", "kwargs":{"arg0": 2}},
            "pre_process_1",
            {"name": "pre_process_2", "kwargs":{"arg0": 2}, "id": "sample"}
        ]
   }

sources
=======

This setting is short for preprocessors. This setting expects a list of task
settings. Task settings can either be specified as a set of key-value pairs or
a string representing the name of the task to run. The order in which tasks are
specified represent their metadata priority. Tasks at the beginning of the list
have greater metadata priority than tasks lower on the list.

If specified using key-value pairs, then there must exist some pair,
``"name": "some_name"``. Any unrecongnized task settings will be silently
ignored.

If specified using a string, then all other settings will interpreted as
whatever the program defaults to.

Example
-------

.. code-block:: json

   {
        "pres": [
            {"name": "source_0", "kwargs":{"arg0": 2}},
            "source_1",
            {"name": "source_2", "kwargs":{"arg0": 2}, "id": "sample"}
        ]
   }

posts
=====

This setting is short for postprocessors. This setting expects a list of task
settings. Task settings can either be specified as a set of key-value pairs or
a string representing the name of the task to run. The order in which tasks are
specified represent the order in which they will be executed.

If specified using key-value pairs, then there must exist some pair,
``"name": "some_name"``. Any unrecongnized task settings will be silently
ignored.

If specified using a string, then all other settings will interpreted as
whatever the program defaults to.

Example
-------

.. code-block:: json

   {
        "pres": [
            {"name": "post_process_0", "kwargs":{"arg0": 2}},
            "post_process_1",
            {"name": "post_process_2", "kwargs":{"arg0": 2}, "id": "sample"}
        ]
   }

key_mappings
============

The metadata storage prioritizes keys in the following manner

1. posts (last-to-first)
2. sources (first-to-last)
3. pres (last-to-first)

In some instances, you may want the metadata of specific tasks to take higher
precedence. This setting allows you to remap the precedence of specific keys
using process ids. All unmapped ids will be placed at the bottom of the
priorization stack using the default process priorization.

1. user-mapped priorization
2. unspecified_posts
3. unspecified_sources
4. unspecified_pres

Key mappings are written in the form ``key: [id_0, ..., id_N]`` where each id
is some regular expression

Example
-------
Consider the following config and suppose each task returns the keys ``key_0``,
``key_1``, and `key_3`. Note that the regular expression in ``key_2`` means
any id that contains a string "pre\_" followed by one or more characters.

.. code-block:: json

   {
        "name": "example key_mappings",
        "pres": ["pre_0", "pre_1"],
        "sources": ["src_0", "src_1"],
        "posts": ["post_0", "post_1"],
        "key_mappings": {
            "key_0": ["pre_1", "src_1"],
            "key_2": ["pre\_.+"]
        }
   }

The priority mapping for each key is

.. csv-table::
   :header: priority, key_0, key_1, key_2

   1, post_1, pre_1, pre_1
   2, post_0, src_1, pre_0
   3, src_0, post_0, post_1
   4, src_1, post_1, post_0
   5, pre_1, src_0, src_0
   6, pre_0, pre_0, src1

aliases
=======
Some sources may use different key names for metadata. For instance, the
OreGairu series is known by

- My Youth Romantic Comedy Is Wrong, As I Expected
- やはり俺の青春ラブコメはまちがっている
- My Teen Romantic Comedy SNAFU
- SNAFU
- OreGairu
- 俺ガイル
- Hamachi
- はまち

This setting is used in the aggregation and the disambiugation steps. This
setting remaps a list of alias keys to some primary name.


Example
-------
Using the previous example of OreGairu, suppose two sources are used, each of
which return the data shown below.

.. code-block:: python

   # src_0
   {
        "name": やはり俺の青春ラブコメはまちがっている,
        "title": "My Youth Romantic Comedy Is Wrong, As I Expected",
        "alternate_title": [
            "My Teen Romantic Comedy SNAFU",
            "SNAFU",
            "OreGairu"
        ]
   }

.. code-block::

   # src_1
   {
        "name": "OreGairu"
   }

Without an alias, these two results are interpreted by the aggregator as
different. Additionally, if the files are named by an alternate title, the
disambiugator will be unable to determine a match. The following configuration
should correct these issues

.. code-block:: json

   {
        "aliases": {
            "name": ["title", "name", "title_jp", "alternate_title"]
        }
   }

log
===

This setting configures the built in logger. Internally, this setting executes
the built-in logging function `logging.config.dictConfig <https://docs.python.org/3.8/library/logging.config.html#logging-config-dictschema>`__.
The logging settings shown below are using the `StackOverflow example <// settings taken from https://stackoverflow.com/a/7507842>`__.

Example
-------
.. code-block:: json

    {
        "log": {
            "version": 1,
            "disable_existing_loggers": true,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "level": "INFO",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": "WARNING",
                    "propagate": false
                },
                "my.packg": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": false
                },
                "__main__": {
                    "handlers": ["default"],
                    "level": "DEBUG",
                    "propagate": false
            }
        }
    }

cache
=====

By default, mediama enables a cache for the python requests package. The
avaliable settings for the cache are

.. csv-table::
   :header: setting, type, default

   path, str, "cache"

The path can either be either a filename or a directory within either a
relative path or an absolute. Relative paths are taken with respect to the user
data directory.

To disable the cache, specify a null value for the cache: ``null``, ``{}``, 0

Example
-------

The following example changes the cache file location

.. code-block:: json

   {
        "cache": {
            "path": "/tmp/cache"
        }
   }

This config will disable the cache

.. code-block:: json

   {
        "cache": {}
   }

prompt
======

Sometimes, the program is unable to automatically disambiugate the series.
Should this be the case, this setting determines whether the user will be
prompted or not. By default, this value is True.

Example
-------

.. code-block:: json

   {
        "prompt": false
   }

timeout
=======

Sets the maximum amount of time in seconds each source API is allowed to take.
By default, this value is 180

Example
-------

This example changes maximum execution time to 5 minutes

.. code-block:: json

   {
        "timeout": 300
   }

*************
Task Settings
*************

Task settings are used by the preprocessor, source APIs, and the postprocessor.
Each setting have the following signature

.. code-block:: json

   {
        "name": "task name",
        "kwargs": {"kw_0": "value_0", "kw_1": "value_1"},
        "id": "custom id"
   }

The only required setting is the task name. The default values for the other
settings are listed below. For the ``id`` setting, the process is either
``pre``, ``src``, or ``post`` and the processIndex is the indice the setting is
within the process list.

.. csv-table::
   :header: setting, type, default

   kwargs, dict, {}
   id, str, ${process}_${taskName}_${processIndex}

.. _example_py_config:

*********************
Example Python Config
*********************

.. code-block:: python

   from pathlib import Path

   name = f"Path(__file__).name"
   pres, sources, posts = [], [], []
   limit = 10

   config = {
       "name": name,
       "pres": pres,
       "sources": sources,
       "posts": posts,
       "limit": limit
   }
