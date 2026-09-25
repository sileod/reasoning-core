## Level 0

**Example 1**

Prompt:

```
A forecaster issues probabilistic (0-1) forecasts, grouped into 3 bins by rounded forecast value; bins sharing a forecast value have been merged, so each bin carries a weight equal to the number of forecasts it contains. For each bin you are given its weight n, its mean forecast r, and the realized number k of positive outcomes. The bins (weight, mean forecast, positive outcomes) are:

Bin 1: weight 2, forecast 0/1, positives 1.
Bin 2: weight 2, forecast 1/3, positives 1.
Bin 3: weight 2, forecast 0/1, positives 0.

Compute the Murphy decomposition of the Brier score (mean squared error) into three components. Let N be the total weight, o = (sum of positives)/N the overall base rate, and for each bin o_j = k_j/n_j its observed frequency. Then calibration = (1/N)*sum_j n_j*(r_j - o_j)^2, resolution = (1/N)*sum_j n_j*(o_j - o)^2, and outcome uncertainty = o*(1-o). The total Brier score equals calibration + outcome uncertainty - resolution.

Give the three components each as a reduced fraction of the total Brier score, in the fixed order calibration, resolution, outcome uncertainty, separated by commas - for example 1/3, 2/5, 4/15.
```

Answer: 5/14, 3/14, 6/7

**Example 2**

Prompt:

```
A forecaster issues probabilistic (0-1) forecasts, grouped into 3 bins by rounded forecast value; bins sharing a forecast value have been merged, so each bin carries a weight equal to the number of forecasts it contains. For each bin you are given its weight n, its mean forecast r, and the realized number k of positive outcomes. The bins (weight, mean forecast, positive outcomes) are:

Bin 1: weight 2, forecast 2/3, positives 1.
Bin 2: weight 2, forecast 1/3, positives 2.
Bin 3: weight 2, forecast 2/3, positives 1.

Compute the Murphy decomposition of the Brier score (mean squared error) into three components. Let N be the total weight, o = (sum of positives)/N the overall base rate, and for each bin o_j = k_j/n_j its observed frequency. Then calibration = (1/N)*sum_j n_j*(r_j - o_j)^2, resolution = (1/N)*sum_j n_j*(o_j - o)^2, and outcome uncertainty = o*(1-o). The total Brier score equals calibration + outcome uncertainty - resolution.

Give the three components each as a reduced fraction of the total Brier score, in the fixed order calibration, resolution, outcome uncertainty, separated by commas - for example 1/3, 2/5, 4/15.
```

Answer: 1/2, 1/6, 2/3

## Level 2

**Example 1**

Prompt:

```
A forecaster issues probabilistic (0-1) forecasts, grouped into 5 bins by rounded forecast value; bins sharing a forecast value have been merged, so each bin carries a weight equal to the number of forecasts it contains. For each bin you are given its weight n, its mean forecast r, and the realized number k of positive outcomes. The bins (weight, mean forecast, positive outcomes) are:

Bin 1: weight 4, forecast 1/1, positives 2.
Bin 2: weight 2, forecast 2/5, positives 2.
Bin 3: weight 3, forecast 4/5, positives 2.
Bin 4: weight 2, forecast 1/1, positives 1.
Bin 5: weight 3, forecast 1/5, positives 2.

Compute the Murphy decomposition of the Brier score (mean squared error) into three components. Let N be the total weight, o = (sum of positives)/N the overall base rate, and for each bin o_j = k_j/n_j its observed frequency. Then calibration = (1/N)*sum_j n_j*(r_j - o_j)^2, resolution = (1/N)*sum_j n_j*(o_j - o)^2, and outcome uncertainty = o*(1-o). The total Brier score equals calibration + outcome uncertainty - resolution.

Give the three components each as a reduced fraction of the total Brier score, in the fixed order calibration, resolution, outcome uncertainty, separated by commas - for example 1/3, 2/5, 4/15.
```

Answer: 439/864, 25/378, 125/224

**Example 2**

Prompt:

