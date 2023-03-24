import math
import wave
from pathlib import Path
import click
from tqdm import trange
import itertools
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

samples_per_frame = int(44100 / 30)


# slow and not band-limited, but sounds cool in this situation
def square(radians):
    radians = radians % (2 * math.pi)
    return 1 if radians < math.pi else 0


@click.command()
@click.argument("path", type=click.Path(exists=True), default="test")
@click.option(
    "-s",
    "--size",
    "scan_size",
    default=4,
    help="Square root of the number of oscillators",
)
def main(path, scan_size):
    path = Path(path)
    files = sorted(path.glob("*.png"))
    phi = 0
    count = len(files) - 1
    print(f"{count} files to process in `{path}`")

    n_oscillators = scan_size * scan_size
    print(f"{n_oscillators} oscillators activated")

    freqs = []
    for y in range(scan_size):
        # frequency based on y coordinate, 3520 is 440 * 8
        freq = 20 + 3500 * (scan_size - y) / scan_size
        freqs.append(freq)
    print(f"frequencies: {freqs}")

    for frame in trange(count):
        # load current and next image
        file_1 = files[frame]
        file_2 = files[frame + 1]

        image_1 = Image.open(file_1).resize(
            (scan_size, scan_size), resample=Image.BICUBIC
        )
        image_2 = Image.open(file_2).resize(
            (scan_size, scan_size), resample=Image.BICUBIC
        )

        pixels_1 = image_1.load()
        pixels_2 = image_2.load()

        w, h = image_1.size

        # iterate over samples in this frame
        for sample_index in trange(samples_per_frame, leave=False):
            l_sample = r_sample = 0
            # iterate over image pixels
            for x, y in itertools.product(range(scan_size), repeat=2):
                amp_1 = pixels_1[x, y][0] / 256  # 0..1
                amp_2 = pixels_2[x, y][0] / 256  # 0..1

                # linterp
                amp = amp_1 + (amp_2 - amp_1) * (sample_index / samples_per_frame)

                # calculate sample contribution from this pixel

                freq = freqs[y]
                w = 2 * math.pi * freq / 44100.0

                # scale sample by amplitude and n_oscillators
                sample = amp * math.sin(w * phi) / n_oscillators
                # sample = amp * square(w * phi) / n_oscillators

                l_sample += sample * (1 - x / scan_size)
                r_sample += sample * (x / scan_size)

            l_channel.buffer.append(l_sample)
            r_channel.buffer.append(r_sample)
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


if __name__ == "__main__":
    main()
