#!/usr/bin/env python
from phr_api import access_interface
from phr_api import app

access_interface.addroute()
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=50000)


