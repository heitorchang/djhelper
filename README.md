# djhelper

Utility to auto-generate typical configuration files for Django (latest version)

## Usage

`djhelper.py proj PROJECT_NAME` creates a new Django project with:

* Virtualenv in `venv/`
* `.gitignore`
* `runserver, migrate, makemigrations` empty files for tab completion in the command line
* Moves the `SECRET_KEY` to `mysecrets.py`
* Creates a `ui` app with a `static` directory and a placeholder HTML file
* Migrates default apps
* Creates an initial Git repository

`djhelper.py app APP_NAME` creates a new app within a Django project:

* Installs the app in `settings.py`
* Creates an empty, namespaced `urls.py`
* Updates the project's `urls.py` to include the new app's `urls.py`
* Creates a namespaced `templates/` directory with an empty `base.html`
