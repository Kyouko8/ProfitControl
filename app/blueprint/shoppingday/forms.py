""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo


class AddShoppingDayForm(FlaskForm):
    date = StringField("Fecha", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=3, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=64, message="Este campo admite hasta %(max)s caracteres.")
    ])

    note = TextAreaField("Nota (opcional)", validators=[
        Length(max=2048, message="Este campo admite hasta %(max)s caracteres.")
    ])
    
    submit = SubmitField("Guardar")

class AddShoppingDayProductForm(FlaskForm):
    product = StringField("Nombre del Producto")

    price = StringField("Precio de Venta")

    cost = StringField("Costo")

    extra_cost = StringField("Costo Extra")

    quantity = StringField("Cantidad Vendida", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])

    submit = SubmitField("Agregar")
    submit_and_finish = SubmitField("Agregar y Finalizar")



class SearchShoppingDayForm(FlaskForm):
    min_price = StringField("Venta Mínima")

    max_price = StringField("Venta Máxima")

    min_date = StringField("Fecha Inicial")

    max_date = StringField("Fecha Final")

    min_shoppings = StringField("Productos Mínimos")

    max_shoppings = StringField("Productos Máximos")

    min_profit = StringField("Ganancia Mínima")

    max_profit = StringField("Ganancia Máxima")

    min_cost = StringField("Inversión Mínima")

    max_cost = StringField("Inversión Máxima")

    submit = SubmitField("Buscar")


class NoteShoppingDayForm(FlaskForm):
    note = TextAreaField("Nota", validators=[
        Length(max=2048, message="Este campo admite hasta %(max)s caracteres.")
    ])
    
    submit = SubmitField("Guardar")