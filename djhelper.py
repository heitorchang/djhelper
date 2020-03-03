#!winpty python.exe

# Remove winpty above if not using Git Bash

# Script that extends Django's manage.py
# - creates the virtualenv
# - creates .gitignore
# - touches commands runserver, migrate, makemigrations for tab completion
# - moves the SECRET_KEY to mysecrets.py
# - migrates default apps
# - creates an initial Git repository

# When starting an app:
# - installs the app in settings.py 
# - creates a namespaced urls.py
# - updates the project's urls.py to include the new app's URLs
# - creates a namespaced templates directory with empty base.html

# Configuration
# Edit the shebang above to use a different Python in your system

# Copy the values in config_example.py to config.py

# GitHub username
# GITHUB_USERNAME = "heitorchang"


import os
import sys
import subprocess
import shutil
import distutils.dir_util


# Help notice
VALID_COMMANDS = "Valid commands: proj, app, startproject, startapp"

# Location of resources
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")


def echo_progress(message):
    print("[djhelper]", message)
    
    
def create_venv(root_dir):
    echo_progress("Creating venv")
    if os.path.isdir("venv"):
        raise FileExistsError("venv already exists.")
    else:
        subprocess.run("python -m venv venv".split())
        # later, by using the Python in the venv directory,
        # there's no need to activate the venv


def extract_secrets(project_name):
    django_settings_dir = os.path.join(os.getcwd(), project_name)
    with open(os.path.join(django_settings_dir, 'settings.py'), encoding="utf-8") as settings,\
         open(os.path.join(django_settings_dir, 'mysecrets.py'), 'w', encoding="utf-8") as secrets,\
         open(os.path.join(django_settings_dir, 'new_settings.py'), 'w', encoding="utf-8") as new_settings:
          
        for line in settings:
            if 'SECRET_KEY =' in line:
                print(line, file=secrets, end="")
                
            elif 'import os' in line:
                print(line, file=new_settings, end="")
                print("from .mysecrets import SECRET_KEY, DEBUG", file=new_settings, end="")

            elif 'DEBUG' in line:
                print(line, file=secrets, end="")
                
            # replace end of settings with predefined values
            elif 'Internationalization' in line:
                break
            
            else:
                print(line, file=new_settings, end="")

        # Print the last part of settings.py
        print(open(os.path.join(RESOURCES_DIR, "settingsfooter.txt")).read(), file=new_settings)

    shutil.move(os.path.join(django_settings_dir, 'new_settings.py'), os.path.join(django_settings_dir, 'settings.py'))


def install_app(project_name, app_name):
    django_settings_dir = os.path.join(os.getcwd(), project_name)
    with open(os.path.join(django_settings_dir, 'settings.py'), encoding="utf-8") as settings,\
         open(os.path.join(django_settings_dir, 'new_settings.py'), 'w', encoding="utf-8") as new_settings:
        for line in settings:
            if "INSTALLED_APPS" in line:
                print(line, file=new_settings, end="")
                print(f"    '{app_name}',", file=new_settings)
            else:
                print(line, file=new_settings, end="")
                
    shutil.move(os.path.join(django_settings_dir, 'new_settings.py'), os.path.join(django_settings_dir, 'settings.py'))


def create_app(root_dir, app_name, create_templates=True):
    os.chdir(root_dir)
    
    if os.path.isdir(app_name):
        echo_progress("App already exists. Aborting.")
        exit(0)

    project_dir = os.getcwd()

    echo_progress(f"Creating new app {app_name} in " + project_dir)

    venv_scripts = os.path.join(project_dir, 'venv', 'Scripts')
    venv_py = os.path.join(venv_scripts, "python.exe")

    subprocess.run([venv_py, "manage.py", "startapp", app_name, '-v', '2'])
    project_name = os.path.basename(os.getcwd())

    app_dir = os.path.join(project_dir, app_name)

    echo_progress(f"Creating {app_name}/urls.py")
    with open(os.path.join(app_dir, "urls.py"), 'w', encoding="utf-8") as urls:
        print(open(os.path.join(RESOURCES_DIR, "appurlsheader.txt")).read(), file=urls, end="")
        print(f"app_name = '{app_name}'", file=urls)
        print(open(os.path.join(RESOURCES_DIR, "appurlsfooter.txt")).read(), file=urls, end="")

    include_urls(project_name, app_name)

    echo_progress("Installing app in settings.py")
    install_app(project_name, app_name)

    if create_templates:
        echo_progress("Creating templates directory")
        os.mkdir(os.path.join(app_dir, "templates"))
        os.mkdir(os.path.join(app_dir, "templates", app_name))
        shutil.copyfile(os.path.join(RESOURCES_DIR, "basehtml.txt"), os.path.join(app_dir, "templates", app_name, "base.html"))

    echo_progress("End of app creation")

            
