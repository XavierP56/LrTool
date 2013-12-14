Lr Tool.
An experiment with Python, AngularJS, Lightroom database and OpenCV.

GPL v3
Copyright Xavier Pouyollon 2013.

- Display statical datas of the used focal in a browser.
- Do facial recognition and add tags in the database : Backup your database ! Use at your own risks !
- Developped on Mac but should work without troubles on Windows and even Linux since Python and HTML based
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
Use a browser on http://localhost:8080/index.html. Since it is an HTML front-end, you can use it from your ipad to
recognize the faces in your collections !

Files/train contains the various pictures of that are used to recognize the faces.
Files/img is a temporary working directory

To use the facial reco:
- Create a "Faces" keyword. Create the names you want to recognize as children of "Faces".
- Put your images in a collection.
