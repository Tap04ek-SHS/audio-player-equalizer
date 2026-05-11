import sqlite3
from Track import BaseTrack, TrackFactory

"""Попытка реализовать Singletone через декоратор"""




class DataBaseManager():
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataBaseManager, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect("music.db")
            cls._instance.cursor = cls._instance.conn.cursor()
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, TrackFactory: TrackFactory):
        if self._initialized:
            return
        self.track_factory = TrackFactory
    def create_table_tracks(self):
        self.cursor.execute("""CREATE TABLE TrackTable(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               path TEXT UNIQUE,
                               title TEXT,
                               author TEXT,
                               album TEXT,
                               genre TEXT,
                               duration INTEGER,
                               is_favourite INTEGER)""")

    def add_track(self,track: BaseTrack):
        """Принимает объект трека и добавляет его в бд"""
        query = """INSERT OR IGNORE INTO TrackTable(path, title, author,album, genre, duration) VALUES (?, ?, ?, ?, ?,?)"""


        track_cort = (track.filepath, track.title, track.author,track.album,track.genre, track.duration)
        self.cursor.execute(query, track_cort)
        self.conn.commit()

    def get_all_tracks(self):
        """Возвращаем все объекты track"""
        track_list = []
        query = """SELECT * FROM TrackTable"""
        self.cursor.execute(query)
        for track in self.cursor.fetchall():
            parsed_track = self.track_factory.create_from_db(filepath=track[1], title=track[2], author=track[3], album=track[4], genre=track[5], duration=track[6], is_favourite=track[7])
            track_list.append(parsed_track)
        return track_list

    def get_track(self, user_data):
        """Поиск трека по user_data(title, author)"""
        track_list = []
        user_data = '%' + user_data + '%'
        query = """SELECT * FROM TrackTable WHERE title LIKE ? OR author LIKE ?"""
        self.cursor.execute(query, (user_data, user_data))
        for track in self.cursor.fetchall():
            track_list.append(self.track_factory.create_from_db(filepath=track[1], title=track[2], author=track[3], album=track[4], genre=track[5], duration=track[6], is_favourite=track[7]))
        return track_list

    def make_favourite(self, params):
        self.cursor.execute("""UPDATE TrackTable
                               SET is_favourite = 1
                               WHERE path = ?""", (params,))
        self.conn.commit()

    def clear_table(self):
        self.cursor.execute("""DELETE FROM TrackTable""")
        self.conn.commit()





    def create_table_folders(self):
        self.cursor.execute("""CREATE TABLE FolderTable
                               (
                                   path TEXT UNIQUE
                               )""")
    def add_folder(self,folderpath):
        query = """INSERT OR IGNORE INTO FolderTable(path) VALUES (?)"""
        self.cursor.execute(query, (folderpath,))
        self.conn.commit()

    def get_all_folders(self):
        folder_list = []
        query = """SELECT * FROM FolderTable"""
        self.cursor.execute(query)
        for folder in self.cursor.fetchall():
            folder_list.append(folder[0])
        return folder_list


    def create_table_userstats(self):
        self.cursor.execute("""CREATE TABLE UserStatsTable(
            genre TEXT UNIQUE, 
            count INTEGER
        )
        """)
    def get_user_stats(self):
        stats_dict = {}
        query = """SELECT * FROM UserStatsTable"""
        self.cursor.execute(query)
        for stat in self.cursor.fetchall():
            stats_dict[stat[0]] = stat[1]
        return stats_dict
    def update_user_stats(self, track):
        query = """UPDATE UserStatsTable SET count = count + 1 WHERE genre = ?"""
        self.cursor.execute(query, (track.genre,))
        self.conn.commit()

    def get_recommendations(self, top):
        query = """SELECT * FROM UserStatsTable ORDER BY count DESC ?"""
        self.cursor.execute(query, (top,))
        stats = self.cursor.fetchall()
        return stats










