# -*- coding: utf-8 -*-

"""
Inverse Index Search Engine.
"""

from six import iteritems


class InvIndex(object):
    """
    Inverse Index for inverse search.

    Variable definition:

    - ``data_row_list``: ``[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]``
    - ``data_index_row``: ``{0: {"id": 1, "name": "Alice"}, 1: {"id": 2, "name": "Bob"}}``
    - ``data_col_values``: ``{"id": [1, 2], "name": ["Alice", "Bob]}``
    """

    def __init__(self, data):
        """
        """
        self._data = dict()
        self._columns = list()
        self._pk_columns = set()
        self._index = dict()

        if isinstance(data, dict):
            self._init_from_dict(data)
        elif isinstance(data, (list, tuple)):
            self._init_from_list(data)
        else: # pragma: no cover
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
        self._init_build_index(_data_ind_row, self._pk_columns)

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
                    _data_col_values[c].append(row.get(c))
                except KeyError:
                    _data_col_values[c] = [row.get(c), ]

        self._data = _data_ind_row
        self._columns = _columns
        self._init_get_pk_columns(_data_col_values, len(_data_ind_row))
        self._init_build_index(_data_ind_row, self._pk_columns)

    def _init_get_pk_columns(self, data_col_values, n_rows):
        _pk_columns = set()
        for col, values in iteritems(data_col_values):
            if len(set(values)) == n_rows:
                _pk_columns.add(col)
        self._pk_columns = _pk_columns

    def _init_build_index(self, data_ind_row, pk_columns):
        _index = dict()
        for ind, row in iteritems(data_ind_row):
            for key, value in row.items():
                if key in pk_columns:
                    try:
                        _index[key][value] = ind
                    except KeyError:
                        _index[key] = {value: ind}
                else:
                    try:
                        dct_mapper = _index[key]
                        try:
                            dct_mapper[value].add(ind)
                        except KeyError:
                            dct_mapper[value] = {ind, }
                    except KeyError:
                        _index[key] = {value: {ind, }}
        self._index = _index

    def find(self, filters):
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
