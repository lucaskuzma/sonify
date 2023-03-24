from PIL import Image, ImageDraw

size = 512
test_dir = "test"
count = 60

for i in range(count):
    image = Image.new("RGBA", (size, size), "black")
    draw = ImageDraw.Draw(image)
    x = i * size / count
    y = i * size / count
    r = 40
    draw.ellipse((x - r, y - r, x + r, y + r), fill="white")
    # draw.point((100, 100), 'red')
    s = str(i).zfill(4)
    image.save(f"{test_dir}/{s}.png")
