import math
import datetime
from .math_interpreter3 import Lexer, Interpreter
from .niceprice import NicePrice

def process_form_data(field):
    if field.data:
        return field.data

    return ""


def add_decimal_mark(number, ndigits=2) -> str:
    if ndigits:
        return "{0:,}".format(round(number, ndigits))
    return "{0:,}".format(number)


def get_month_name(number) -> str:
    if number is None:
        return ""
    return [
        "Enero", "Febrero", "Marzo",
        "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre",
        "Octubre", "Noviembre", "Diciembre"
    ][max(0, min(11, (number-1)%12))]

def get_day_name(number, first_monday=False, abbr=False) -> str:
    if number is None:
        return ""

    if isinstance(number, datetime.datetime):
        number = number.isoweekday()

    day = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"][(number + int(first_monday==True)) % 7]
    if abbr:
        return day[:3]
    
    return day


def calculate(calc, variables=None, functions=None):
    if variables is None:
        variables = {}

    if functions is None:
        functions = {}

    lexer = Lexer()
    inter = Interpreter(lexer, variables, functions)
    try:
        code = str(calc)

    except BaseException:
        pass

    result = inter.parse(code)
    return int(round(result, 0))


def calculate_orig(text):
    return int(round(float(text), 0))


def percent(number, total, default=0):
    if total == 0:
        return default

    return int(round(100*number/total))


def get_progress_color(percentage, value_red=5, value_orange=15, value_green=30, default="blue"):
    if percentage <= value_red:
        return "red"

    elif percentage <= value_orange:
        return "orange"

    elif percentage <= value_green:
        return "green"

    return default

def get_color(percentage, color1, color2, divider=0):
    if percentage <= divider:
        return color2

    return color1


def analyze_int_fields(field, default=None):
    error = 0
    try:
        if field.data:
            value = calculate(field.data)
        else:
            value = default

    except BaseException:
        error = 1
        field.errors.append("Ingrese un número válildo.")

    return (value, error)



def analyze_str_fields(field, default=None):
    error = 0
    try:
        if field.data:
            value = field.data
        else:
            value = default

    except BaseException:
        error = 1
        field.errors.append("Ingrese un texto válildo.")

    return (value, error)

def round_price(number):
    return round(float(number), 2)

nice_price = NicePrice()