from Track import Track
import sounddevice as sd
from AudioEngine import AudioPlayer
if __name__ == '__main__':
    info = sd.query_devices(1)
    print(f"Device 1: {info}")
    print(f"Output channels: {info['max_output_channels']}")  # Должно быть > 0
    track = Track('/home/tapochek/Загрузки/Casey Edwards. - Bury the Light (Hardstyle Version).mp3')
    print(track.get_audio_file())
    print(sd.query_devices())
    print("Доступные устройства:")
    for i, dev in enumerate(sd.query_devices()):
        if dev['max_output_channels'] > 0:
            print(f"{i}: {dev['name']}")

    dev_id = int(input("Введи номер устройства: "))

    player = AudioPlayer(dev_id)
    player.load("/home/tapochek/Загрузки/Casey Edwards. - Bury the Light (Hardstyle Version).mp3")

    print("\n=== КОМАНДЫ ===")
    print("play, pause, stop")
    print("bass/mid/treble 0.0-3.0  — EQ")
    print("speed 0.5-2.0     — скорость (0.5=медленно, 2.0=быстро)")
    print("pitch 0.5-2.0     — высота (0.5=низко, 2.0=высоко)")
    print("reverb 0.0-1.0    — эхо")
    print("volume 0.0 - 1.0")
    print("presets:")
    print("  slowed   — speed 0.8, pitch 0.9, reverb 0.3")
    print("  spedup   — speed 1.5, pitch 1.0")
    print("  nightcore — speed 1.3, pitch 1.2")
    print("  normal   — сброс всего")
    print("quit")


    while True:
        cmd = input("\n> ").strip().split()
        if not cmd:
            continue

        action = cmd[0]

        if action == "play":
            player.play()
        elif action == "pause":
            player.pause()
        elif action == "stop":
            player.stop()
        elif action == "bass":
            player.set_eq(bass=float(cmd[1]))
        elif action == "mid":
            player.set_eq(mid=float(cmd[1]))
        elif action == "treble":
            player.set_eq(treble=float(cmd[1]))
        elif action == "speed":
            player.set_speed(float(cmd[1]))
        elif action == "pitch":
            player.set_pitch(float(cmd[1]))
        elif action == "volume":
            player.set_volume(float(cmd[1]))
        elif action == "reverb":
            wet = float(cmd[1])
            decay = float(cmd[2]) if len(cmd) > 2 else 0.5
            player.set_reverb(wet, decay)

        # Пресеты
        elif action == "slowed":
            player.set_speed(0.8)
            player.set_pitch(0.9)
            player.set_reverb(0.3, 0.6)
        elif action == "spedup":
            player.set_speed(1.5)
            player.set_pitch(1.0)
            player.set_reverb(0.0)
        elif action == "nightcore":
            player.set_speed(1.3)
            player.set_pitch(1.2)
            player.set_reverb(0.1)
        elif action == "normal":
            player.set_speed(1.0)
            player.set_pitch(1.0)
            player.set_reverb(0.0)
            player.set_eq(1.0, 1.0, 1.0)

        elif action == "quit":
            player.stop()
            break

    print("Готово")