def include_urls(project_name, app_name):
    django_settings_dir = os.path.join(os.getcwd(), project_name)
    with open(os.path.join(django_settings_dir, 'urls.py'), encoding="utf-8") as urls,\
         open(os.path.join(django_settings_dir, 'new_urls.py'), 'w', encoding="utf-8") as new_urls:
        for line in urls:
            if line.strip() == "from django.urls import path":
                print("from django.urls import path, include", file=new_urls)
            elif "]" in line:
                print(f"    path('{app_name}/', include('{app_name}.urls')),", file=new_urls)
                print(line, file=new_urls, end="")
            else:
                print(line, file=new_urls, end="")
                
    shutil.move(os.path.join(django_settings_dir, 'new_urls.py'), os.path.join(django_settings_dir, 'urls.py'))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python djhelper.py COMMAND ARGS")
        print(VALID_COMMANDS)
        exit(0)
        
    command = sys.argv[1]

    if command == "proj" or command == "startproject":
        if os.path.isfile("manage.py"):
            echo_progress("manage.py found in this directory, will not create new project.")
            exit(0)
            
        project_name = sys.argv[2]

        if os.path.isdir(project_name):
            echo_progress("Project already exists. Aborting.")
            exit(0)

            
        project_dir = os.path.join(os.getcwd(), project_name)

        os.mkdir(project_name)    
        os.chdir(project_name)
        
        try:
            create_venv(os.getcwd())
        except FileExistsError:
            echo_progress("venv already exists")

        venv_scripts = os.path.join(os.getcwd(), 'venv', 'Scripts')
        venv_py = os.path.join(venv_scripts, "python.exe")
        venv_pip = os.path.join(venv_scripts, "pip.exe")

        echo_progress("Upgrading pip")
        subprocess.run([venv_py, "-m", "pip", "install", "--upgrade", "pip"])
        
        echo_progress("Installing packages with pip")
        subprocess.run([venv_pip, "install", "-r", os.path.join(RESOURCES_DIR, "requirements.txt")])


        venv_django_admin = os.path.join(venv_scripts, "django-admin.exe")

        try:
            echo_progress("Running django-admin")
            subprocess.run([venv_django_admin, "startproject", project_name, ".", "--verbosity", "2"])
            
        except:
            echo_progress("Django project already exists.")

            
        echo_progress("Copying .gitignore")
        shutil.copyfile(os.path.join(RESOURCES_DIR, "dotgitignore.txt"), ".gitignore")

        
        echo_progress("Touching manage.py commands: makemigrations, migrate, runserver")
        touch_filename = os.path.join(RESOURCES_DIR, "touchcontent.txt")
        shutil.copyfile(touch_filename, "makemigrations")
        shutil.copyfile(touch_filename, "migrate")
        shutil.copyfile(touch_filename, "runserver")
        shutil.copyfile(touch_filename, "createsuperuser")

        echo_progress("Extracting secrets")
        extract_secrets(project_name)
        

        # Generate ui app with static and index.html
        echo_progress("Generating ui app")
        create_app(project_dir, "ui", create_templates=False)
        distutils.dir_util.copy_tree(os.path.join(RESOURCES_DIR, "ui"), os.path.join(project_dir, "ui"))
        

        echo_progress("Substituting project's urls.py")
        shutil.copyfile(os.path.join(RESOURCES_DIR, "mainurls.py"), os.path.join(project_dir, project_name, "urls.py"))

        
        echo_progress("Copying ui/views.py")
        shutil.copyfile(os.path.join(RESOURCES_DIR, "uiviews.txt"), os.path.join(project_dir, "ui", "views.py"))

        
        echo_progress("Migrating default apps")
        subprocess.run([venv_py, 'manage.py', 'migrate'])

        
        echo_progress("Creating an initial Git repository. Add remote and push manually.")
        subprocess.run(["git", "init"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "djhelper"])

        
        echo_progress("End of proj creation")
        print()
        echo_progress("Now, run these commands:")
        echo_progress(f"cd {project_name}")
        echo_progress("source venv/Scripts/activate")
        echo_progress("python manage.py createsuperuser")
        
    elif command == 'app' or command == 'startapp':
        app_names = sys.argv[2:]
        project_dir = os.getcwd()
        
        for app_name in app_names:
            app_name = app_name.replace("/", "")
            create_app(project_dir, app_name)
        
    else:
        print("Unknown command", command)
        print(VALID_COMMANDS)
