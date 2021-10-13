""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class ChangeNameUserForm(FlaskForm):
    name = StringField("Nombre Completo", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=3, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=128, message="Este campo admite hasta %(max)s caracteres.")
    ])
    
    submit = SubmitField("Guardar")


class ChangePasswordUserForm(FlaskForm):
    current_email = StringField("Email Actual", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(max=256, message="Este campo admite hasta %(max)s caracteres."),
        Email(message="El email ingresado no es válido.")
    ])

    current_password = PasswordField("Contraseña Actual", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=8, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=160, message="Este campo admite hasta %(max)s caracteres.")
    ])

    password = PasswordField("Nueva Contraseña", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=8, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=160, message="Este campo admite hasta %(max)s caracteres."),
        EqualTo('confirm', message='Las contraseñas deben coincidir')
    ])

    confirm = PasswordField("Confirmar Contraseña", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=8, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=160, message="Este campo admite hasta %(max)s caracteres.")
    ])
    
    submit = SubmitField("Guardar")

class ChangeEmailUserForm(FlaskForm):
    current_email = StringField("Email Actual", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(max=256, message="Este campo admite hasta %(max)s caracteres."),
        Email(message="El email ingresado no es válido.")
    ])

    current_password = PasswordField("Contraseña Actual", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=8, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=160, message="Este campo admite hasta %(max)s caracteres.")
    ])

    email = StringField("Email Actual", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(max=256, message="Este campo admite hasta %(max)s caracteres."),
        Email(message="El email ingresado no es válido.")
    ])
    
    submit = SubmitField("Guardar")