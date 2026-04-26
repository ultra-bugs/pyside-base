#                  M"""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *
"""Unit tests for SharedCollection — no QApplication required."""

import threading

import pytest
from PySide6.QtCore import QCoreApplication

from core.SharedCollection import SharedCollection


@pytest.fixture(scope='module')
def qapp():
    app = QCoreApplication.instance() or QCoreApplication([])
    return app


@pytest.fixture
def col(qapp):
    return SharedCollection()


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------


class TestMutation:
    def testAdd(self, col):
        col.add(1).add(2)
        assert col.toList() == [1, 2]

    def testAddMany(self, col):
        col.addMany([10, 20, 30])
        assert 10 in col
        assert len(col) == 3

    def testRemove(self, col):
        col.add('a').add('b').add('a')
        col.remove('a')
        assert col.toList() == ['b', 'a']

    def testRemoveMissing(self, col):
        col.add(1)
        col.remove(999)  # must not raise
        assert col.toList() == [1]

    def testRemoveWhere(self, col):
        col.addMany([1, 2, 3, 4, 5])
        col.removeWhere(lambda x: x % 2 == 0)
        assert col.toList() == [1, 3, 5]

    def testUpdate(self, col):
        data = [{'v': 1}, {'v': 2}, {'v': 3}]
        col.replace(data)
        col.update(lambda x: x['v'] == 2, lambda x: x.update({'v': 99}))
        assert col.first(lambda x: x['v'] == 99) is not None

    def testReplace(self, col):
        col.add(1).add(2)
        col.replace([7, 8, 9])
        assert col.toList() == [7, 8, 9]

    def testClear(self, col):
        col.add(1).add(2)
        col.clear()
        assert len(col) == 0

    def testFluentChaining(self, col):
        result = col.add(1).add(2).add(3)
        assert result is col
        assert len(col) == 3


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


class TestQuery:
    def testWhere(self, col):
        col.addMany([1, 2, 3, 4])
        assert col.where(lambda x: x > 2) == [3, 4]

    def testSelect(self, col):
        col.addMany([1, 2, 3])
        assert col.select(lambda x: x * 10) == [10, 20, 30]

    def testFirst(self, col):
        col.addMany([5, 3, 8])
        assert col.first() == 5
        assert col.first(lambda x: x > 4) == 5
        assert col.first(lambda x: x > 100) is None
        assert col.first(lambda x: x > 100, default=-1) == -1

    def testLast(self, col):
        col.addMany([5, 3, 8])
        assert col.last() == 8
        assert col.last(lambda x: x < 8) == 3

    def testAny(self, col):
        assert col.any() is False
        col.add(1)
        assert col.any() is True
        assert col.any(lambda x: x == 1) is True
        assert col.any(lambda x: x == 99) is False

    def testAll(self, col):
        col.addMany([2, 4, 6])
        assert col.all(lambda x: x % 2 == 0) is True
        assert col.all(lambda x: x > 3) is False

    def testCount(self, col):
        col.addMany([1, 2, 3, 4])
        assert col.count() == 4
        assert col.count(lambda x: x > 2) == 2

    def testGroupBy(self, col):
        col.addMany([1, 2, 3, 4, 5])
        groups = col.groupBy(lambda x: 'even' if x % 2 == 0 else 'odd')
        assert sorted(groups['even']) == [2, 4]
        assert sorted(groups['odd']) == [1, 3, 5]

    def testOrderBy(self, col):
        col.addMany([3, 1, 2])
        assert col.orderBy(lambda x: x) == [1, 2, 3]
        assert col.orderBy(lambda x: x, reverse=True) == [3, 2, 1]

    def testDistinct(self, col):
        col.addMany([1, 2, 1, 3, 2])
        assert col.distinct() == [1, 2, 3]

    def testDistinctByKey(self, col):
        items = [{'id': 1, 'v': 'a'}, {'id': 2, 'v': 'b'}, {'id': 1, 'v': 'c'}]
        col.replace(items)
        d = col.distinct(keyFn=lambda x: x['id'])
        assert len(d) == 2
        assert d[0]['id'] == 1
        assert d[1]['id'] == 2

    def testToList(self, col):
        col.addMany([10, 20])
        lst = col.toList()
        assert lst == [10, 20]
        lst.append(99)  # mutation of snapshot must NOT affect collection
        assert col.count() == 2


# ---------------------------------------------------------------------------
# Dunder helpers
# ---------------------------------------------------------------------------


class TestDunder:
    def testLen(self, col):
        assert len(col) == 0
        col.add(1)
        assert len(col) == 1

    def testContains(self, col):
        col.add('hello')
        assert 'hello' in col
        assert 'world' not in col

    def testIter(self, col):
        col.addMany([10, 20, 30])
        assert list(col) == [10, 20, 30]

    def testRepr(self, col):
        col.add(42)
        assert '42' in repr(col)


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def testConcurrentAdd(self, qapp):
        col: SharedCollection = SharedCollection()
        threadCount = 10
        itemsPerThread = 100
        threads = [threading.Thread(target=lambda: [col.add(i) for i in range(itemsPerThread)]) for _ in range(threadCount)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert col.count() == threadCount * itemsPerThread

    def testConcurrentAddRemove(self, qapp):
        col: SharedCollection = SharedCollection()
        col.addMany(list(range(100)))
        errors = []
        def worker():
            try:
                for i in range(10):
                    col.add(i)
                    col.removeWhere(lambda x: x < 0)  # safe no-op
                    _ = col.toList()
            except Exception as e:
                errors.append(e)
        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == [], f'Thread errors: {errors}'
