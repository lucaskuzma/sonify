import math
import wave
from pathlib import Path

from PIL import Image


class Osc:
    def __init__(self, freq, amp):
        self.freq = freq
        self._amp = self.amp = amp
        self.phi = -1

    def step(self):
        self.phi += 1
        self._amp = .99 * self._amp + .01 * self.amp
        w = 2 * math.pi * self.freq / 44100.0
        return self._amp * math.sin(w * self.phi)


class Scanner:
    def __init__(self, pos, freq):
        self.pos = pos
        self.freq = freq
        self.osc = Osc(freq, 0)


class Channel:
    def __init__(self, scanners):
        self.scanners = scanners
        self.buffer = []


l_channel = Channel([
    Scanner(.15, 559),
    Scanner(.30, 449),
    Scanner(.40, 339),
    Scanner(.45, 229),
    Scanner(.50, 119),
])

r_channel = Channel([
    Scanner(.50, 110),  # A
    Scanner(.55, 220),  # A
    Scanner(.60, 330),  # E
    Scanner(.70, 440),  # A
    Scanner(.85, 550),  # C#
])


channels = [l_channel, r_channel]
loudest = 0  # for normalization

# path = Path("../temp/rnd_point_19c/out_a")
path = Path("../temp/rnd_point_16/out_c")
# path = Path("images")
files = sorted(path.glob('*.png'))

for file in files:

    print(file)

    image = Image.open(file)
    pixels = image.load()
    w, h = image.size

    print(pixels[w/2, h/2])

    for channel in channels:

        for scanner in channel.scanners:

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
        for channel in channels:
            sample = 0
            # mix output from scanner oscillators
            for scanner in channel.scanners:
                sample += scanner.osc.step()
            # track level for normalization
            if abs(sample) > loudest:
                loudest = abs(sample)
            channel.buffer.append(sample)


# convert, normalize, and interleave channel buffers to byte array
audio_buffer = bytearray()
normfactor = .95 / loudest  # -0.22dB
print(f'loudest sample: {loudest}, normalizing by: {normfactor}')
scale = 32767.0 * normfactor  # float to int
for step in range(len(channels[0].buffer)):
    for channel in channels:
        sample = int(scale * channel.buffer[step])
        # print(f'step {step} value: {channel.buffer[step]}, scaled: {sample}')
        byted = sample.to_bytes(2, byteorder='little', signed=True)
        audio_buffer += byted


# write to wav file
wav = wave.open('sound.wav', 'w')
wav.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
wav.writeframes(audio_buffer)
wav.close()
