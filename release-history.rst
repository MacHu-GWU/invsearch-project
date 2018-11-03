.. _release_history:

Release and Version History
==============================================================================


0.0.3 (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.0.2 (2018-11-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Features and Improvements**

- allow unhashable value in document. but fields with unhashable value are not indexed.
- add ``InvIndex.by_id(field=value)`` utility method. always assumes using one of primary_key field.
- add ``InvIndex.slow_find()`` method.
- use ``sentinels.NOTHING`` to distinguish not exists field from None value.


0.0.1 (2018-10-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- First release
- Implement inv search engine.
- Benchmark tested, beat in-memory sqlite.