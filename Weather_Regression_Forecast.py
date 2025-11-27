import requests
import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie
import numpy as np
from sklearn.linear_model import LinearRegression


class Weather_app(QWidget):

    def __init__(self):
        super().__init__()
        # Initialize widgets
        self.date_label = QLabel(self)
        self.city_label = QLabel("Please enter city:", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Search", self)
        self.icon_label = QLabel(self)
        self.temperature_label = QLabel(self)
        self.humidity_label = QLabel(self)
        self.description_label = QLabel(self)

        # Create a layout and widgets for the 5-day forecast
        self.forecast_layout = QHBoxLayout()
        self.forecast_widgets = []
        for _ in range(5):
            day_vbox = QVBoxLayout()
            day_widget_group = {
                "day": QLabel(),
                "icon": QLabel(),
                "temp": QLabel()
            }
            day_vbox.addWidget(day_widget_group["day"])
            day_vbox.addWidget(day_widget_group["icon"])
            day_vbox.addWidget(day_widget_group["temp"])
            self.forecast_widgets.append(day_widget_group)
            self.forecast_layout.addLayout(day_vbox)

        self.initGUI()

    def initGUI(self):
        self.setWindowTitle("Weather App with Regression Forecast")

        main_vbox = QVBoxLayout()
        main_vbox.addStretch(1)
        main_vbox.addWidget(self.date_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.city_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.city_input, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.get_weather_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.temperature_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.humidity_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.description_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addLayout(self.forecast_layout)
        main_vbox.addStretch(1)
        self.setLayout(main_vbox)

        # Set current date
        self.date_label.setText(datetime.today().strftime("%A, %B %d, %Y"))

        # Center align all widgets
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'setAlignment'):
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Scale GIF to fit
        self.icon_label.setFixedSize(128, 128)
        self.icon_label.setScaledContents(True)
        for day_widget in self.forecast_widgets:
            day_widget["icon"].setFixedSize(64, 64)
            day_widget["icon"].setScaledContents(True)

        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; }
            QLabel#date_label { font-size: 18px; color: #555; margin-bottom: 15px; }
            QLabel#city_label { font-size: 20px; }
            QLineEdit#city_input { font-size: 20px; font-style: italic; padding: 5px; border: 1px solid #ccc; border-radius: 5px; max-width: 300px;}
            QPushButton#get_weather_button { font-size: 24px; font-weight: bold; margin: 15px; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; max-width: 250px;}
            QPushButton#get_weather_button:hover { background-color: #45a049; }
            QLabel#temperature_label { font-size: 50px; font-weight: bold; color: #333; }
            QLabel#humidity_label { font-size: 30px; color: #555; }
            QLabel#description_label { font-size: 25px; font-style: italic; color: #666; margin-bottom: 10px; }
            QLabel[objectName^="forecast_day"] { font-size: 16px; font-weight: bold; color: #333; }
            QLabel[objectName^="forecast_temp"] { font-size: 14px; color: #555; }
        """)

        self.get_weather_button.clicked.connect(self.weather_search)

    def display_error(self, message):
        if hasattr(self, 'icon_label') and self.icon_label.movie():
            self.icon_label.movie().stop()
        self.icon_label.clear()
        self.city_label.setText("Please enter city: ")
        self.city_input.clear()
        self.temperature_label.clear()
        self.humidity_label.clear()
        self.description_label.setText(f"Error: {message}")
        self.description_label.setStyleSheet("font-size: 20px; font-style: italic; color: #D32F2F;")
        # Clear forecast widgets on error
        for day_widget in self.forecast_widgets:
            day_widget["day"].clear()
            day_widget["icon"].clear()
            day_widget["temp"].clear()

    def weather_search(self):
        """Enter Data in URL."""
        city = self.city_input.text().title()
        api_key = "27cd0727c153dac69c31a32fd17d080d"
        current_weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        try:
            # Get current weather and coordinates
            response = requests.get(current_weather_url)
            response.raise_for_status()
            data = response.json()

            lat = data['coord']['lat']
            lon = data['coord']['lon']
            
            # Update current weather UI
            weather_id = data.get("weather", [{}])[0].get("id")
            icon_path = self.get_weather_icon_path(weather_id)
            if icon_path:
                movie = QMovie(icon_path)
                self.icon_label.setMovie(movie)
                movie.start()

            # Edit text after getting info
            temp = int(data.get("main", {}).get("temp"))
            humidity = data.get("main", {}).get("humidity")
            description = data.get("weather", [{}])[0].get("description", "N/A")
            
            self.city_label.setText(f"The weather in {city} is:")
            self.city_input.clear()
            self.temperature_label.setText(f"Temperature: {temp}°C")
            self.humidity_label.setText(f"Humidity: {humidity}%")
            self.description_label.setText(f"{description.title()}")
            self.description_label.setStyleSheet("font-size: 25px; font-style: italic; color: #666;")

            # --- Get historical data for regression model ---
            timestamps = []
            temps = []
            today = datetime.today()
            for i in range(5, 0, -1): # Get data for the last 5 days
                past_date = today - timedelta(days=i)
                date_str = past_date.strftime('%Y-%m-%d')
                api_key2 = "6a242d9b802ae4c613994cddc3a640fc"
                summary_url = f"https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={date_str}&appid={api_key2}&units=metric"
                summary_response = requests.get(summary_url)
                summary_response.raise_for_status()
                summary_data = summary_response.json()
                
                # The API returns a date string. Convert it to a numerical timestamp.
                date_obj = datetime.strptime(summary_data['date'], '%Y-%m-%d')
                timestamps.append(date_obj.timestamp())
                
                # CORRECTED: Use the 'afternoon' key which exists in the API response
                temps.append(summary_data['temperature']['afternoon'])

            X = np.array(timestamps).reshape(-1, 1)
            y = np.array(temps)

            # --- Train model and predict future temperatures ---
            model = LinearRegression()
            model.fit(X, y)

            future_timestamps = []
            for i in range(1, 6):
                future_date = today + timedelta(days=i)
                future_noon = future_date.replace(hour=12, minute=0, second=0, microsecond=0)
                future_timestamps.append(future_noon.timestamp())
            
            future_X = np.array(future_timestamps).reshape(-1, 1)
            predicted_temps = model.predict(future_X)

            # --- Update UI with regression forecast ---
            unknown_icon_path = "icons/unknown.gif"
            for i in range(5):
                widget_group = self.forecast_widgets[i]

                # Calculate future day
                future_date = today + timedelta(days=i + 1)
                widget_group["day"].setText(future_date.strftime("%a"))

                # Set icon to "unknown" as we cannot predict it
                movie = QMovie(unknown_icon_path)
                widget_group["icon"].setMovie(movie)
                movie.start()

                # Use the predicted temperature from our model
                predicted_temp = predicted_temps[i]
                widget_group["temp"].setText(f"{predicted_temp:.0f}°C (pred)")

        except requests.exceptions.HTTPError as err:
            match err.response.status_code:
                case 400:
                    self.display_error("400: Bad Request - Check your input")
                case 401:
                    self.display_error("401: Unauthorized - Invalid API Key")
                case 403:
                    self.display_error("403: Forbidden - Access Denied")
                case 404:
                    self.display_error(f"404: City '{city}' not found")
                case 500:
                    self.display_error("500: Internal Server Error")
                case 501:
                    self.display_error("501: Not Implemented")
                case 502:
                    self.display_error("502: Bad Gateway")
                case 503:
                    self.display_error("503: Service Unavailable")
                case 504:
                    self.display_error("504: Gateway Timeout")
                case _:
                    self.display_error(f"{err.response.status_code}: An unexpected error occurred")
        except requests.exceptions.RequestException:
            self.display_error("Network Error - Check your connection")
        except Exception as e:
            self.display_error(f"An unexpected error occurred: {e}")

    @staticmethod
    def get_weather_icon_path(weather_id):
        """Icon select."""
        if not weather_id: return "icons/unknown.gif"
        if 200 <= weather_id <= 232: return "icons/thunderstorm.gif"
        if 300 <= weather_id <= 321: return "icons/drizzle.gif"
        if 500 <= weather_id <= 531: return "icons/rain.gif"
        if 600 <= weather_id <= 622: return "icons/snow.gif"
        if 701 <= weather_id <= 781: return "icons/mist.gif"
        if weather_id == 800: return "icons/clear.gif"
        if 801 <= weather_id <= 804: return "icons/clouds.gif"
        return "icons/unknown.gif"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_widget = Weather_app()
    weather_widget.show()
    sys.exit(app.exec())