from mutagen import File
import os
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
class BaseTrack:
    def __init__(self, filepath=None, title=None, author=None, is_favourite=None, duration=None, album=None,
                 genre=None):
        self.title = title
        self.author = author
        self.album = album
        self.genre = genre
        self.is_favourite = is_favourite
        self.duration = duration
        self.filepath = filepath
    def parse_metadata(self):
        pass


class MP4Track(BaseTrack):
    def __init__(self, filepath, title=None, author=None, is_favourite=None, duration=None, album=None, genre=None):
        super().__init__(filepath, title, author, is_favourite, duration, album, genre)

    def parse_metadata(self):
        track = MP4(self.filepath)
        self.duration = int(getattr(track.info, 'length', 0))
        if hasattr(track, 'tags') and track.tags:
            tags = track.tags
            self.title = "".join(track.get('©nam', ['']))
            self.author = "".join(tags.get('©ART', ['']))
            self.album = "".join(tags.get('©alb', ['']))
            self.genre = "".join(tags.get('©gen', ['']))
        if self.title is None:
            self.title = os.path.basename(self.filepath)


class OggVorbisTrack(BaseTrack):
    def __init__(self, filepath, title=None, author=None, is_favourite=None, duration=None, album=None,genre=None):
        super().__init__(filepath, title, author, is_favourite, duration, album, genre)

    def parse_metadata(self):
        track = OggVorbis(self.filepath)
        self.duration = int(getattr(track.info, 'length', 0))
        if hasattr(track, 'tags') and track.tags:
            tags = track.tags
            self.title = "".join(tags.get('title', ['']))
            self.author = "".join(tags.get('artist', ['']))
            self.album = "".join(tags.get('album', ['']))
            self.genre = "".join(tags.get('genre', ['']))
        if self.title is None:
            self.title = os.path.basename(self.filepath)


class MP3Track(BaseTrack):
    def __init__(self, filepath, title=None, author=None, is_favourite=None, duration=None, album=None, genre=None):
        super().__init__(filepath, title, author, is_favourite, duration, album, genre)

    def parse_metadata(self):
        track = MP3(self.filepath)
        self.duration = int(getattr(track.info, 'length', 0))
        if hasattr(track, 'tags') and track.tags:
            self.title = "".join(track.get('TIT2', ['']))
            self.author = "".join(track.get('TPE1', ['']))
            self.album = "".join(track.get('TALB', ['']))
            self.genre = "".join(track.get('TCON', ['']))
        if self.title is None:
            self.title = os.path.basename(self.filepath)


class FlACTrack(BaseTrack):
    def __init__(self, filepath, title=None, author=None, is_favourite=None, duration=None, album=None, genre=None):
        super().__init__(filepath, title, author, is_favourite, duration, album, genre)

    def parse_metadata(self):
        track = FLAC(self.filepath)
        self.duration = int(getattr(track.info, 'length', 0))
        if hasattr(track, 'tags') and track.tags:
            tags = track.tags
            self.title = "".join(tags.get('title', ['']))
            self.author = "".join(tags.get('artist', ['']))
            self.album = "".join(tags.get('album', ['']))
            self.genre = "".join(tags.get('genre', ['']))
        if self.title is None:
            self.title = os.path.basename(self.filepath)


class TrackFactory():
    def __init__(self):
        self.registry = {
            '.mp4': MP4Track,
            '.ogg': OggVorbisTrack,
            '.mp3': MP3Track,
            '.flac': FlACTrack,
        }
    def create_from_file(self,filepath):
        extension = os.path.splitext(filepath)[1].lower()
        cls = self.registry.get(extension)
        if cls is None:
            return None
        track = cls(filepath)
        track.parse_metadata()
        return track

    def create_from_db(self, **kwargs):
        filepath = kwargs.pop('filepath')
        extension = os.path.splitext(filepath)[1].lower()
        cls = self.registry.get(extension, BaseTrack)
        return cls(filepath=filepath, **kwargs)

    def register_format(self,extension, Track):
        self.registry[extension] = Track







