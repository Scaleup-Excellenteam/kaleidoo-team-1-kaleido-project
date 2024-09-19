from transcription import Transcriptor
from db_reader import DB 
DBPATH = 'db.txt'
if __name__ == "__main__":
    db = DB(DBPATH)
    for file in db.read_db():
        Transcriptor(file)