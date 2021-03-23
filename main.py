import argparse
from weather_handler import WeatherHandler

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Weather forecast')
    parser.add_argument('-m', '--method', type=str, default='get',
                        help='Methods for forecast processing: add - to add forecast to database; get - to get forecast'
                             ' from database; create - to create postcard with forecast')
    parser.add_argument('-d', '--date_range', type=int, default=10, help='Date range')
    args = parser.parse_args()

    if args.method == 'get':
        weather_handler = WeatherHandler(date_range=args.date_range)
        weather_handler.print_forecast_for_dates()

    elif args.method == 'add':
        weather_handler = WeatherHandler(date_range=args.date_range)
        weather_handler.add_weather_forecast_for_dates()

    elif args.method == 'create':
        weather_handler = WeatherHandler(date_range=args.date_range)
        weather_handler.create_postcard_forecast_for_dates()

    else:
        print(f'Method {args.method} cannot be executed. Supported methods: add, get or create.')
