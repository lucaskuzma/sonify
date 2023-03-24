`sonify.py`

Runs through a directory of PNG images and for every image generates 1/30 seconds of sound. Sound is determined by a set of Scanner objects, each of which is initialized with an x position, normalized 0..1, and a frequency. Each Scanner reads a column from the image, the total brightness of which, in the red channel, determines the amplitude of the Scanner's oscillator.

generate audio:

    python sonify.py

generate video:

    ffmpeg -framerate 30 -i pg_%04d.png -pix_fmt yuv420p -s 1080x1080 ../video.mp4

add audio to video:

    ffmpeg -i video.mp4 -i sound.wav -c:v copy -map 0:v:0 -map 1:a:0 -c:a aac -b:a 192k -strict -2 output.mp4

`sonify_raw.py`

Similar to the above, but more of a crude dump of image data to audio buffer.

`sonify_add.py`

Additive synth, with $size^2$ oscillators, i.e. one for each pixel in a downsampled image. Pan is determined by `x` and pitch by `y`.

    python sonify.py ../some/path

`make_test.py`

Writes a series of test images to a `test` directory. Use these to test the synths above.

### Python Shenanigans

You might want to use `pipenv`.

    pipenv install
    pipenv shell
    python sonify.py
