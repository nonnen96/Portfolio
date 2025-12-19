# Perfume Time Series Analysis

**Forecasting monthly perfume values using ARIMA models**

## Description

This project analyzes a monthly time series of perfume values and builds ARIMA models to forecast future trends. The main objectives are:

- Load and preprocess the dataset.  
- Examine stationarity and apply transformations (differencing).  
- Identify the best ARIMA model using AIC and BIC criteria.  
- Check model residuals for whiteness and normality.  
- Forecast future values with confidence intervals.

The analysis is conducted in R, using packages such as `forecast`, `tseries`, `urca`, and `ggplot2`.

## Data

- **Source:** CSV file `valeurs_mensuelles_parfum.csv`  
- **Structure:** First two columns represent `DATE` and `VALUES`.  
- **Preprocessing:** Initial metadata rows are skipped, and dates are converted to `Date` objects.  
- **Transformation:** Log transformation and differencing are applied to achieve stationarity.

## Methodology

1. **Exploratory Analysis**  
   - Time series plots.  
   - Autocorrelation (ACF) and partial autocorrelation (PACF) analysis.  

2. **Stationarity Check**  
   - Augmented Dickey-Fuller (ADF) and Phillips-Perron tests.  
   - Differencing to remove trends and stabilize the mean.  

3. **ARIMA Model Selection**  
   - Grid search over ARIMA(p,1,q) models.  
   - Selection based on AIC and BIC criteria.  

4. **Residual Diagnostics**  
   - Ljung-Box tests for autocorrelation in residuals.  
   - Normality and whiteness checks to validate the model.  

5. **Forecasting**  
   - Generate short-term forecasts with 95% confidence intervals.  
   - Visualize predictions alongside the historical series.

## Results

- ARIMA(1,1,2) is identified as the best-fitting model.  
- Residuals are largely uncorrelated, confirming model adequacy.  
- Forecasts include confidence regions, helping assess uncertainty.

**Output:** Project report ([PDF](Linear%20Times%20Series%20Project.pdf))

