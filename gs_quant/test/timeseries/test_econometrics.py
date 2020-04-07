"""
Copyright 2018 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from math import isclose

import pytest
from pandas import Timestamp
from pandas.util.testing import assert_series_equal

from gs_quant.timeseries import *


def test_returns():
    dates = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
        date(2019, 1, 6),
    ]

    x = pd.Series([])
    assert_series_equal(x, returns(x))

    x = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=dates)

    result = returns(x)
    expected = pd.Series([np.nan, 0.01, 0.02, -0.02, 0.0, 0.02], index=dates)
    assert_series_equal(result, expected, obj="Simple returns default")

    result = returns(x, 1, Returns.SIMPLE)
    expected = pd.Series([np.nan, 0.01, 0.02, -0.02, 0.0, 0.02], index=dates)
    assert_series_equal(result, expected, obj="Simple returns", check_less_precise=True)

    result = returns(x, 2, Returns.SIMPLE)
    expected = pd.Series([np.nan, np.nan, 0.0302, -0.0004, -0.0200, 0.0200], index=dates)
    assert_series_equal(result, expected, obj="Simple returns", check_less_precise=True)

    result = returns(x, 1, Returns.LOGARITHMIC)
    expected = pd.Series([np.nan, 0.009950, 0.019803, -0.020203, 0.0, 0.019803], index=dates)
    assert_series_equal(result, expected, obj="Logarithmic returns", check_less_precise=True)

    result = returns(x, 2, Returns.LOGARITHMIC)
    expected = pd.Series([np.nan, np.nan, 0.029753, -0.0004, -0.020203, 0.019803], index=dates)
    assert_series_equal(result, expected, obj="Logarithmic returns", check_less_precise=True)

    with pytest.raises(MqValueError):
        returns(x, 1, "None")


def test_prices():
    dates = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
        date(2019, 1, 6),
    ]

    r = pd.Series([])
    assert_series_equal(r, prices(r))

    r = pd.Series([np.nan, 0.01, 0.02, -0.02, 0.0, 0.02], index=dates)

    result = prices(r)
    expected = pd.Series([1.0, 1.01, 1.0302, 1.009596, 1.009596, 1.02978792], index=dates)
    assert_series_equal(result, expected, obj="Simple price series default")

    result = prices(r, 100)
    expected = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=dates)
    assert_series_equal(result, expected, obj="Simple price series default")

    result = prices(r, 100, Returns.SIMPLE)
    expected = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=dates)
    assert_series_equal(result, expected, obj="Simple price series", check_less_precise=True)

    r = pd.Series([np.nan, 0.009950, 0.019803, -0.020203, 0.0, 0.019803], index=dates)

    result = prices(r, 100, Returns.LOGARITHMIC)
    expected = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=dates)
    assert_series_equal(result, expected, obj="Logarithmic prices series", check_less_precise=True)

    with pytest.raises(MqValueError):
        prices(r, 1, "None")


def test_index():
    dates = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
        date(2019, 1, 6),
    ]

    x = pd.Series([200, 202, 201, 203, 202, 201], index=dates)

    result = index(x)
    expected = pd.Series([1.000, 1.010, 1.005, 1.015, 1.010, 1.005], index=dates)
    assert_series_equal(result, expected, obj="Index series")


def test_change():
    dates = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
        date(2019, 1, 6),
    ]

    x = pd.Series([200, 202, 201, 203, 202, 201.5], index=dates)

    result = change(x)
    expected = pd.Series([0.0, 2.0, 1.0, 3.0, 2.0, 1.5], index=dates)
    assert_series_equal(result, expected, obj="Change of series", check_series_type=False)


def test_annualize():
    daily_dates = [
        date(2019, 1, 1),
        date(2019, 1, 1),
        date(2019, 1, 1),
    ]

    daily_series = pd.Series([0.01, 0.02, -0.01], index=daily_dates)

    with pytest.raises(MqValueError):
        annualize(daily_series)

    daily_dates = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
        date(2019, 1, 6),
    ]

    daily_series = pd.Series([0.01, 0.02, -0.01, 0.03, 0, -0.01], index=daily_dates)

    result = annualize(daily_series)
    assert_series_equal(result, daily_series * math.sqrt(252), obj="Annualize daily")

    weekly_dates = [
        date(2019, 1, 1),
        date(2019, 1, 8),
        date(2019, 1, 15),
        date(2019, 1, 22),
        date(2019, 1, 29),
        date(2019, 2, 6),
    ]

    weekly_series = pd.Series([0.01, 0.02, -0.01, 0.03, 0, -0.01], index=weekly_dates)

    result = annualize(weekly_series)
    assert_series_equal(result, weekly_series * math.sqrt(52), obj="Annualize weekly")

    semi_monthly_dates = [
        date(2019, 1, 1),
        date(2019, 1, 15),
        date(2019, 2, 1),
        date(2019, 2, 15),
        date(2019, 3, 1),
        date(2019, 3, 15),
    ]

    semi_monthly_series = pd.Series([0.01, 0.02, -0.01, 0.03, 0, -0.01], index=semi_monthly_dates)

    result = annualize(semi_monthly_series)
    assert_series_equal(result, semi_monthly_series * math.sqrt(26), obj="Annualize semi-monthly")

    monthly_dates = [
        date(2019, 1, 1),
        date(2019, 2, 1),
        date(2019, 3, 1),
        date(2019, 4, 1),
        date(2019, 5, 1),
        date(2019, 6, 1),
    ]

    monthly_series = pd.Series([0.01, 0.02, -0.01, 0.03, 0, -0.01], index=monthly_dates)

    result = annualize(monthly_series)
    assert_series_equal(result, monthly_series * math.sqrt(12), obj="Annualize monthly")

    quarterly_dates = [
        date(2019, 1, 1),
        date(2019, 3, 1),
        date(2019, 6, 1),
        date(2019, 9, 1),
        date(2020, 1, 1),
        date(2020, 3, 1),
    ]

    quarterly_series = pd.Series([0.01, 0.02, -0.01, 0.03, 0, -0.01], index=quarterly_dates)

    result = annualize(quarterly_series)
    assert_series_equal(result, quarterly_series * math.sqrt(4), obj="Annualize quarterly")

    annual_dates = [
        date(2019, 1, 1),
        date(2020, 1, 1),
        date(2021, 1, 1),
        date(2022, 1, 1),
        date(2023, 1, 1),
        date(2024, 1, 1),
    ]

    annual_series = pd.Series([0.01, 0.02, -0.01, 0.03, 0, -0.01], index=annual_dates)

    result = annualize(annual_series)
    assert_series_equal(result, annual_series, obj="Annualize annually")

    invalid_dates = [
        date(2019, 1, 1),
        date(2019, 1, 3),
        date(2019, 1, 6),
        date(2019, 1, 9),
        date(2019, 1, 12),
        date(2019, 1, 13),
    ]

    invalid_series = pd.Series([0.01, 0.02, -0.01, 0.03, 0, -0.01], index=invalid_dates)

    with pytest.raises(MqValueError):
        annualize(invalid_series)


def test_volatility():
    x = pd.Series([])
    assert_series_equal(x, volatility(x))

    daily_dates = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
        date(2019, 1, 6),
    ]

    x = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=daily_dates)

    std = 0.016733200530681527
    vol = std * math.sqrt(252) * 100

    real_vol = volatility(x)

    assert (real_vol[-1] == vol)


def test_correlation():
    x = pd.Series([])
    assert_series_equal(pd.Series([]), correlation(x, x))
    assert_series_equal(pd.Series([]), correlation(x, x, 1))

    daily_dates = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
        date(2019, 1, 6),
    ]

    x = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=daily_dates)
    y = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=daily_dates)

    result = correlation(x, y)
    expected = pd.Series([np.nan, np.nan, 1.0, 1.0, 1.0, 1.0], index=daily_dates)

    assert_series_equal(result, expected, check_less_precise=True)

    y = pd.Series([100.0, 102.0, 104.0, 101.0, 100.95, 100.0], index=daily_dates)

    result = correlation(x, y)
    expected = pd.Series([np.nan, np.nan, -1.0, 0.969025, 0.969254, 0.706042], index=daily_dates)

    assert_series_equal(result, expected, check_less_precise=True)

    result = correlation(x, y, Window(2, 0))
    expected = pd.Series([np.nan, np.nan, -
                          1.0000000000000435, 1.0, 0.9999999999999994, -
                          1.0000000000000007], index=daily_dates)

    assert_series_equal(result, expected, check_less_precise=True)

    ret_x = returns(x)
    ret_y = returns(y)

    result = correlation(ret_x, ret_y, Window(2, 0), False)
    expected = pd.Series([np.nan, np.nan, -
                          1.0000000000000435, 1.0, 0.9999999999999994, -
                          1.0000000000000007], index=daily_dates)

    assert_series_equal(result, expected, check_less_precise=True)


def test_beta():
    x = pd.Series([])
    assert_series_equal(pd.Series([]), beta(x, x))
    assert_series_equal(pd.Series([]), beta(x, x, 1))

    daily_dates = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
        date(2019, 1, 6),
    ]

    x = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=daily_dates)
    y = pd.Series([100.0, 101, 103.02, 100.9596, 100.9596, 102.978792], index=daily_dates)

    result = beta(x, y)
    expected = pd.Series([np.nan, np.nan, np.nan, 1.0, 1.0, 1.0], index=daily_dates)

    assert_series_equal(result, expected, check_less_precise=True)

    y = pd.Series([100.0, 102.0, 104.0, 101.0, 100.95, 100.0], index=daily_dates)

    result = beta(x, y)
    expected = pd.Series([np.nan, np.nan, np.nan, 0.718146, 0.718919, 0.572201], index=daily_dates)

    assert_series_equal(result, expected, check_less_precise=True)

    result = beta(x, y, Window(2, 0))
    expected = pd.Series([np.nan, np.nan, np.nan, 0.8255252918287954,
                          0.7054398925453326, -2.24327163719368], index=daily_dates)

    assert_series_equal(result, expected, check_less_precise=True)

    ret_x = returns(x)
    ret_y = returns(y)

    result = beta(ret_x, ret_y, Window(2, 0), False)
    expected = pd.Series([np.nan, np.nan, np.nan, 0.8255252918287954,
                          0.7054398925453326, -2.24327163719368], index=daily_dates)

    assert_series_equal(result, expected, check_less_precise=True)


def test_max_drawdown():
    series = pd.Series([1, 5, 5, 4, 4, 1])

    basic_output = max_drawdown(series)
    assert_series_equal(basic_output, pd.Series([0.0, 0.0, 0.0, -0.2, -0.2, -0.8]), obj="Max drawdown")

    output_window = max_drawdown(series, Window(2, 0))
    assert_series_equal(output_window, pd.Series([0.0, 0.0, 0.0, -0.2, -0.2, -0.75]), obj="Max drawdown window")


def test_arima_fit():
    test_dict = {
                'High': {Timestamp('1989-01-03 00:00:00'): 3.575721263885498,
                         Timestamp('1989-01-04 00:00:00'): 3.5857372283935547,
                         Timestamp('1989-01-05 00:00:00'): 3.62580132484436,
                         Timestamp('1989-01-06 00:00:00'): 3.62580132484436,
                         Timestamp('1989-01-09 00:00:00'): 3.575721263885498,
                         Timestamp('1989-01-10 00:00:00'): 3.575721263885498,
                         Timestamp('1989-01-11 00:00:00'): 3.5657050609588623,
                         Timestamp('1989-01-12 00:00:00'): 3.635817289352417,
                         Timestamp('1989-01-13 00:00:00'): 3.615785360336304,
                         Timestamp('1989-01-16 00:00:00'): 3.615785360336304,
                         Timestamp('1989-01-17 00:00:00'): 3.635817289352417,
                         Timestamp('1989-01-18 00:00:00'): 3.675881385803223,
                         Timestamp('1989-01-19 00:00:00'): 3.695913553237915,
                         Timestamp('1989-01-20 00:00:00'): 3.665865421295166,
                         Timestamp('1989-01-23 00:00:00'): 3.675881385803223,
                         Timestamp('1989-01-24 00:00:00'): 3.675881385803223,
                         Timestamp('1989-01-25 00:00:00'): 3.695913553237915,
                         Timestamp('1989-01-26 00:00:00'): 3.7760417461395264,
                         Timestamp('1989-01-27 00:00:00'): 3.8561699390411377,
                         Timestamp('1989-01-30 00:00:00'): 3.8561699390411377},
                'Low': {Timestamp('1989-01-03 00:00:00'): 3.4855768680572514,
                        Timestamp('1989-01-04 00:00:00'): 3.5356571674346924,
                        Timestamp('1989-01-05 00:00:00'): 3.575721263885498,
                        Timestamp('1989-01-06 00:00:00'): 3.575721263885498,
                        Timestamp('1989-01-09 00:00:00'): 3.5356571674346924,
                        Timestamp('1989-01-10 00:00:00'): 3.5356571674346924,
                        Timestamp('1989-01-11 00:00:00'): 3.5256409645080566,
                        Timestamp('1989-01-12 00:00:00'): 3.5456731319427486,
                        Timestamp('1989-01-13 00:00:00'): 3.5857372283935547,
                        Timestamp('1989-01-16 00:00:00'): 3.5957531929016118,
                        Timestamp('1989-01-17 00:00:00'): 3.5857372283935547,
                        Timestamp('1989-01-18 00:00:00'): 3.615785360336304,
                        Timestamp('1989-01-19 00:00:00'): 3.655849456787109,
                        Timestamp('1989-01-20 00:00:00'): 3.62580132484436,
                        Timestamp('1989-01-23 00:00:00'): 3.615785360336304,
                        Timestamp('1989-01-24 00:00:00'): 3.615785360336304,
                        Timestamp('1989-01-25 00:00:00'): 3.655849456787109,
                        Timestamp('1989-01-26 00:00:00'): 3.665865421295166,
                        Timestamp('1989-01-27 00:00:00'): 3.79607367515564,
                        Timestamp('1989-01-30 00:00:00'): 3.786057710647583},
                'Close': {Timestamp('1989-01-03 00:00:00'): 3.5256409645080566,
                          Timestamp('1989-01-04 00:00:00'): 3.5857372283935547,
                          Timestamp('1989-01-05 00:00:00'): 3.575721263885498,
                          Timestamp('1989-01-06 00:00:00'): 3.575721263885498,
                          Timestamp('1989-01-09 00:00:00'): 3.575721263885498,
                          Timestamp('1989-01-10 00:00:00'): 3.5556890964508057,
                          Timestamp('1989-01-11 00:00:00'): 3.5556890964508057,
                          Timestamp('1989-01-12 00:00:00'): 3.605769157409668,
                          Timestamp('1989-01-13 00:00:00'): 3.605769157409668,
                          Timestamp('1989-01-16 00:00:00'): 3.5957531929016118,
                          Timestamp('1989-01-17 00:00:00'): 3.62580132484436,
                          Timestamp('1989-01-18 00:00:00'): 3.675881385803223,
                          Timestamp('1989-01-19 00:00:00'): 3.665865421295166,
                          Timestamp('1989-01-20 00:00:00'): 3.6458332538604736,
                          Timestamp('1989-01-23 00:00:00'): 3.62580132484436,
                          Timestamp('1989-01-24 00:00:00'): 3.675881385803223,
                          Timestamp('1989-01-25 00:00:00'): 3.675881385803223,
                          Timestamp('1989-01-26 00:00:00'): 3.756009578704834,
                          Timestamp('1989-01-27 00:00:00'): 3.79607367515564,
                          Timestamp('1989-01-30 00:00:00'): 3.846153736114502},
                    }

    test_df = pd.DataFrame(test_dict)
    arima = econometrics.arima()
    arima.fit(test_df, train_size=0.8, freq='B', q_vals=[0])
    transformed_test_df = arima.transform(test_df)

    for col in transformed_test_df.keys():
        count_nans = arima.best_params[col].p + arima.best_params[col].d
        assert(count_nans == transformed_test_df[col].isna().sum())

    # Test (1,2,0) Model
    diff_test_df_high = test_df['High'].diff().diff()
    assert(transformed_test_df['High'][3] == (arima.best_params['High'].const + diff_test_df_high[2] * arima.best_params['High'].ar_coef[0]))
    assert(transformed_test_df['High'][4] == (arima.best_params['High'].const + diff_test_df_high[3] * arima.best_params['High'].ar_coef[0]))
    assert(transformed_test_df['High'][-1] == (arima.best_params['High'].const + diff_test_df_high[-2] * arima.best_params['High'].ar_coef[0]))

    # Test (2,1,0) Model
    diff_test_df_low = test_df['Low'].diff()
    assert(isclose(transformed_test_df['Low'][3], (arima.best_params['Low'].const + diff_test_df_low[2] * arima.best_params['Low'].ar_coef[0] + diff_test_df_low[1] * arima.best_params['Low'].ar_coef[1]), abs_tol=1e-8))
    assert(isclose(transformed_test_df['Low'][4], (arima.best_params['Low'].const + diff_test_df_low[3] * arima.best_params['Low'].ar_coef[0] + diff_test_df_low[2] * arima.best_params['Low'].ar_coef[1]), abs_tol=1e-8))
    assert(isclose(transformed_test_df['Low'][-1], (arima.best_params['Low'].const + diff_test_df_low[-2] * arima.best_params['Low'].ar_coef[0] + diff_test_df_low[-3] * arima.best_params['Low'].ar_coef[1]), abs_tol=1e-8))

    # Test (1,2,0) Model
    diff_test_df_close = test_df['Close'].diff()[1:].diff()
    first_day = pd.Series([np.nan])
    first_day.index = [diff_test_df_close.index[0] - pd.DateOffset(days=1)]
    first_day.name = 'Close'
    diff_test_df_close = pd.concat([first_day, diff_test_df_close])
    diff_test_df_close.index.name = "Date"

    assert(transformed_test_df['Close'][4] == (arima.best_params['Close'].const + diff_test_df_close[3] * arima.best_params['Close'].ar_coef[0]))
    assert(transformed_test_df['Close'][5] == (arima.best_params['Close'].const + diff_test_df_close[4] * arima.best_params['Close'].ar_coef[0]))
    assert(transformed_test_df['Close'][-1] == (arima.best_params['Close'].const + diff_test_df_close[-2] * arima.best_params['Close'].ar_coef[0]))


if __name__ == "__main__":
    pytest.main(args=["test_econometrics.py"])
