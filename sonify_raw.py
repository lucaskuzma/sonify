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
        self._amp = 0.99 * self._amp + 0.01 * self.amp
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


l_channel = Channel(
    [
        Scanner(0.15, 559),
        Scanner(0.30, 449),
        Scanner(0.40, 339),
        Scanner(0.45, 229),
        Scanner(0.50, 119),
    ]
)

r_channel = Channel(
    [
        Scanner(0.50, 110),  # A
        Scanner(0.55, 220),  # A
        Scanner(0.60, 330),  # E
        Scanner(0.70, 440),  # A
        Scanner(0.85, 550),  # C#
    ]
)


channels = [l_channel, r_channel]
loudest = 0  # for normalization

path = Path("../dst_10")
files = sorted(path.glob("*.png"))


for file in files:

    print(file)

    image = Image.open(file).resize((40, 40), resample=Image.BICUBIC)
    pixels = image.load()
    w, h = image.size

    print(pixels[w / 2, h / 2])

    for i in range(40):
        for j in range(40):

            x = i
            y = j
            sample = pixels[x, y][0] / 128  # 0..2
            sample = sample - 1  # -1..1

            if i * j >= 44100 / 30:
                break

            l_channel.buffer.append(sample)
            r_channel.buffer.append(sample)

# convert, normalize, and interleave channel buffers to byte array
audio_buffer = bytearray()
# normfactor = 0.95 / loudest  # -0.22dB
# print(f"loudest sample: {loudest}, normalizing by: {normfactor}")
normfactor = 0.95
scale = 32767.0 * normfactor  # float to int

for step in range(len(channels[0].buffer)):
    for channel in channels:
        sample = int(scale * channel.buffer[step])
        # print(f'step {step} value: {channel.buffer[step]}, scaled: {sample}')
        byted = sample.to_bytes(2, byteorder="little", signed=True)
        audio_buffer += byted

# write to wav file
wav = wave.open("sound.wav", "w")
wav.setparams((2, 2, 44100, 0, "NONE", "not compressed"))
wav.writeframes(audio_buffer)
wav.close()
