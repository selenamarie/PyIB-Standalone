import cgi
import datetime
import time
import pickle
import _mysql

from settings import Settings
from database import *

def setBoard(dir):
  """
  Sets the board which the script is operating on by filling Settings._BOARD
  with the data from the db.  Once the data is set, the configuration field from
  the database is unpickled and placed in a pseudo-field called settings.
  All settings have a default value which will remain that way until the script
  changes and updates the board by calling updateBoardSettings()
  This allows new settings to be added for each board without requiring any SQL
  queries to be ran
  """
  board = FetchOne("SELECT * FROM `boards` WHERE `dir` = '" + _mysql.escape_string(dir) + "' LIMIT 1")
  
  board['settings'] = {
    'anonymous': 'Anonymous',
    'forced_anonymous': False,
    'disable_subject': False,
    'tripcode_character': '!',
  }
  
  if board['configuration'] != '':
    configuration = pickle.loads(board['configuration'])
    board['settings'].update(configuration)
    
  Settings._BOARD = board
  
  return board
  
def updateBoardSettings():
  """
  Pickle the board's settings and store it in the configuration field
  """
  board = Settings._BOARD
  configuration = pickle.dumps(board['settings'])
  
  db.query("UPDATE `boards` SET `configuration` = '" + _mysql.escape_string(configuration) + "' WHERE `id` = " + board['id'] + " LIMIT 1")

def timestamp(t=None):
  """
  Create MySQL-safe timestamp from the datetime t if provided, otherwise create
  the timestamp from datetime.now()
  """
  if not t:
    t = datetime.datetime.now()
  return int(time.mktime(t.timetuple()))

def get_post_form(environ):
  """
  Process input sent to WSGI through a POST method and output it in an easy to
  retrieve format: dictionary of dictionaries in the format of {key: value}
  """
  wsgi_input = environ['wsgi.input']
  post_form = environ.get('wsgi.post_form')
  if (post_form is not None
    and post_form[0] is wsgi_input):
    return post_form[2]
  # This must be done to avoid a bug in cgi.FieldStorage
  environ.setdefault('QUERY_STRING', '')
  fs = cgi.FieldStorage(fp=wsgi_input,
                        environ=environ,
                        keep_blank_values=1)
  new_input = InputProcessed()
  post_form = (new_input, wsgi_input, fs)
  environ['wsgi.post_form'] = post_form
  environ['wsgi.input'] = new_input
  
  """
  Pre-"list comprehension" code (benchmarked as being five times slower):
  formdata = {}
  fs = dict(fs)
  for key in fs:
    formdata[key] = str(fs[key].value)
  """
  
  formdata = dict([(key, fs[key].value) for key in dict(fs)])
  
  #import sys
  #sys.exit(repr(formdata))
  
  return formdata

class InputProcessed(object):
  def read(self):
    raise EOFError('The wsgi.input stream has already been consumed')
  readline = readlines = __iter__ = read