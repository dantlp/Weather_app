import requests
import sys
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie


class Weather_app(QWidget):

    def __init__(self):
        super().__init__()
        # Initialize widgets with default text to ensure they are visible
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
        self.setWindowTitle("Weather App")

        main_vbox = QVBoxLayout()
        main_vbox.addStretch(1)
        main_vbox.addWidget(self.date_label,alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.city_label,alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.city_input,alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.get_weather_button, alignment=Qt.AlignmentFlag.AlignCenter)
        # Add the icon_label to the layout with center alignment
        main_vbox.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.temperature_label,alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.humidity_label,alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.description_label,alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addLayout(self.forecast_layout) # Add the forecast layout here
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

        # Set object names for styling
        self.date_label.setObjectName("date_label")
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.humidity_label.setObjectName("humidity_label")
        self.description_label.setObjectName("description_label")
        for i, day_widget in enumerate(self.forecast_widgets):
            day_widget["day"].setObjectName(f"forecast_day_{i}")
            day_widget["temp"].setObjectName(f"forecast_temp_{i}")

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
        """Clears data labels and shows an error message."""
        if hasattr(self, 'icon_label') and self.icon_label.movie():
            self.icon_label.movie().stop()
        self.city_label.setText("Please enter city: ")
        self.icon_label.clear()
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
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

        try:
            # --- Get and display current weather ---
            response = requests.get(current_weather_url)
            response.raise_for_status()
            data = response.json()

            # Code working
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

            # --- Get and display 5-day forecast ---
            response = requests.get(forecast_url)
            response.raise_for_status()
            forecast_data = response.json()
            
            # Filter for daily forecasts at noon
            daily_forecasts = [item for item in forecast_data.get("list", []) if "12:00:00" in item.get("dt_txt", "")]

            for i in range(min(len(daily_forecasts), 5)):
                day_data = daily_forecasts[i]
                widget_group = self.forecast_widgets[i]

                # Update day label (e.g., "Mon")
                day_dt = datetime.fromtimestamp(day_data.get("dt"))
                widget_group["day"].setText(day_dt.strftime("%a"))

                # Update icon
                weather_id = day_data.get("weather", [{}])[0].get("id")
                icon_path = self.get_weather_icon_path(weather_id)
                if icon_path:
                    movie = QMovie(icon_path)
                    widget_group["icon"].setMovie(movie)
                    movie.start()

                # Update temp
                temp = day_data.get("main", {}).get("temp")
                widget_group["temp"].setText(f"{temp:.0f}°C")

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