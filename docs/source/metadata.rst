########
Metadata
########

Data is passed between tasks over a shared metadata pool. The data is encoded
in the format ``(id_, field, value)``.

*****
Write
*****

Direct write access to a pool is restricted. All metadata is expected to pass
through some manager that writes to the pool. For the manager to insert the
data, just return some dictionary in the format ``{field: value}``. The id for
the task will be appended by the manager

****
Read
****

To read from the pool, initialize a ``VariablePool`` instance from
``mediama.metadata``. Reading from the pool can be done using one of the
following methods.

If no key is specified in the get method, then it will return the value whose
associated id has the greatest priority. If no id exists, it will throw a
``KeyError``

.. code-block:: python

    from mediama.metadata import VariablePool

    varpool = VariablePool()

    # get default
    varpool["series"]
    varpool.get("series")
    varpool.get("series", id_=None)

    # get value of series associated with id
    varpool.get("series", id_="id_0")

    # get all keys sorted by priority
    varpool.get_all("series")  # {"id_0": value_0, "id_1": value_1}
