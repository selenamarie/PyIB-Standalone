import threading
import _mysql
from settings import Settings

db = _mysql.connect(Settings.DATABASE_HOST, Settings.DATABASE_USERNAME, Settings.DATABASE_PASSWORD, Settings.DATABASE_DB)

database_lock = threading.Lock()

def FetchAll(query, method=1):
  global db
  
  db.query(query)
  r = db.use_result()
  return r.fetch_row(0, method)

def FetchOne(query, method=1):
  global db
  
  db.query(query)
  r = db.use_result()
  try:
    return r.fetch_row(1, method)[0]
  except:
    return None
