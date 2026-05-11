import os

from Track import BaseTrack
from DataBaseManager import DataBaseManager
from AudioEngine import AudioPlayer
from Track import TrackFactory
from Scanner import Scanner


class Init_system:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Init_system, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.track_factory = TrackFactory()
        self.data_manager = DataBaseManager(self.track_factory)
        self.scanner = Scanner(self.data_manager, self.track_factory)
        self.audio_player = None
        self.initialize_db()
        self._initialized = True

    def initialize_db(self):
        try:
            self.data_manager.create_table_tracks()
            self.data_manager.create_table_folders()
            self.data_manager.create_table_userstats()
        except Exception:
            print("Таблицы уже существуют, пропускаем...")

    def set_audio_engine(self, id):
        self.audio_player = AudioPlayer(device_id=id)

    def return_tracks(self):
        tracks = self.data_manager.get_all_tracks()
        return tracks

    def choose_track(self, track:BaseTrack):
        self.audio_player.load(track.filepath)








