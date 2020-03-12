"""
import time
import simpleaudio as sa


perk = sa.WaveObject.from_wave_file('static/perkphase.wav')
horn = sa.WaveObject.from_wave_file('static/AIRHORNMLG.wav')
playbacks = []
def play_perk_music():
    stop_music()
    playback = perk.play()
    playbacks.append(playback)
def play_horn():
    stop_music()
    playback = horn.play()
    playbacks.append(playback)
def stop_music():
    for playback in playbacks:
        playback.stop()
"""
