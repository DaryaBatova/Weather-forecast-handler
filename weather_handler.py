from weather_maker_yandex import WeatherMaker
from database_updater import DataBaseHandler
from datetime import timedelta, date
from image_maker import ImageMaker


class WeatherHandler:
    HOURS = 1

    def __init__(self, date_range):
        self.weather_maker = WeatherMaker(date_range=date_range)
        self.db_handler = DataBaseHandler()
        self.image_maker = ImageMaker()
        self.dates = [date.today() + timedelta(days=x) for x in range(date_range)]

    def get_weather_forecast_for_dates(self):
        forecast_from_database = []
        cnt = 0
        try:
            for date_ in self.dates:
                forecast = self.db_handler.get_row_from_database(date_=date_, hours=self.HOURS)
                forecast_from_database.append((date_, forecast))
                cnt += 1
        except Exception as exc:
            if exc.__class__.__name__ == 'ForecastDoesNotExist' or exc.__class__.__name__ == 'DataIsOutOfDate':
                forecasts = self.weather_maker.get_the_forecast_from_the_content()
                for date_ in self.dates[cnt:]:
                    self.db_handler.add_row_to_database(date_=date_, forecast=forecasts[date_])
                    forecast_from_database.append((date_, forecasts[date_]))
        return forecast_from_database

    def add_weather_forecast_for_dates(self):
        forecasts = self.weather_maker.get_the_forecast_from_the_content()
        for date_, forecast in forecasts.items():
            self.db_handler.add_row_to_database(date_=date_, forecast=forecast)

    def create_postcard_forecast_for_dates(self):
        f_db = self.get_weather_forecast_for_dates()
        for date_, forecast in f_db:
            self.image_maker.create_weather_card(date_=date_, forecast=forecast)

    def print_forecast_for_dates(self):
        f_db = self.get_weather_forecast_for_dates()
        for date_, forecast in f_db:
            print(f'Дата: {date_}\n\tОписание погоды: {forecast.condition}')
            print(f'\tТемпература днём: {forecast.temp_day}\n\tТемпература ночью: {forecast.temp_night}')


if __name__ == '__main__':
    date_range = int(input('Введите диапазон дат'))
    weather_handler = WeatherHandler(date_range=date_range)
    weather_handler.print_forecast_for_dates()
    weather_handler.create_postcard_forecast_for_dates()
