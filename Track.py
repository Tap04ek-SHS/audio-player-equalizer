from mutagen import File
import os
import mutagen

class Track:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_audio_file(self):
        audio = File(self.filepath)
        if audio is None:
            return None
        info = {
            'length': int(audio.info.length),
            'bitrate': getattr(audio.info, 'bitrate', None),
            'channels': getattr(audio.info, 'channels', None),
            'sample_rate': getattr(audio.info, 'sample_rate', None),
            'tags':{}
        }
        if audio.tags:
            for tag in audio.tags.keys():
                info['tags'][tag] = str(audio.tags[tag])
        return info

