""" Main file of project """
import os
from app import create_app, db


def main():
    if not os.path.exists("app/.data"):
        os.mkdir("app/.data")

    app_instance = create_app()

    with app_instance.app_context():
        db.create_all()
        app_instance.run()


if __name__ == '__main__':
    main()

    

        
