"""Note routes"""
import logging
import math
import random
from flask import render_template, request, redirect, abort, url_for
from flask_login import current_user, login_required


from . import note_bp
from .forms import AddNoteForm

from app.models import Note, WorkDay, ShoppingDay
from app.functions import calculate

logger = logging.getLogger(__name__)


@note_bp.route("/update/", methods=["GET", "POST"])
@note_bp.route("/update/<token>", methods=["GET", "POST"])
@login_required
def add(token=None):
    form = AddNoteForm()

    mode = "add"
    note = None
    show_finish = True

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        # Crear el producto si no existe ninguno con el nombre ingresado:
        note = None
        if token:
            note = Note.get_by_token(token)
            if not note.id_user == current_user.id:
                note = None
        
        if not note:
            note = Note.get_by_name(title, current_user.id)

        if note:
            note.title = title
            note.content = content
            note.save()

        else:
            note = Note(
                id_user=current_user.id,
                title=title,
                content=content
            )
            note.save()

        next_page = request.form.get('next', None)
        if not next_page or url_parse(next_page).netloc == "":
            next_page = url_for('note.add')
            if token is not None:
                next_page = url_for('note.details', token=token)
            
            elif form.submit_and_finish.data:
                next_page = url_for('note.view_list')

        return redirect(next_page)

    else:
        if token is not None:
            note = Note.get_by_token(token)
            if note is None or not note.id_user == current_user.id:
                abort(404)
                
            form.title.data = note.title
            form.content.data = str(note.content)
            mode = "edit"
            show_finish = False
        
    return render_template("note/add.html", form=form, mode=mode, note=note, show_finish=show_finish)


@note_bp.route("/list/", methods=["GET"])
@login_required
def view_list():
    notes = Note.get_by_user(current_user.id)
    workdays = WorkDay.get_by_user_and_contains_notes(current_user.id)  
    shoppingdays = ShoppingDay.get_by_user_and_contains_notes(current_user.id)    

    return render_template("note/list.html", notes=notes, workdays=workdays, shoppingdays=shoppingdays)


@note_bp.route("/details/<token>/", methods=["GET"])
@login_required
def details(token=None):
    note = Note.get_by_token(token)
    
    if note is None:
        abort(404)

    if not note.id_user == current_user.id:
        abort(404)   
    
    return render_template("note/details.html", note=note, token=token)

@note_bp.route("/from-workday/<token>/", methods=["GET"])
@login_required
def workday_note_details(token=None):
    workday = WorkDay.get_by_token(token)
    
    if workday is None:
        abort(404)

    if not workday.id_user == current_user.id:
        abort(404)   
    
    return render_template("note/workday_note.html", workday=workday, token=token)

@note_bp.route("/from-shoppingday/<token>/", methods=["GET"])
@login_required
def shoppingday_note_details(token=None):
    shoppingday = ShoppingDay.get_by_token(token)
    
    if shoppingday is None:
        abort(404)

    if not shoppingday.id_user == current_user.id:
        abort(404)   
    
    return render_template("note/shoppingday_note.html", shoppingday=shoppingday, token=token)


@note_bp.route("/discard/<token>/", methods=["GET"])
@login_required
def discard(token=None):
    note = Note.get_by_token(token)
    if note is None or not note.id_user == current_user.id:
        abort(404) 

    if note.can_be_deleted():
        note.delete()
        
    return redirect(url_for("note.view_list"))



@note_bp.route("/test/add/<int:number>/")
@login_required
def test_add(number):
    for i in range(int(number)):
        note = Note(
            id_user=current_user.id,
            title=f"Nota Auto Generada {i+1}",
            content=f"Contenido de la nota. Nota {i+1}",
        )
        note.save()

    return redirect(url_for("note.list"))