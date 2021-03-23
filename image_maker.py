import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re
from datetime import datetime, date
from weather_maker_yandex import WeatherMaker, WeatherDayDescription


YELLOW = (0, 255, 255)
GRAY = (90, 90, 90)
BLUE = (255, 255, 0)
DARK_BLUE = (255, 0, 0)
WHITE = (255, 255, 255)


class WeatherState:
    def __init__(self, path, patterns, background_gradient):
        self.path = path
        self.patterns = patterns
        self.background_gradient = background_gradient


IMAGE_FOR_FORECAST = {
    'sun': WeatherState(path='weather_img/sun.jpg',
                        patterns=['солн', 'ясн'],
                        background_gradient=(YELLOW, WHITE)),
    'cloud': WeatherState(path='weather_img/cloud.jpg',
                          patterns=['обл', 'пасм'],
                          background_gradient=(GRAY, WHITE)),
    'rain': WeatherState(path='weather_img/rain.jpg',
                         patterns=['дожд'],
                         background_gradient=(DARK_BLUE, WHITE)),
    'snow': WeatherState(path='weather_img/snow.png',
                         patterns=['сне', 'метел'],
                         background_gradient=(BLUE, WHITE))
}


class ImageMaker:
    PATH_TO_POSTCARD = 'weather_img/postcard.jpg'
    PATH_TO_FONT = 'fonts/20016.ttf'
    PATH_TO_FONT_FOR_TEMPERATURE = 'fonts/DejaVu_Sans_Mono_Nerd_Font_Complete.ttf'

    def create_weather_card(self, date_, forecast: WeatherDayDescription):
        postcard_img = cv2.imread(self.PATH_TO_POSTCARD)
        weather_descriptions = self.get_path_and_gradient_for_weather_image(condition=forecast.condition.lower())
        if weather_descriptions is None:
            raise RuntimeError('Нет подходящей под погоду картинки.')
        path_to_weather_img = weather_descriptions[0]
        weather_img = cv2.imread(path_to_weather_img)
        bg_gradient = weather_descriptions[1]
        self.add_gradient_as_background(postcard_img, bg_gradient)
        self.add_weather_image_on_postcard(postcard_img, weather_img)
        self.add_weather_description_on_postcard(postcard_img, date_, forecast)

    @staticmethod
    def get_path_and_gradient_for_weather_image(condition: str):
        for image, components in IMAGE_FOR_FORECAST.items():
            for pattern in components.patterns:
                if re.search(pattern, condition):
                    path_to_weather_img = components.path
                    background_gradient = components.background_gradient
                    return path_to_weather_img, background_gradient
        return None

    def add_gradient_as_background(self, postcard: Image, bg_grad: tuple):
        post_rows, post_cols, _ = postcard.shape
        from_color, to_color = bg_grad
        for y in range(post_cols):
            color = self.get_next_color(from_color, to_color, step=y // 2)
            postcard[:, y] = [color for _ in range(post_rows)]

    @staticmethod
    def get_next_color(from_color: tuple, to_color: tuple, step=0):
        compared_colors = zip(from_color, to_color)
        _next_color = []
        for color_, to_color in compared_colors:
            if color_ + step >= to_color:
                _next_color.append(to_color)
                continue
            _next_color.append(color_ + step)
        return _next_color

    @staticmethod
    def add_weather_image_on_postcard(postcard: Image, weather_img: Image):
        w_rows, w_cols, _ = weather_img.shape
        p_rows, p_cols, _ = postcard.shape
        x_cord = (p_rows - w_rows) // 4
        y_cord = (p_cols // 2 - w_cols) // 2
        roi = postcard[x_cord:x_cord + w_rows, y_cord:y_cord + w_cols]

        weather_gray = cv2.cvtColor(weather_img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(weather_gray, 225, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        postcard_bg = cv2.bitwise_and(roi, roi, mask=mask)
        weather_fg = cv2.bitwise_and(weather_img, weather_img, mask=mask_inv)
        modify_postcard = cv2.add(postcard_bg, weather_fg)
        postcard[x_cord:x_cord + w_rows, y_cord:y_cord + w_cols] = modify_postcard

    def add_weather_description_on_postcard(self, postcard: np.array, date_, forecast: WeatherDayDescription):
        im = Image.fromarray(postcard)
        draw = ImageDraw.Draw(im)
        p_rows, p_cols, _ = postcard.shape

        date_ = datetime.strftime(date_, '%d.%m.%Y')
        self.put_date_on_postcard(date=date_, draw=draw, p_cols=p_cols, font=self.PATH_TO_FONT, font_size=30)

        y_pos, y_step = 30, 25
        condition = forecast.condition
        self.put_text_on_image(draw=draw, text='Описание погоды:', y_pos=y_pos, p_cols=p_cols,
                               font=self.PATH_TO_FONT, font_size=24)
        self.put_text_on_image(draw=draw, text=condition, y_pos=y_pos + y_step, p_cols=p_cols,
                               font=self.PATH_TO_FONT, font_size=24)

        temp_d = forecast.temp_day
        self.put_text_on_image(draw=draw, text='Температура днем:', y_pos=y_pos + 3 * y_step, p_cols=p_cols,
                               font=self.PATH_TO_FONT, font_size=24)
        self.put_text_on_image(draw=draw, text=temp_d, y_pos=y_pos + 4 * y_step, p_cols=p_cols,
                               font=self.PATH_TO_FONT_FOR_TEMPERATURE, font_size=24)

        temp_n = forecast.temp_night
        self.put_text_on_image(draw=draw, text='Температура ночью:', y_pos=y_pos + 5 * y_step, p_cols=p_cols,
                               font=self.PATH_TO_FONT, font_size=24)
        self.put_text_on_image(draw=draw, text=temp_n, y_pos=y_pos + 6 * y_step, p_cols=p_cols,
                               font=self.PATH_TO_FONT_FOR_TEMPERATURE, font_size=24)

        postcard = np.asarray(im)
        self.view_image(postcard, f'Postcard for day {date_}')

    @staticmethod
    def put_text_on_image(draw, text, y_pos, p_cols, font, font_size):
        font = ImageFont.truetype(font, size=font_size)
        w, h = draw.textsize(text, font=font)
        x_pos = int(p_cols / 2 + (p_cols / 2 - w) / 2)
        draw.text((x_pos, y_pos), text, fill='rgb(0, 0, 0)', font=font)

    @staticmethod
    def put_date_on_postcard(date, draw, p_cols, font, font_size):
        font = ImageFont.truetype(font, size=font_size)
        w, h = draw.textsize(date, font=font)
        y_pos_for_date = 170
        x_pos_for_date = int((p_cols / 2 - w) / 2)
        draw.text((x_pos_for_date, y_pos_for_date), date, fill='rgb(0, 0, 0)', font=font)

    @staticmethod
    def view_image(image, name_of_window):
        cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
        cv2.imshow(name_of_window, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    weather_maker = WeatherMaker()
    forecasts = weather_maker.get_the_forecast_from_the_content()

    image_maker = ImageMaker()
    for date_, forecast in forecasts.items():
        image_maker.create_weather_card(date_=date_, forecast=forecast)

    date = date.today()
    forecast_ = WeatherDayDescription(condition='Небольшой снег', temp_d='+1', temp_n='0')
    image_maker.create_weather_card(date_=date, forecast=forecast_)
