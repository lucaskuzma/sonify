import math
import wave
from pathlib import Path

from PIL import Image

"""
Sonify a directory of images.

Scales the image to a `scan_size`, and uses pixel intensities of the new image to control (`scan_size * scan_size`) oscillators.
"""


class Channel:
    def __init__(self):
        self.buffer = []


l_channel = Channel()
r_channel = Channel()
channels = [l_channel, r_channel]

path = Path("../../Jujo/cloud_05")
files = sorted(path.glob("*.png"))
samples_per_frame = int(44100 / 30)
scan_size = 16
print(f"{scan_size * scan_size} oscillators activated")
phi = 0

for frame in range(len(files) - 1):
    print(f"frame {frame}")
    # load current and next image
    file_1 = files[frame]
    file_2 = files[frame + 1]

    image_1 = Image.open(file_1).resize((scan_size, scan_size), resample=Image.BICUBIC)
    image_2 = Image.open(file_2).resize((scan_size, scan_size), resample=Image.BICUBIC)

    pixels_1 = image_1.load()
    pixels_2 = image_2.load()

    w, h = image_1.size

    # iterate over samples in this frame
    for sample in range(samples_per_frame):
        # iterate over image pixels
        for i in range(scan_size):
            for j in range(scan_size):
                # in case we want to do any coordinate mapping
                x = i
                y = j

                amp_1 = pixels_1[x, y][0] / 256  # 0..1
                amp_2 = pixels_2[x, y][0] / 256  # 0..1

                # linterp
                amp = amp_1 + (amp_2 - amp_1) * (sample / samples_per_frame)

                freq = 20 + 20000 * (scan_size - y) / scan_size
                w = 2 * math.pi * freq / 44100.0
                sample = amp * math.sin(w * phi)

                l_channel.buffer.append(sample * (1 - x / scan_size))
                r_channel.buffer.append(sample * x / scan_size)
        phi += 1

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
