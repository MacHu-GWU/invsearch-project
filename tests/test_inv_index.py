# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from invsearch.inv_index import InvIndex

data_list = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Cathy"},
    {"id": 4, "name": "Bob"},
]
data_dict = {
    "id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Cathy", "Bob"]
}


class InvIndexTestBase(object):
    def test_implementation(self):
        assert self.ii._data == {
            0: {"id": 1, "name": "Alice"},
            1: {"id": 2, "name": "Bob"},
            2: {"id": 3, "name": "Cathy"},
            3: {"id": 4, "name": "Bob"},
        }
        assert self.ii._columns == ["id", "name"]
        assert self.ii._pk_columns == {"id", }
        assert self.ii._index == {
            "id": {
                1: 0,
                2: 1,
                3: 2,
                4: 3,
            },
            "name": {
                "Cathy": {2, },
                "Bob": {1, 3},
                "Alice": {0, },
            },
        }

    def test_find(self):
        results = self.ii.find(filters=dict(id=1))
        assert len(results) == 1
        assert results[0]["id"] == 1

        results = self.ii.find(filters=dict(name="Alice"))
        assert len(results) == 1
        assert results[0]["id"] == 1

        results = self.ii.find(filters=dict(name="Bob"))
        assert len(results) == 2

        with raises(ValueError):
            self.ii.find(filters=dict(name="David"))

        with raises(ValueError):
            self.ii.find(filters=dict(age=25))

    def test_find_one(self):
        row = self.ii.find_one(filters=dict(id=1))
        assert row["id"] == 1

        row = self.ii.find_one(filters=dict(name="Alice"))
        assert row["name"] == "Alice"

        with raises(ValueError):
            self.ii.find_one(filters=dict(id=0))

        with raises(ValueError):
            self.ii.find_one(filters=dict(name="David"))

        with raises(ValueError):
            self.ii.find_one(filters=dict(name="Bob"))


class TestInvIndexFromDataList(InvIndexTestBase):
    ii = InvIndex(data=data_list)


class TestInvIndexFromDataDict(InvIndexTestBase):
    ii = InvIndex(data=data_dict)


def test_complex_init():
    data_list = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 4, "name": "Bob", "age": None},
        {"id": 5, "name": "David", "gender": "Male"},
    ]
    ii = InvIndex(data=data_list)
    assert ii._pk_columns == {"id", }
    assert ii._columns == ["age", "gender", "id", "name"]

    assert ii.find_one(filters=dict(age=25))["id"] == 2
    assert ii.find_one(filters=dict(age=None))["id"] == 4
    assert ii.find_one(filters=dict(gender="Male"))["id"] == 5


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
