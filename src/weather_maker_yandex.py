import requests
import http.client
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta


class WeatherDayDescription:
    def __init__(self, condition, temp_d, temp_n):
        self.condition = condition
        self.temp_day = temp_d
        self.temp_night = temp_n


class WeatherMaker:
    CITY = 'nizhny-novgorod'
    URL_TO_FORECAST = f'/pogoda/{CITY}'
    DAYS_FORECAST = {}

    def __init__(self, date_range=7):
        self.date_range = date_range
        self._content = None

    def get_the_content_from_the_site(self):
        conn = http.client.HTTPSConnection("yandex.ru")
        conn.request("GET", self.URL_TO_FORECAST)
        response = conn.getresponse()
        if response.status != 200:
            raise requests.RequestException('Не удалось получить прогноз погоды.')
        self._content = response.read().decode("utf-8")

    def get_the_forecast_from_the_content(self):
        self.get_the_content_from_the_site()
        html_doc = BeautifulSoup(self._content, 'html.parser')
        forecasts = html_doc.find_all('div', {'class': 'forecast-briefly__day'})
        for forecast in forecasts:
            date_str = forecast.find_all('time', {'class': 'time forecast-briefly__date'})[0]['datetime']
            day_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M%z').replace(tzinfo=None).date()
            temperatures = forecast.find_all('span', {'class': 'temp__value temp__value_with-unit'})
            temp_daytime, temp_nighttime = [t.text for t in temperatures]
            condition = forecast.find('div', {'class': 'forecast-briefly__condition'}).text

            if self.is_date_in_range(day_date):
                self.DAYS_FORECAST[day_date] = WeatherDayDescription(condition, temp_daytime, temp_nighttime)

        # self.print_forecasts()
        return self.DAYS_FORECAST

    def is_date_in_range(self, date_):
        return date.today() <= date_ < date.today() + timedelta(days=self.date_range)

    def print_forecasts(self):
        for date_, description in self.DAYS_FORECAST.items():
            print(f'Дата: {datetime.strftime(date_, "%d.%m.%Y")}')
            print(f'\tСостояние погоды: {description.condition}')
            print(f'\tТемпература днем: {description.temp_day}')
            print(f'\tТемпература ночью: {description.temp_night}')


if __name__ == '__main__':
    maker = WeatherMaker()
    forecasts = maker.get_the_forecast_from_the_content()
    maker.print_forecasts()
