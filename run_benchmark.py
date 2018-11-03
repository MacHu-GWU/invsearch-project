# -*- coding: utf-8 -*-

"""
Performance Test, compares:

1. in memory invsearch
2. intuitive in memory row scan
3. in memory sqlite query with index

Conclusion: invsearch is the best.
"""

import time
import random
import string
from sqlalchemy_mate import engine_creator
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy import select
from invsearch.inv_index import InvIndex


class InvIndexV2(object):
    """
    This implementation is intuitive but slow! DO NOT use this!

    :param _data: list of rows
    """

    def __init__(self, data):
        self._data = data

    def find(self, filters):
        results = list()
        for row in self._data:
            try:
                if sum([row.get(key) == value for key, value in filters.items()]) == len(filters):
                    results.append(row)
            except:
                pass
        return results


class InvIndexV3(object):
    def __init__(self, data):
        self.engine = engine_creator.create_sqlite()
        self.metadata = MetaData()
        self.table = Table(
            "user", self.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String, index=True),
        )
        self.metadata.create_all(self.engine)

        self.engine.execute(self.table.insert(), data)

    def find(self, filters):
        sql = select([self.table])
        crt_list = list()
        for key, value in filters.items():
            crt_list.append(self.table.columns[key] == value)
        sql = sql.where(*crt_list)
        results = self.engine.execute(sql).fetchall()
        return results


def rnd_str(length):
    return "".join([random.choice(string.lowercase) for _ in range(length)])


def run_benchmark():
    """
    Test Machine::

        MacOS Sierra V10.12.6

        Macbook Pro 13inch Early 2015
        2.9GHz inter Core i5
        16GB 1867MHz DDR3

    Performance::

        n_rows = 1000000, n_search = 100:
            v1: 0.00508400
        n_rows = 1000000, n_search = 1000:
            v1: 0.06388600
        n_rows = 1000000, n_search = 10000:
            v1: 0.70872300

        n_rows = 10000, n_search = 1000:
            v1: 0.00562300
        n_rows = 10000, n_search = 10000:
            v1: 0.05006100
        n_rows = 10000, n_search = 100000:
            v1: 0.51928800
    """
    params_grid = [
        (100, 10),
        (100, 100),
        (100, 1000),
        (1000, 100),
        (1000, 1000),
        # (1000, 10000),
    ]

    for n_rows, n_search in params_grid:
        data = [
            dict(id=i, name=rnd_str(3))
            for i in range(n_rows)
        ]
        ii1 = InvIndex(data=data)
        ii2 = InvIndexV2(data=data)
        ii3 = InvIndexV3(data=data)

        name_list = [random.choice(data)["name"] for _ in range(n_search)]

        st = time.clock()
        for name in name_list:
            results = ii1.find(name=name)
        elapse1 = time.clock() - st

        st = time.clock()
        for name in name_list:
            results = ii2.find(filters=dict(name=name))
        elapse2 = time.clock() - st

        st = time.clock()
        for name in name_list:
            results = ii3.find(filters=dict(name=name))
        elapse3 = time.clock() - st

        print("n_rows = %s, n_search = %s:" % (n_rows, n_search))
        print("    invsearch: %.8f" % elapse1)
        print("    brute force: %.8f" % elapse2)
        print("    sqlite: %.8f" % elapse3)


if __name__ == "__main__":
    run_benchmark()
