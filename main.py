# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import re
import subprocess
import sys

import tornado.web

PORT = 8765


class MainPageHandler(tornado.web.RequestHandler):

    def initialize(self, base_url, ws_url):
        self.base_url = base_url
        self.ws_url = ws_url

    def get(self):
        return self.render("index.html", static=self.static_url,
                           ws_url=self.ws_url, base_url=self.base_url)


def main(argv):

    url = "http://localhost:%s" % PORT

    nb_command = [sys.executable, '-m', 'notebook', '--no-browser',
                  '--NotebookApp.allow_origin="%s"' % url]
    nb_server = subprocess.Popen(nb_command, stderr=subprocess.STDOUT,
                                 stdout=subprocess.PIPE)

    # wait for notebook server to start up
    while 1:
        line = nb_server.stdout.readline().decode('utf-8').strip()
        if not line:
            continue
        print("Browse to http://localhost:8765")
        print(line)
        if 'Jupyter Notebook is running at:' in line:
            base_url = re.search('(http.*?)$', line).groups()[0]
            ws_url = base_url.replace('http', 'ws')
            break

    handlers = [
        (r"/", MainPageHandler, dict(ws_url=ws_url, base_url=base_url)),
        (r'/(.*)', tornado.web.StaticFileHandler,
         {'path': '.'}),
    ]

    app = tornado.web.Application(handlers, static_path='build',
                                  template_path='.')

    app.listen(PORT, 'localhost')
    loop = tornado.ioloop.IOLoop.instance()
    print('Browse to http://localhost:%s' % PORT)
    try:
        loop.start()
    except KeyboardInterrupt:
        print(" Shutting down on SIGINT")
    finally:
        nb_server.kill()
        loop.close()

if __name__ == '__main__':
    main(sys.argv)
