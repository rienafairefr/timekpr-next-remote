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

# app.run(host="0.0.0.0", port=8080, use_reloader=True, extra_files=extra_files)


server = Server(app.wsgi_app)
for file in extra_files:
    server.watch(file)
server.serve()

