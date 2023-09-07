# SHELF MASTER
This is a Library Management System.

# Quickstart

To run the server, open this folder using command prompt and execute:

```powershell
env\Scripts\activate.bat
```
Once you've run that run
```
python shelfmaster.py
```
to run the server.

The admin login credentials is as follows

```
Username: rahulreji
Password: power
```
# How to set up the development environment

## 1. Clone the repository in your local.
 Run the following command after navigating to the directory you intend to clone the repo in.
```bash
git clone https://github.com/Whitespace404/ShelfMaster
```

This will create a clone of the current version of the repository in your system.

## 2. Create Virtual Environment
This project uses a virtual environment to ensure that dependencies required by different
projects are kept distinct. You can create a virtual environment by running

```bash
python -m venv env
```

We shall use `env` as the name for our virtual environment, as is convention.

## 3. Enter Virtual Environment
You can enter the virtual environment created in the last step using the following command

```
env\Scripts\Activate.bat
```

This will add a header that says `(env)` before or above your command
prompt, showing that you are in the virtual environment. 

When you close the command prompt, you automatically exit the virtual environment. To exit manually simply run

```bash
deactivate
```

You must make sure that you are in the virtual environment 
before you run the Python program. You may get an `ModuleNotFoundError`
if you are not. This is because the modules used in the program are unresolved because we have installed them
within our virtual environment, and not in our global Python installation. This is done to prevent package conflicts.


## 4. Install Python dependencies
This project requires Flask and various other dependencies, which are external Python modules. 
These dependencies can be installed by running the following command. Make sure you are in the [virtual environment](#3-enter-virtual-environment) before running this.
```bash
pip install -r requirements.txt
```

If this does not work, make sure you have Python and Pip installed properly. [This](https://youtu.be/AdUZArA-kZw?si=uzYZpuG0W-Zlshwv) video, may help,  although *it is* intended for installation of the 
`Pygame` module, it holds good for Flask as well. 

Also note that you need not run this again if it is already installed. 

## 5. Start Server
Once you have completed all of the above steps and are in the [virtual environment](#3-enter-virtual-environment), you can run the following command to start the Flask web server, and run the code.

```
python run.py
```

Once you have run the code, visit `localhost:5000`  on a web browser to view it.

<hr>
