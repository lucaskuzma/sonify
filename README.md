
generate audio:

	python sonify.py 


generate video:

	ffmpeg -framerate 30 -i pg_%04d.png -pix_fmt yuv420p -s 1080x1080 ../video.mp4


add audio to video:

	ffmpeg -i video.mp4 -i sound.wav -c:v copy -map 0:v:0 -map 1:a:0 -c:a aac -b:a 192k -strict -2 output.mp4
