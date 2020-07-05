import math
import random
import struct
import wave

from PIL import Image
from pathlib import Path


class Osc:
    def __init__(self, freq, amp):
        self.freq = freq
        self.amp = amp
        self.phi = -1

    def step(self):
        self.phi += 1
        w = 2 * math.pi * self.freq / 44100.0
        return int(self.amp * 32767.0 * math.sin(w * self.phi))


class Scanner:
    def __init__(self, pos, freq):
        self.pos = pos
        self.freq = freq
        self.osc = Osc(freq, 0)

# array of channels
# in each channel, define column to sample as portion of image width
scanners = [
        [
            Scanner(.2, 660),
            Scanner(.3, 440),
            Scanner(.4, 220),
            Scanner(.5, 110),
        ],
        [
            Scanner(.5, 110),
            Scanner(.6, 450),
            Scanner(.7, 230),
            Scanner(.8, 670),
        ]
    ]

audio_buffer = bytearray()

# path = Path("../temp/rnd_point_19c/out_a")
path = Path("images")
files = sorted(path.glob('*.png'))

for file in files:
    
    print(file)

    image = Image.open(file)
    pixels = image.load()
    w, h = image.size
    
    print(pixels[w/2, h/2])

    for channel in scanners:

        for scanner in channel:
        
            # calculate amplitude at this image location
            amp = 0
            for y in range(h):
                amp += pixels[int(w * scanner.pos), y][0]  # just grabbing red component
            amp /= h
            amp /= 256
            print(f'pos: {scanner.pos}, amp: {amp}')

            # set oscillator amplitude
            scanner.osc.amp = amp

    # fill 44100/30=1470 frames of the audio buffer
    for step in range(1470):
        for channel in scanners:
            sample = 0
            for scanner in channel:
                sample += scanner.osc.step()
            byted = (sample).to_bytes(2, byteorder='little', signed=True)
            audio_buffer += byted

wav = wave.open('tone_03.wav', 'w')
wav.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))

wav.writeframes(audio_buffer)
wav.close()
