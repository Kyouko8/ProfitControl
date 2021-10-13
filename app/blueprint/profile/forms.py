""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, HiddenField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo


class AddProfileForm(FlaskForm):

    profile = StringField("Nombre", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=3, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=64, message="Este campo admite hasta %(max)s caracteres.")
    ])

    status = RadioField('Estado', choices=[('1','Activo'), ('0','Inactivo')], default="1")
    submit = SubmitField("Guardar")
    submit_and_finish = SubmitField("Guardar y Finalizar")
