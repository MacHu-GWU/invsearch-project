# -*- coding: utf-8 -*-

"""
Inverse Index Search Engine.
"""

from six import iteritems
from sentinels import NOTHING


class InvIndex(object):
    """
    Inverse Index for inverse search.

    Variable definition:

    - ``data_row_list``: ``[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]``
    - ``data_index_row``: ``{0: {"id": 1, "name": "Alice"}, 1: {"id": 2, "name": "Bob"}}``
    - ``data_col_values``: ``{"id": [1, 2], "name": ["Alice", "Bob]}``
    """

    def __init__(self, data):
        self._data = dict()
        self._columns = list()
        self._pk_columns = set()
        self._unhashable_columns = set()
        self._index = dict()

        if isinstance(data, dict):
            self._init_from_dict(data)
        elif isinstance(data, (list, tuple)):
            self._init_from_list(data)
        else:  # pragma: no cover
            raise TypeError("unsupported data type!")

    def _init_from_dict(self, data):
        _data_col_values = data
        _data_ind_row = dict()

        _columns = list(data.keys())
        _columns.sort()

        for key, values in iteritems(data):
            for ind, value in enumerate(values):
                try:
                    _data_ind_row[ind][key] = value
                except:
                    _data_ind_row[ind] = {key: value}

        self._data = _data_ind_row
        self._columns = _columns
        self._init_get_pk_columns(_data_col_values, len(_data_ind_row))
        self._init_build_index(_data_col_values, self._pk_columns, self._unhashable_columns)

    def _init_from_list(self, data):
        _data_row_list = data
        _data_ind_row = dict()
        _data_col_values = dict()
        _columns = set()

        for ind, row in enumerate(data):
            _data_ind_row[ind] = row
            for key, value in row.items():
                _columns.add(key)
        _columns = list(_columns)
        _columns.sort()
        for row in _data_row_list:
            for c in _columns:
                try:
                    _data_col_values[c].append(row.get(c, NOTHING))
                except KeyError:
                    _data_col_values[c] = [row.get(c, NOTHING), ]

        self._data = _data_ind_row
        self._columns = _columns
        self._init_get_pk_columns(_data_col_values, len(_data_ind_row))
        self._init_build_index(_data_col_values, self._pk_columns, self._unhashable_columns)

    def _init_get_pk_columns(self, data_col_values, n_rows):
        _pk_columns = set()
        _unhashable_columns = set()
        for col, values in iteritems(data_col_values):
            try:
                if len(set(values)) == n_rows:
                    _pk_columns.add(col)
            except TypeError:
                _unhashable_columns.add(col)
        self._pk_columns = _pk_columns
        self._unhashable_columns = _unhashable_columns

    def _init_build_index(self, _data_col_values, pk_columns, unhashable_columns):
        _index = dict()
        for col, values in iteritems(_data_col_values):
            if col in pk_columns:
                for ind, value in enumerate(values):
                    try:
                        _index[col][value] = ind
                    except KeyError:
                        _index[col] = {value: ind}
            elif col in unhashable_columns:
                pass
            else:
                for ind, value in enumerate(values):
                    try:
                        dct_mapper = _index[col]
                        try:
                            dct_mapper[value].add(ind)
                        except KeyError:
                            dct_mapper[value] = {ind, }
                    except KeyError:
                        try:
                            _index[col] = {value: {ind, }}
                        except TypeError:
                            pass
        self._index = _index

    def find(self, filters):
        """
        Find documents.

        :return: list of dict
        """
        pk_columns = set.intersection(self._pk_columns, set(filters.keys()))
        if len(pk_columns):
            key = pk_columns.pop()
            return [self._data[self._index[key][filters[key]]], ]

        set_list = list()
        for key, value in filters.items():
            try:
                set_list.append(self._index[key][value])
            except KeyError:
                raise ValueError("no result match!")

        pk_set = set.intersection(*set_list)
        pk_list = list(pk_set)
        pk_list.sort()
        return [self._data[pk] for pk in pk_list]

    def find_one(self, filters):
        """
        Find one matching document.

        if no document or multi documents found, raise error
        """

        pk_columns = set.intersection(self._pk_columns, set(filters.keys()))
        if len(pk_columns):
            key = pk_columns.pop()
            try:
                return self._data[self._index[key][filters[key]]]
            except KeyError:
                raise ValueError("no result match!")

        set_list = list()
        for key, value in filters.items():
            try:
                set_list.append(self._index[key][value])
            except KeyError:
                raise ValueError("no result match!")

        pk_set = set.intersection(*set_list)
        if len(pk_set) == 1:
            return self._data[pk_set.pop()]
        elif len(pk_set) == 0:  # pragma: no cover
            raise ValueError("no result match!")
        else:
            raise ValueError("multiple matching results!")

    def by_id(self, **filters):
        """
        By primary_key columns and its value.

        Example::

            >>> by_id(id=1)
            {"id: 1, "name": "Alice"}
        """
        try:
            key, value = filters.popitem()
            return self._data[self._index[key][value]]
        except KeyError:
            raise ValueError

    def slow_find(self, **filters):
        """
        A slow finding algorithm. brute iterate and compare.
        """
        results = list()
        for dct in self._data.values():
            flag = True
            for key, value in filters.items():
                if not dct.get(key, NOTHING) == value:
                    flag = False
                    break
            if flag:
                results.append(dct)
        return results
