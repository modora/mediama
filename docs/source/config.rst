#######
Config
#######

A configuration profile is the typically the way settings
are passed into the mediama engine. The following formats are supported:

- .json
- .py

By default, if no configuration file is specified, the engine will attempt to
discover a config in the following order

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
settings.

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

This setting expects a list of task settings.

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
settings.

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

key_sources
===========

The metadata storage prioritizes keys in the following manner

1. posts (last-to-first)
2. sources (first-to-last)
3. pres (last-to-first)

In some instances, you may want specific tasks to take higher precedence. This
setting allows you to remap the precedence of specific keys using process ids.
All unmapped ids will be placed at the bottom of the priorization stack using
the default process priorization.

1. user-mapped priorization
2. unspecified_posts
3. unspecified_sources
4. unspecified_pres

Example
-------
Consider the following config and suppose each task returns the keys **key_0**
and **key_1**.

.. code-block:: json

   {
        "name": "example key_sources",
        "pres": ["pre_0", "pre_1"],
        "sources": ["src_0", "src_1"],
        "posts": ["post_0", "post_1"],
        "key_sources": {
            "key_0": ["pre_1", "src_1"]
        }
   }

The priority mapping for each key is

.. csv-table::
   :header: priority, key_0, key_1

   1, post_1, pre_1
   2, post_0, src_1
   3, src_0, post_0
   4, src_1, post_1
   5, pre_0, src_0
   6, pre_1, src_1

aliases
=======
TODO: Needs behvior definition

Some sources may use different key names for their metadata. This setting
remaps a list of keys to a standard, primary name.

This setting affects key_sources as well as the disambiugators during the
identification stage.


Example
-------
Consider a source that returns the keys **title** and **title_jp**.

.. code-block:: json

   {
        "aliases": {
            "title": ["title_jp"]
        }
   }

*************
Task Settings
*************

Task settings have the following signature

.. code-block:: json

   {
        "name": "task name",
        "kwargs": {"kw_0": "value_0", "kw_1": "value_1"},
        "id": "custom id"
   }

The only required setting is the task name. The default values for the other
settings are listed below. For the **id** setting, the process is either
**pre**, **src**, or **post** and the process_index is the indice the setting is
within the process list.

.. csv-table::
   :header: setting, type, default

   kwargs, dict, {}
   id, str, ${process}_${process_index}
