# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from sentinels import NOTHING
from invsearch.inv_index import InvIndex
from pprint import pprint

data_list = [
    {"id": 1, "name": "Alice", "friends": [2, 3]},
    {"id": 2, "name": "Bob", "age": 15, "friends": [1, 3]},
    {"id": 3, "name": "Cathy", "age": None, "friends": [1, 2]},
    {"id": 4, "name": "Bob", "age": None},
]
data_dict = {
    "id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Cathy", "Bob"],
    "age": [NOTHING, 15, None, None],
    "friends": [[2, 3], [1, 3], [1, 2], NOTHING]
}


class InvIndexTestBase(object):
    def test_implementation(self):
        assert self.ii._columns == ["age", "friends", "id", "name"]
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
            "age": {
                NOTHING: {0, },
                15: {1, },
                None: {2, 3},
            },
        }

    def test_find(self):
        results = self.ii.find(id=1)
        assert len(results) == 1
        assert results[0]["id"] == 1

        results = self.ii.find(name="Alice")
        assert len(results) == 1
        assert results[0]["id"] == 1

        results = self.ii.find(name="Bob")
        assert len(results) == 2

        with raises(ValueError):
            self.ii.find(name="David")

        with raises(ValueError):
            self.ii.find(age=2)

    def test_find_one(self):
        row = self.ii.find_one(id=1)
        assert row["id"] == 1

        row = self.ii.find_one(name="Alice")
        assert row["name"] == "Alice"

        with raises(ValueError):
            self.ii.find_one(id=0)

        with raises(ValueError):
            self.ii.find_one(name="David")

        with raises(ValueError):
            self.ii.find_one(name="Bob")

    def test_by_id(self):
        assert self.ii.by_id(id=1)["id"] == 1
        assert self.ii.by_id(id=2)["id"] == 2

        with raises(ValueError):
            self.ii.by_id(id=999)

    def test_slow_find(self):
        assert {dct["id"] for dct in self.ii.slow_find(name="Bob")} == {2, 4}
        assert {dct["id"] for dct in self.ii.slow_find(friends=[1, 2])} == {3, }


class TestInvIndexFromDataList(InvIndexTestBase):
    ii = InvIndex(data=data_list)

    def test_implementation_data_part(self):
        assert self.ii._data == {
            0: {"id": 1, "name": "Alice", "friends": [2, 3]},
            1: {"id": 2, "name": "Bob", "age": 15, "friends": [1, 3]},
            2: {"id": 3, "name": "Cathy", "age": None, "friends": [1, 2]},
            3: {"id": 4, "name": "Bob", "age": None},
        }


class TestInvIndexFromDataDict(InvIndexTestBase):
    ii = InvIndex(data=data_dict)

    def test_implementation_data_part(self):
        assert self.ii._data == {
            0: {"id": 1, "name": "Alice", "age": NOTHING, "friends": [2, 3]},
            1: {"id": 2, "name": "Bob", "age": 15, "friends": [1, 3]},
            2: {"id": 3, "name": "Cathy", "age": None, "friends": [1, 2]},
            3: {"id": 4, "name": "Bob", "age": None, "friends": NOTHING},
        }


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

    assert ii.find_one(age=25)["id"] == 2
    assert ii.find_one(age=None)["id"] == 4
    assert ii.find_one(gender="Male")["id"] == 5


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
