""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo


class AddNoteForm(FlaskForm):

    title = StringField("Nombre", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=3, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=64, message="Este campo admite hasta %(max)s caracteres.")
    ])
    content = TextAreaField("Contenido", validators=[
        Length(max=8192, message="Este campo admite hasta %(max)s caracteres.")
    ])

    submit = SubmitField("Guardar")
    submit_and_finish = SubmitField("Guardar y Finalizar")
