Lr Tool.
An experiment with Python, AngularJS, Lightroom database and OpenCV.

GPL v3
Copyright Xavier Pouyollon 2013.

- Display statical datas of the used focal in a browser.
- Do facial recognition and add tags in the database : Backup your database ! Use at your own risks !
- Developped on Mac but should work with some minor tweaks on Windows and even Linux since Python and HTML based
- Ipad can be used as interface since it is a local web application.

Dependencies (use home-brew to install)

- Python
- Python-bottle
- Python-bottle-sql
- CherryPi
- OpenCV
- Bower

cd Files
bower install : This will install all the needed Javascript libraries.

Start the python server.
Use a browser on http://localhost:8080/demo/index.html. Since it is an HTML front-end, you can use it from your ipad to
recognize the faces in your collections !

Files/train contains the various pictures of that are used to recognize the faces.
Files/img is a temporary working directory

To use the facial reco:
- Create a "Faces" keyword. Create the names you want to recognize as children of "Faces".
- Put your images in a collection.

It will display a small version of the head : Select in the dropdown menu the correct face and click on Tag.
The more face it will learn, the better it will become at guessing who is who.
Go back in lightroom : Tags are set in the pictures !

Instructions for Macintosh installation:
----------------------------------------
The following should work on a fresh Maverick installation.
Open a terminal and follow these instructions:

git help
==> You will get a dialog box asking to install the command-line tools. Install them.

ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
==> It will ask for your password and will install brew

brew doctor
brew install cmake
brew tap homebrew/science
brew install opencv
==> Be patient !

brew install dcraw
brew install node
brew install python
pip install bottle
pip install bottle-sqlite
pip install CherryPy

npm install -g coffee-script
npm install -g bower

You can now download the lrtool
cd Documents
git clone  https://github.com/XavierP56/LrTool.git
cd LrTool/Files
bower install
cd ..

You should be ready now !
python lrtool.py <full path to a .lrcat file from Lightroom>
Open a browser at:
http://localhost:8080/demo/index.html

