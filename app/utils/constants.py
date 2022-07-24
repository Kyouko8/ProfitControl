from app import db


MODEL = db.Model
COLUMN = db.Column

STRING = db.String
TEXT = db.Text
INTEGER = db.Integer
FLOAT = db.Float
DATETIME = db.DateTime
BOOLEAN = db.Boolean

FK = db.ForeignKey


class ModelSaveDelete():
    def save(self):
        try:
            db.session.add(self)

        except:
            db.session.rollback()

        finally:
            db.session.commit()

    def delete(self):
        try:
            db.session.delete(self)

        except:
            db.session.rollback()

        finally:
            db.session.commit()

    def get_as_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)

        return d