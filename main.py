
import sounddevice as sd
import os
from Init_system import Init_system

if __name__ == '__main__':
    info = sd.query_devices(1)
    print(f"Device 1: {info}")
    print(f"Output channels: {info['max_output_channels']}")  # Должно быть > 0
    print(os.path.splitext('/home/tapochek/Загрузки/Casey Edwards. - Bury the Light (Hardstyle Version).mp3')[1])
    print(sd.query_devices())
    print("Доступные устройства:")
    for i, dev in enumerate(sd.query_devices()):
        if dev['max_output_channels'] > 0:
            print(f"{i}: {dev['name']}")

    dev_id = int(input("Введи номер устройства: "))


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
    init_system = Init_system()
    try:
        init_system.data_manager.clear_table()
        init_system.scanner.scan("/home/tapochek/Загрузки/")
        init_system.set_audio_engine(dev_id)
        for index, track in enumerate(init_system.return_tracks()):
            print(f"id {index}: {track.title}")
        track_id = int(input("Введите id нужного трека:"))
        init_system.audio_player.load(init_system.return_tracks()[track_id].filepath)
        

    except Exception as e:
        print(e)

    while True:
        cmd = input("\n> ").strip().split()
        if not cmd:
            continue

        action = cmd[0]

        if action == "play":
            init_system.audio_player.play()
        elif action == "pause":
            init_system.audio_player.pause()
        elif action == "stop":
            init_system.audio_player.stop()
        elif action == "bass":
            init_system.audio_player.set_eq(bass=float(cmd[1]))
        elif action == "mid":
            init_system.audio_player.set_eq(mid=float(cmd[1]))
        elif action == "treble":
            init_system.audio_player.set_eq(treble=float(cmd[1]))
        elif action == "speed":
            init_system.audio_player.set_speed(float(cmd[1]))
        elif action == "pitch":
            init_system.audio_player.set_pitch(float(cmd[1]))
        elif action == "volume":
            init_system.audio_player.set_volume(float(cmd[1]))
        elif action == "reverb":
            wet = float(cmd[1])
            decay = float(cmd[2]) if len(cmd) > 2 else 0.5
            init_system.audio_player.set_reverb(wet, decay)

        # Пресеты
        elif action == "slowed":
            init_system.audio_player.set_speed(0.8)
            init_system.audio_player.set_pitch(0.9)
            init_system.audio_player.set_reverb(0.3, 0.6)
        elif action == "spedup":
            init_system.audio_player.set_speed(1.5)
            init_system.audio_player.set_pitch(1.0)
            init_system.audio_player.set_reverb(0.0)
        elif action == "nightcore":
            init_system.audio_player.set_speed(1.3)
            init_system.audio_player.set_pitch(1.2)
            init_system.audio_player.set_reverb(0.1)
        elif action == "normal":
            init_system.audio_player.set_speed(1.0)
            init_system.audio_player.set_pitch(1.0)
            init_system.audio_player.set_reverb(0.0)
            init_system.audio_player.set_eq(1.0, 1.0, 1.0)

        elif action == "quit":
            init_system.audio_player.stop()
            break
    print("Готово")
