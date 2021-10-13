""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length


class AddShoppingDaySpendingForm(FlaskForm):
    hidden_token = HiddenField()

    spending = StringField("Nombre del Gasto", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])

    description = StringField("Descripción")

    price = StringField("Monto", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])

    submit = SubmitField("Guardar")
    
    submit_and_finish = SubmitField("Guardar y Finalizar")

