########
Metadata
########

Data is passed between tasks over a shared metadata pool.

*****
Write
*****

Direct write access to a pool is restricted. All metadata is expected to pass
through some manager that writes to the pool. For the manager to insert the
data, just return some dictionary in the format ``{field: value}``.

****
Read
****

To read from the pool, initialize a ``VariablePool`` instance from
``mediama.metadata``. Reading from the pool can be done using one of the
following methods.

For example suppose we want to access the "series" metadata.

.. code-block:: python

    from mediama.metadata import VariablePool

    varpool = VariablePool()

    series = varpool.get("series")
    series = varpool["series"]
