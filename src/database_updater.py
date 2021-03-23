from peewee import *
from src.weather_maker_yandex import WeatherMaker, WeatherDayDescription
from datetime import datetime, date, timedelta


class SingletonMeta(type):

    DATABASE_PATH = '../test.db'
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            cls.database = SqliteDatabase(cls.DATABASE_PATH)
        return cls._instances[cls]


class DatabaseInstance(metaclass=SingletonMeta):

    def create_table(self, model):
        self.database.create_tables([model])


class DataIsOutOfDate(Exception):
    pass


class DataBaseHandler:

    class BaseModel(Model):
        class Meta:
            database = DatabaseInstance().database

    class Forecast(BaseModel):
        date = DateField(column_name='Date', unique=True)
        condition = CharField(column_name='Weather condition')
        temp_day = TextField(column_name='Daytime temperature')
        temp_night = TextField(column_name='Nighttime temperature')
        time_of_last_update = DateTimeField(column_name='Time of last update')

        class Meta:
            table_name = 'Forecast'

    def __init__(self):
        db = DatabaseInstance()
        db.create_table(model=self.Forecast)

    def delete_rows_from_database(self):
        query = self.Forecast.delete()
        query.execute()

    def add_row_to_database(self, date_, forecast: WeatherDayDescription):
        try:
            self.add_new_row_to_database(date_=date_, forecast=forecast)
        except IntegrityError:
            self.add_update_row_in_database(date_=date_, new_condition=forecast.condition,
                                            new_temp_d=forecast.temp_day, new_temp_n=forecast.temp_night)

    def add_new_row_to_database(self, date_, forecast: WeatherDayDescription):
        forecast_for_the_day = self.Forecast.create(date=date_,
                                                    condition=forecast.condition,
                                                    temp_day=forecast.temp_day,
                                                    temp_night=forecast.temp_night,
                                                    time_of_last_update=datetime.today())
        forecast_for_the_day.save()

    def add_update_row_in_database(self, date_, new_condition, new_temp_d, new_temp_n):
        forecast = self.Forecast.get(date=date_)
        forecast.condition = new_condition
        forecast.temp_day = new_temp_d
        forecast.temp_night = new_temp_n
        forecast.time_of_last_update = datetime.now()
        forecast.save()

    def get_row_from_database(self, date_, hours):
        forecast = self.Forecast.get(date=date_)
        if forecast.time_of_last_update < datetime.now() - timedelta(hours=hours):
            raise DataIsOutOfDate()
        return forecast


if __name__ == '__main__':
    weather_maker = WeatherMaker(date_range=10)
    forecasts = weather_maker.get_the_forecast_from_the_content()

    db_handler = DataBaseHandler()
    # db_handler.delete_rows_from_database()

    get_dates = [date(2021, 3, 26), date(2021, 3, 27)]
    # db_handler.add_rows_to_database(forecasts=forecasts)
    # db_handler.get_rows_from_database(get_dates)

    # db_handler.get_row_from_database(date_=get_dates[0], hours=1)
    db_handler.add_row_to_database(date_=get_dates[0], forecast=forecasts[get_dates[0]])
