""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import  SubmitField, RadioField, FileField
from wtforms.validators import DataRequired, Length, EqualTo


class LoadJSONForm(FlaskForm):
    upload_file = FileField("Seleccione un archivo", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])
    
    if_exists = RadioField('Si ya existe', choices=[('0','Personalizar'), ('1','No hacer nada')], default="0")
    update = RadioField('Actualizar Precios', choices=[('0', 'No modificar'), ('1', 'Costo, Costo Extra y Precio'), ('2','Precio'), ('3','Costo y Costo Extra')], default="0")
    stock = RadioField('Actualizar Stock', choices=[('0', 'No modificar'), ('1','Agregar al actual'), ('2', 'Colocar en 0'), ('3','Reemplazar')], default="0")
    update_name = RadioField('Editar Nombre', choices=[('0','No modificar'), ('1','[Nombre del Producto]@Copia'), ('2','[Nombre del Producto] ([Número de Copia])'), ('3','@[Nombre del Producto]')], default="0")
    
    submit = SubmitField("Cargar Copia")
