""" Main file of project """
import sys, os
from app import create_app, db
from app import models
from app import offline

def main():
    open_tab = False
    debug = True
    minify = True
    args = sys.argv.copy()

    if len(args) >= 2:
        if "--openTabInBrowser" in args:
            args.remove("--openTabInBrowser")
            open_tab = True

        if "--no-debug" in args:
            args.remove("--no-debug")
            debug = False

        if "--offline" in args:
            args.remove("--offline")
            offline.data = True

        if "--nominify" in args:
            args.remove("--nominify")
            minify = False

    if not os.path.exists("app/.data"):
        os.mkdir("app/.data")

    app_instance = create_app(minify=minify)

    with app_instance.app_context():
        db.create_all()

    host = '0.0.0.0'
    port = 5000

    if len(args) == 2:
        host = args[1]

    elif len(args) == 3:
        port = int(args[2])

    if open_tab:
        import webbrowser
        if host == '0.0.0.0':
            webbrowser.open(f"http://localhost:{port}/")
        else:
            webbrowser.open(f"http://{host}:{port}/")
        open_tab = None

    app_instance.run(host, port, debug=debug)


if __name__ == '__main__':
    main()

    

        
