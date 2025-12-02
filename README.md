# Weather Forecast App
A simple Python application that provides an easy and visual representation of today's weather and predicts temperatures for the next 5 days.

Features
  Current weather display with visual icons

  5-day temperature forecast

  Linear regression-based temperature predictions

  User-friendly PyQt6 interface

Before use

pip install requests PyQt6 scikit-learn numpy

run app 

  python Todays_Weather.py
or
  python Weather_Forecast.py
or
  python Weather_Regression_Forecast.py

Usage
  Enter your city name in the search field

  View current weather conditions with animated icons

  See temperature predictions for the next 5 days

  Simple and intuitive visual interface

  The app combines real-time weather data with linear regression to provide accurate temperature forecasts in an easy-to-understand visual format.

As the app is using a very basic linear regression, it is able to forecast the temperature but not the weather conditions, as gathering information from the API takes around 2-3 seconds per search, Time series analysis requieres infromation from previous years and recent information, this would make the execution take way longer to show the information.

For future improvement, it is recommended to store the API information, limit the cities selected and implement time series analysis.
