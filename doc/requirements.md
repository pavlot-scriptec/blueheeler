
Installing the system provided PyGObject:

        Open a terminal

        Execute sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgtksourceview-5-dev

        Change the directory to where your hello.py script can be found (e.g. cd Desktop)

        Run python3 hello.py

Installing from PyPI with pip:

        Open a terminal and enter your virtual environment

        Execute sudo apt install libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 to install the build dependencies and GTK

        Execute pip3 install pycairo to build and install Pycairo

        Execute pip3 install PyGObject to build and install PyGObject

        Change the working directory to where your hello.py script can be found

        Run python3 hello.py

