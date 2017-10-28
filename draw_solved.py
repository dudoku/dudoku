
from PIL import Image, ImageDraw

# solvedVects is a list of {topX,topY,bottomX,bottomY}
def drawSolved(image_file, topX, topY, bottomX, bottomY, solved_vects):
    im = Image.open(image_file)

    draw = ImageDraw.Draw(im)

    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 10)

    for vect in solvedVects:
        # draw text, full opacity
        draw.text((vect.xMid, vect.yMid), vect.description, font=fnt, fill=(255,255,255,255))

    im.save('output.jpg', 'JPEG')

if __name__ == '__main__':
  drawSolved('./testImages/sudoku1.jpg', 6, 3, 209, 215, [{xMid:, yMid:}])