```
A forecaster issues probabilistic (0-1) forecasts, grouped into 5 bins by rounded forecast value; bins sharing a forecast value have been merged, so each bin carries a weight equal to the number of forecasts it contains. For each bin you are given its weight n, its mean forecast r, and the realized number k of positive outcomes. The bins (weight, mean forecast, positive outcomes) are:

Bin 1: weight 2, forecast 2/5, positives 1.
Bin 2: weight 3, forecast 1/1, positives 0.
Bin 3: weight 3, forecast 2/5, positives 3.
Bin 4: weight 3, forecast 0/1, positives 2.
Bin 5: weight 3, forecast 4/5, positives 1.

Compute the Murphy decomposition of the Brier score (mean squared error) into three components. Let N be the total weight, o = (sum of positives)/N the overall base rate, and for each bin o_j = k_j/n_j its observed frequency. Then calibration = (1/N)*sum_j n_j*(r_j - o_j)^2, resolution = (1/N)*sum_j n_j*(o_j - o)^2, and outcome uncertainty = o*(1-o). The total Brier score equals calibration + outcome uncertainty - resolution.

Give the three components each as a reduced fraction of the total Brier score, in the fixed order calibration, resolution, outcome uncertainty, separated by commas - for example 1/3, 2/5, 4/15.
```

Answer: 83/108, 125/594, 175/396

## Level 5

**Example 1**

Prompt:

```
A forecaster issues probabilistic (0-1) forecasts, grouped into 8 bins by rounded forecast value; bins sharing a forecast value have been merged, so each bin carries a weight equal to the number of forecasts it contains. For each bin you are given its weight n, its mean forecast r, and the realized number k of positive outcomes. The bins (weight, mean forecast, positive outcomes) are:

Bin 1: weight 2, forecast 3/8, positives 2.
Bin 2: weight 7, forecast 1/1, positives 1.
Bin 3: weight 5, forecast 3/8, positives 4.
Bin 4: weight 6, forecast 3/4, positives 1.
Bin 5: weight 2, forecast 5/8, positives 2.
Bin 6: weight 3, forecast 1/2, positives 1.
Bin 7: weight 5, forecast 3/8, positives 0.
Bin 8: weight 5, forecast 1/8, positives 1.

Compute the Murphy decomposition of the Brier score (mean squared error) into three components. Let N be the total weight, o = (sum of positives)/N the overall base rate, and for each bin o_j = k_j/n_j its observed frequency. Then calibration = (1/N)*sum_j n_j*(r_j - o_j)^2, resolution = (1/N)*sum_j n_j*(o_j - o)^2, and outcome uncertainty = o*(1-o). The total Brier score equals calibration + outcome uncertainty - resolution.

Give the three components each as a reduced fraction of the total Brier score, in the fixed order calibration, resolution, outcome uncertainty, separated by commas - for example 1/3, 2/5, 4/15.
```

Answer: 22321/31185, 160/567, 5888/10395

**Example 2**

Prompt:

```
A forecaster issues probabilistic (0-1) forecasts, grouped into 8 bins by rounded forecast value; bins sharing a forecast value have been merged, so each bin carries a weight equal to the number of forecasts it contains. For each bin you are given its weight n, its mean forecast r, and the realized number k of positive outcomes. The bins (weight, mean forecast, positive outcomes) are:

Bin 1: weight 6, forecast 3/8, positives 3.
Bin 2: weight 6, forecast 7/8, positives 6.
Bin 3: weight 3, forecast 0/1, positives 3.
Bin 4: weight 3, forecast 5/8, positives 1.
Bin 5: weight 3, forecast 0/1, positives 0.
Bin 6: weight 4, forecast 3/4, positives 3.
Bin 7: weight 5, forecast 7/8, positives 5.
Bin 8: weight 3, forecast 1/8, positives 3.

Compute the Murphy decomposition of the Brier score (mean squared error) into three components. Let N be the total weight, o = (sum of positives)/N the overall base rate, and for each bin o_j = k_j/n_j its observed frequency. Then calibration = (1/N)*sum_j n_j*(r_j - o_j)^2, resolution = (1/N)*sum_j n_j*(o_j - o)^2, and outcome uncertainty = o*(1-o). The total Brier score equals calibration + outcome uncertainty - resolution.

Give the three components each as a reduced fraction of the total Brier score, in the fixed order calibration, resolution, outcome uncertainty, separated by commas - for example 1/3, 2/5, 4/15.
```

Answer: 1117/1677, 7664/18447, 4608/6149

