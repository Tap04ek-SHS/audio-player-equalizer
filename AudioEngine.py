import sounddevice as sd
import numpy as np
import soundfile as sf
from scipy import signal
import threading
from collections import deque

class SimpleEQ:
    """Простой 3-полосный эквалайзер"""
    def __init__(self,sample_rate):
        self.fs = sample_rate

        self.bass_gain = 1.0
        self.mid_gain = 1.0
        self.treble_gain = 1.0

        self._update_filters()

    def _update_filters(self):
        if self.fs is None or self.fs <= 0:
            raise ValueError(f"Invalid sample rate: {self.fs}")

        nyquist = self.fs / 2

        bass_freq = min(100, nyquist * 0.99)
        mid_low = min(500, nyquist * 0.4)
        mid_high = min(2000, nyquist * 0.9)
        treble_freq = min(8000, nyquist * 0.99)

        self.bass_b, self.bass_a = signal.butter(
            1, bass_freq, btype='low', fs=self.fs, output='ba'
        )
        self.mid_b, self.mid_a = signal.butter(
            1, [mid_low, mid_high], btype='band', fs=self.fs, output='ba'
        )
        self.treble_b, self.treble_a = signal.butter(
            1, treble_freq, btype='high', fs=self.fs, output='ba'
        )


        self.bass_z = np.expand_dims(signal.lfilter_zi(self.bass_b, self.bass_a), -1)
        self.mid_z = np.expand_dims(signal.lfilter_zi(self.mid_b, self.mid_a), -1)
        self.treble_z = np.expand_dims(signal.lfilter_zi(self.treble_b, self.treble_a), -1)

    def set_gains(self, bass=None, mid=None, treble=None):
        if bass is not None:
            self.bass_gain = max(0.0, min(bass, 3.0))
        if mid is not None:
            self.mid_gain = max(0.0, min(mid,3.0))
        if treble is not None:
            self.treble_gain = max(0.0, min(treble,3.0))

    def process(self, chunk):
        if chunk.size == 0:
            return chunk

        if chunk.shape[1] != self.bass_z.shape[1]:
            self.bass_z = np.tile(self.bass_z[:, :1], (1, chunk.shape[1]))
            self.mid_z = np.tile(self.mid_z[:, :1], (1, chunk.shape[1]))
            self.treble_z = np.tile(self.treble_z[:, :1], (1, chunk.shape[1]))

        bass_f, self.bass_z = signal.lfilter(self.bass_b, self.bass_a, chunk, zi=self.bass_z, axis=0)
        mid_f, self.mid_z = signal.lfilter(self.mid_b, self.mid_a, chunk, zi=self.mid_z, axis=0)
        treble_f, self.treble_z = signal.lfilter(self.treble_b, self.treble_a, chunk, zi=self.treble_z, axis=0)

        result = bass_f * self.bass_gain + mid_f * self.mid_gain + treble_f * self.treble_gain

        max_val = np.max(np.abs(result))
        if max_val > 1.0:
            result = result / max_val * 0.95

        return np.nan_to_num(result)

class TimeStretch:
    """Time stretching с отдельным контролем скорости и высоты"""
    def __init__(self,sample_rate):
        self.fs = sample_rate

        self.speed = 1.0

        self.pitch = 1.0

        self.reverb_wet = 0.0
        self.reverb_decay = 0.5

        self.delay_samples = int(0.05 * sample_rate)
        self.reverb_buffer = deque(maxlen=self.delay_samples*4)
        for _ in range(self.delay_samples*4):
            self.reverb_buffer.append(0.0)

        self.resample_buffer = np.array([])

    def set_speed(self,speed):
        """Скорость воспроизведения (0.5 - 2.0)"""
        self.speed = max(0.25, min(speed, 4.0))
        print(f"Speed: {self.speed}x ({'slowed' if speed < 1 else 'sped up' if self.speed > 1 else 'normal'})")

    def set_pitch(self,pitch):
        """Высота тона (0.5 - 2.0)"""
        self.pitch = max(0.25, min(pitch, 2.0))
        print(f"Pitch: {self.pitch}x ({'lower' if self.pitch < 1 else 'higher' if self.pitch > 1 else 'normal'})")

    def set_reverb(self, wet, decay=0.5):
        """Реверб (wet 0.0-1.0, decay 0.0-0.9)"""
        self.reverb_wet = max(0.0, min(wet, 1.0))
        self.reverb_decay = max(0.0, min(decay, 0.9))
        print(f"Reverb: wet={self.reverb_wet}, decay={self.reverb_decay}")

    def process(self, chunk, target_frames):

        if self.speed != 1.0:
            current_len = len(chunk)
            new_len = max(1, int(current_len / self.speed))

            stretched = np.zeros((new_len, chunk.shape[1]))
            indices = np.linspace(0, current_len - 1, new_len)
            for ch in range(chunk.shape[1]):
                stretched[:, ch] = np.interp(indices, np.arange(current_len), chunk[:, ch])
        else:
            stretched = chunk

        if self.pitch != 1.0:
            current_len = len(stretched)
            temp_len = max(1, int(current_len / self.pitch))


            pitched = np.zeros((temp_len, stretched.shape[1]))
            indices = np.linspace(0, current_len - 1, temp_len)
            for ch in range(stretched.shape[1]):
                pitched[:, ch] = np.interp(indices, np.arange(current_len), stretched[:, ch])

            result = np.zeros((target_frames, pitched.shape[1]))
            final_indices = np.linspace(0, len(pitched) - 1, target_frames)
            for ch in range(pitched.shape[1]):
                result[:, ch] = np.interp(final_indices, np.arange(len(pitched)), pitched[:, ch])
        else:

            current_len = len(stretched)
            if current_len != target_frames:
                result = np.zeros((target_frames, stretched.shape[1]))
                indices = np.linspace(0, current_len - 1, target_frames)
                for ch in range(stretched.shape[1]):
                    result[:, ch] = np.interp(indices, np.arange(current_len), stretched[:, ch])
            else:
                result = stretched

        if self.reverb_wet > 0:
            output = np.zeros_like(result)
            for i in range(len(result)):
                dry = result[i]*(1-self.reverb_wet)

                echo = 0
                for j, delay in enumerate([self.delay_samples, self.delay_samples*2, self.delay_samples*3]):
                    if len(self.reverb_buffer) > delay:
                        idx = len(self.reverb_buffer) - delay
                        echo += self.reverb_buffer[idx] * (self.reverb_decay ** (j+1))
                wet = echo*self.reverb_wet
                output[i] = dry+wet

                self.reverb_buffer.append(result[i]+echo*0.3)
            result = output

        max_val = np.max(np.abs(result))
        if max_val > 1.0:
            result = result / max_val*0.95
        return result

