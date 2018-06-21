import os
import sys

SECRET_KEY = '\x00(\x86N\x86D\xb4S|\xe3\xc0"\x15\xc9v\xd2c\xda7\xa8\xea\xaaD\x04'

if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    sys.path.insert(0, 'lib.zip')
else:
    if os.name == 'nt':
        os.name = None
        sys.platform = ''

from google.appengine.ext import vendor

vendor.add('lib')
