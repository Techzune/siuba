"""
Note: this test file was heavily influenced by its dbplyr counterpart.

https://github.com/tidyverse/dbplyr/blob/master/tests/testthat/test-verb-filter.R
"""
    
from siuba import _, filter, group_by, arrange
from siuba.dply.vector import row_number, desc
import pandas as pd

import pytest

from .helpers import assert_equal_query, data_frame, backend_notimpl, backend_sql

DATA = pd.DataFrame({
    "x": [1,1,1,1],
    "y": [1,1,2,2],
    "z": [1,2,1,2]
    })


def test_filter_basic(backend):
    df = data_frame(x = [1,2,3,4,5], y = [5,4,3,2,1])
    dfs = backend.load_df(df)

    assert_equal_query(dfs, filter(_.x > 3), df[lambda _: _.x > 3])


@backend_sql("TODO: pandas - grouped col should be first after mutate")
@backend_notimpl("sqlite")
def test_filter_via_group_by(backend):
    df = data_frame(
            x = range(1, 11),
            g = [1]*5 + [2]*5
            )

    dfs = backend.load_df(df)

    assert_equal_query(
            dfs,
            group_by(_.g) >> filter(row_number(_) < 3),
            data_frame(g = [1,1,2,2], x = [1,2,6,7])
            )


@backend_sql("TODO: pandas - grouped col should be first after mutate")
@backend_notimpl("sqlite")
def test_filter_via_group_by_agg(backend):
    dfs = backend.load_df(x = range(1,11), g = [1]*5 + [2]*5)

    assert_equal_query(
            dfs,
            group_by(_.g) >> filter(_.x > _.x.mean()),
            data_frame(g = [1, 1, 2, 2], x = [4, 5, 9, 10])
            )

@backend_sql("TODO: pandas - implement arrange over group by")
@backend_notimpl("sqlite")
def test_filter_via_group_by_arrange(backend):
    dfs = backend.load_df(x = [3,2,1] + [2,3,4], g = [1]*3 + [2]*3)

    assert_equal_query(
            dfs,
            group_by(_.g) >> arrange(_.x) >> filter(_.x.cumsum() > 3),
            data_frame(g = [1, 2, 2], x = [3, 3, 4])
            )

@backend_sql("TODO: pandas - implement arrange over group by")
@backend_notimpl("sqlite")
def test_filter_via_group_by_desc_arrange(backend):
    dfs = backend.load_df(x = [3,2,1] + [2,3,4], g = [1]*3 + [2]*3)

    assert_equal_query(
            dfs,
            group_by(_.g) >> arrange(desc(_.x)) >> filter(_.x.cumsum() > 3),
            data_frame(g = [1, 1, 2, 2, 2], x = [2, 1, 4, 3, 2])
            )