class AudioPlayer:
    """Плеер с EQ + TimeStretch"""

    def __init__(self,device_id=None):
        self.device = device_id
        self.data = None
        self.fs = None
        self.current_frame = 0
        self.is_playing = False
        self.eq = None
        self.timestretch = None
        self.stream = None
        self.event = threading.Event()
        self.volume = 1.0

    def load(self, filename):
        try:
            self.data, self.fs = sf.read(filename, always_2d=True, dtype='float32')
        except Exception as e:
            print(f"Ошибка soundfile: {e}. Пробую librosa...")
            import librosa
            self.data, self.fs = librosa.load(filename, sr=None, mono=False)
            self.data = self.data.T

        if len(self.data) == 0:
            print("ОШИБКА: Файл пуст или не поддерживается!")
            return

        self.eq = SimpleEQ(self.fs)
        self.timestretch = TimeStretch(self.fs)
        self.current_frame = 0
        print(f"Загружено: {filename}, {self.fs}Hz, Каналов: {self.data.shape[1]}")

    def set_eq(self, bass = None, mid = None, treble = None):
        if self.eq:
            self.eq.set_gains(bass, mid, treble)

    def set_speed(self,speed):
        """Скорость воспроизведения"""
        if self.timestretch:
            self.timestretch.set_speed(speed)

    def set_pitch(self,pitch):
        """Высота тона отдельно"""
        if self.timestretch:
            self.timestretch.set_pitch(pitch)

    def set_reverb(self,wet,decay=0.5):
        """реверб"""
        if self.timestretch:
            self.timestretch.set_reverb(wet,decay)

    def _callback(self, outdata, frames, time, status):
        if status:
            print(f"Status: {status}")

        if not self.is_playing or self.data is None:
            outdata.fill(0)
            return
        if not self.is_playing or self.data is None:
            outdata[:] = 0
            return

        speed = self.timestretch.speed if self.timestretch else 1.0
        need_samples = int(frames*speed)

        start = self.current_frame
        end = min(start+need_samples, len(self.data))
        chunk = self.data[start:end]

        if len(chunk) == 0:
            outdata[:] = 0
            self.is_playing = False
            raise sd.CallbackStop()

        if len(chunk) < need_samples:
            padding = np.zeros((need_samples-len(chunk),chunk.shape[1]))
            chunk = np.vstack([chunk, padding])

        processed = self.eq.process(chunk)
        processed = self.timestretch.process(processed,frames)

        outdata[:] = processed.astype('float32')*self.volume


        self.current_frame += len(self.data[start:end])

    def play(self):
        if self.stream is None or not self.stream.active:
            try:
                self._create_stream(self.fs)
            except:
                print("Частота файла не поддерживается, пробую 48000 Гц")
                self._create_stream(48000)
        self.is_playing = True

    def _create_stream(self, samplerate):
        self.stream = sd.OutputStream(
            samplerate=samplerate,
            device=self.device,
            channels=self.data.shape[1],
            callback=self._callback,
            finished_callback=self.event.set,
            blocksize=4096
        )
        self.stream.start()

    def pause(self):
        self.is_playing = False

    def stop(self):
        self.is_playing = False
        self.current_frame = 0

    def seek(self, seconds):
        self.current_frame = int(seconds * self.fs)

    def wait(self):
        self.event.wait()

    def set_volume(self, value):
        self.volume = max(0.0, min(float(value), 1.0))
        print(f"Громкость: {int(self.volume * 100)}%")












