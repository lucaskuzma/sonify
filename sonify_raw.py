import math
import wave
from pathlib import Path

from PIL import Image


class Channel:
    def __init__(self):
        self.buffer = []


l_channel = Channel()
r_channel = Channel()
channels = [l_channel, r_channel]

path = Path("../../Jujo/cloud_05")
files = sorted(path.glob("*.png"))
samples_per_frame = 44100 / 30
scan_size = math.ceil(math.sqrt(samples_per_frame))
print(scan_size)

for file in files:

    print(file)

    image = Image.open(file).resize((scan_size, scan_size), resample=Image.BICUBIC)
    pixels = image.load()
    w, h = image.size

    print(pixels[w / 2, h / 2])

    for i in range(scan_size):
        for j in range(scan_size):

            x = i
            y = j
            sample = pixels[x, y][0] / 128  # 0..2
            sample = sample - 1  # -1..1

            if i * j >= samples_per_frame:
                break

            l_channel.buffer.append(sample)
            r_channel.buffer.append(sample)

# convert, normalize, and interleave channel buffers to byte array
audio_buffer = bytearray()
norm_factor = 0.95  # -0.22dB
scale = 32767.0 * norm_factor  # float to int

for step in range(len(channels[0].buffer)):
    for channel in channels:
        sample = int(scale * channel.buffer[step])
        bytes = sample.to_bytes(2, byteorder="little", signed=True)
        audio_buffer += bytes

# write to wav file
wav = wave.open("sound.wav", "w")
wav.setparams((2, 2, 44100, 0, "NONE", "not compressed"))
wav.writeframes(audio_buffer)
wav.close()
