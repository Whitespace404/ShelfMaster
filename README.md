# Guidelines

## 1. When you want to make changes
Before you can do this you must have the 
repository cloned in your local. See [below](#how-to-set-up-the-development-environment) to see 
how to do that.

Before you make changes, 
make sure you are in the correct working
directory by using the `cd` command, and
run 

```git
git pull origin master
```

before you make changes. This will update all the 
changes made to the remote version of the 
repository to the local version. 

Note: If you are currently working on a different branch of the repo, use

```bash
git pull origin <branch_name>
```
instead.


## 2. Once you have made changes
Once you have made your changes, create a branch for your changes using

```bash
git checkout <branch_name>
```

Then run 
```bash
git add .
```

to add your changes to the staging area

Then, use

```bash
git commit -m "<Enter a message here>"
```
The message is required, and must describe what
changes you made to the repository.

Once you have run that, push changes to the remote
using 

```bash
git push origin <branch_name>
```
Do not push to the `master` branch, regardless of 
how small your changes may be. You must create
a feature branch and create a pull request
to merge to the `master` branch instead. You will 
not be allowed to push to `master` anyway.

Once you have run the following commands, navigate 
to the Github repository, and you should be able to 
see the branch you created. You can create a pull
request to request to merge the branch again, or 
if you want to make more changes, you can repeat 
from [step 1.](#1-when-you-want-to-make-changes)

# How to set up the development environment

## 1. Clone the repository in your local.
 Run the 
following command after navigating to the 
directory you intend to clone the repo in.
```bash
git clone https://github.com/Whitespace404/ShelfMaster
```


This will create a clone of the current version of the repository in your system.

Only run this once at the beginning. Once you
have cloned the repo and have all the files in your 
system, you can simply run `git pull origin master`
 to get the latest version of the repository, and use 
[this](#1-when-you-want-to-make-changes) while 
contributing instead.

## 2. Create Virtual Environment
This project uses a virtual environment
to ensure that dependencies required by different
projects are kept distinct. You can create a 
virtual environment by running

```bash
python -m venv env
```

We shall use `env` as the name for our virtual 
environment, as is convention.

Please note that if the environment is created, you
should see a folder called `env` in this directory.
If you do, do not run this command again.

## 3. Enter Virtual Environment
You can enter the virtual environment created in 
the last step using the following command

```
env\Scripts\Activate.bat
```

This will add a header that says `(env)` before 
or above your command prompt, showing that you are
in the virtual environment. 

When you close the command prompt, you 
automatically exit the virtual environment.
To exit manually simply run

```bash
deactivate
```

You must make sure that you are in the virtual 
environment before you run the Python program.
You may get an `ImportError` if you are not. This
is because the modules used in the program 
are unresolved because we have installed them
within our virtual environment, and not in our
global Python installation. This is done to prevent 
package conflicts.


## 4. Install Python dependencies
This project requires Flask and various other
dependencies, which are external Python modules. 
These dependencies can be installed by running the following command. Make sure you are in the [virtual environment](#3-enter-virtual-environment) before running this.
```bash
pip install -r requirements.txt
```

If this does not work, make sure you have Python
and Pip installed properly. [This](https://youtu.be/AdUZArA-kZw?si=uzYZpuG0W-Zlshwv) video, may help, 
although *it is* intended for installation of the 
`Pygame` module, it holds good for Flask as well. 

Also note that you need not run this again if it is 
already installed. 

## 5. Start Server
Once you have completed all of the above steps and
are in the [virtual environment](#3-enter-virtual-environment), you can run the 
following command to start the Flask web server, 
and run the code.

```
python run.py
```

Once you have run the code, visit `localhost:5000` 
on a web browser to view it.

<hr>
