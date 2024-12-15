from os import walk, path

from dotenv import load_dotenv
from livereload import Server

load_dotenv()
from web import app

extra_dirs = ['templates', 'static']

extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in walk(extra_dir):
        for filename in files:
            filename = path.join(dirname, filename)
            if path.isfile(filename):
                extra_files.append(filename)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.debug = True
server = Server(app.wsgi_app)
for file in extra_files:
    server.watch(file)
server.serve()

