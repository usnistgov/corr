"""Usage: run.py [--host=<host>] [--port=<port>] [--debug | --no-debug]

--host=<host>   set the host address or leave it to 0.0.0.0.
--port=<port>   set the port number or leave it to 5200.

"""
from cloud import app
if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='0.1dev')

    host = arguments['--host']
    port = arguments['--port']
    debug = not arguments['--no-debug']


    if not port: port = 5200
    if not host: host = '0.0.0.0'

    app.run(debug=debug, host=host, port=int(port), threaded=True)
