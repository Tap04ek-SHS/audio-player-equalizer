import os
from DataBaseManager import DataBaseManager
from Track import *
class Scanner:
    def __init__(self, DataBase: DataBaseManager,TrackFactory: TrackFactory):
        self.DataBase = DataBase
        self.TrackFactory = TrackFactory
    def scan(self,folderpath: str):
        existing_paths = {row[0] for row in self.DataBase.get_all_tracks()}
        for root, dirs, files in os.walk(folderpath):
            for file in files:
                if file.lower().endswith((".mp3", ".mp4", ".ogg", ".wav", ".flac")):
                    try:
                        if file not in existing_paths:
                            filepath = os.path.join(root, file)
                            track = self.TrackFactory.create_from_file(filepath)
                            if track.duration > 0:
                                self.DataBase.add_track(track)
                                print(f"Добавлен трек: {track.title}")
                    except Exception as e:
                        print(e)




