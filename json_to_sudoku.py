import json
import sys
import Math

from PIL import Image, ImageDraw

class Collider(object):

    def __init__(self, x1, y1, x2, y2):
        self.xMid = (x2 - x1) / 2 + x1
        self.yMid = (y2 - y1) / 2 + y1

        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        print('collider', x1, y1, x2, y2, ',', self.xMid, self.yMid, ',', self.x1, self.x2, self.y1, self.y2)

    def checkCollision(self, col):
        xCol = (self.x1 >= col.x1 and self.x1 <= col.x2) or (self.x2 >= col.x1 and self.x2 <= col.x2)
        yCol = (self.y1 >= col.y1 and self.y1 <= col.y2) or (self.y2 >= col.y1 and self.y2 <= col.y2)
        return xCol and yCol

    def resize(self):
        self.HALF_AVG_SIZE = ((self.x2 - self.x1) + (self.y2 - self.y1)) / 2
        self.xMid = (self.x2 - self.x1) / 2 + self.x1
        self.yMid = (self.y2 - self.y1) / 2 + self.y1

        self.x1 = self.xMid - self.HALF_AVG_SIZE
        self.x2 = self.xMid + self.HALF_AVG_SIZE
        self.y1 = self.yMid - self.HALF_AVG_SIZE
        self.y2 = self.yMid + self.HALF_AVG_SIZE


def doOCR(content):
    # Imports the Google Cloud client library
    from google.cloud import vision
    from google.cloud.vision import types

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    image = types.Image(content=content)

    response = client.text_detection(image=image)

    print(response)

    return response


def findSpacesBetweenHoriz(col1, col2):
    spaces = 0

    yAvg = ((col1.y2 - col1.y1) + (col2.y2 - col2.y1)) / 2 + (col1.y1 + col2.y1) / 2
    x0Mid = ((col1.x2 - col1.x1) / 2) + col1.x1
    xDiff = (col2.x2 - col2.x1)

    # Account for cases of the same column
    print(col2.x1, "<=", x0Mid)
    if (col2.x1 <= x0Mid):
        return -1

    for objs in range(2, 64):
        pastCldr = col1
        xDelta = (xDiff * 1.0) / objs
        for cldrs in range(0, objs):
            cldr = Collider(x0Mid + (cldrs * xDelta), yAvg, x0Mid + (cldrs + 1 * xDelta), yAvg)
            if (cldr.checkCollision(pastCldr) or cldr.checkCollision(cldr)):
                return spaces
            pastCldr = cldr
        spaces += 1
    return spaces

def findSpacesBetweenVert(col1, col2):
    spaces = 0

    xAvg = ((col1.x2 - col1.x1) + (col2.x2 - col2.x1)) / 2 + (col1.x1 + col2.x1) / 2
    y0Mid = ((col1.y2 - col1.y1) / 2) + col1.y1
    yDiff = (col2.y2 - col2.y1)

    # Account for cases of the same row
    print(col2.x1, "<=", y0Mid)
    if (col2.x1 <= y0Mid):
        return -1

    for objs in range(2, 64):
        pastCldr = col1
        yDelta = (yDiff * 1.0) / objs
        for cldrs in range(0, objs):
            cldr = Collider(xAvg, y0Mid + (cldrs * yDelta), xAvg, y0Mid + (cldrs + 1 * yDelta))
            if (cldr.checkCollision(pastCldr) or cldr.checkCollision(cldr)):
                return spaces
            pastCldr = cldr
        spaces += 1
    return spaces

def drawBounds2(image_file, vects):
    im = Image.open(image_file)

    draw = ImageDraw.Draw(im)

    draw.polygon([
        vects[1].x1, vects[1].y1,
        vects[1].x2, vects[1].y2,
        ], None, 'purple')

    im.save('./debug.jpg', 'JPEG')

def drawBounds(image_file, vects):
    im = Image.open(image_file)

    draw = ImageDraw.Draw(im)

    draw.polygon([
        vects[0].x, vects[0].y,
        vects[1].x, vects[1].y,
        vects[2].x, vects[2].y,
        vects[3].x, vects[3].y], None, 'red')

    im.save('./debug.jpg', 'JPEG')


def getAnchorVerticies(vertices):
    """Get the top left and bottom right vertices in that order."""
    return [
      dict(
        x= min([v.x for v in vertices]),
        y= min([v.y for v in vertices])
      ),
      dict(
        x= max([v.x for v in vertices]),
        y= max([v.y for v in vertices])
      )
    ]


def runDudoku():
    if len(sys.argv) != 1:
        with open(sys.argv[1]) as f:
            #data = json.load(f)
            data = doOCR(f.read())

            #annotations = data["responses"][0]["textAnnotations"]
            annotations = data.text_annotations

            # Create a collection of squares with strings and center x, y coords
            littleSquares = []
            for i in range(len(annotations)):
                #print(annotations[i])
                #print("Dest:", annotations[i]["description"])

                """
                print(annotations[i]["description"])
                vertices = annotations[i]["boundingPoly"]["vertices"]
                col = Collider(vertices[0]["x"], vertices[0]["y"], vertices[1]["x"], vertices[1]["y"])
                print(vertices[0]["x"], vertices[0]["y"], vertices[1]["x"], vertices[1]["y"], " to ",col.x1, col.y1, col.x2, col.y2)
                littleSquares.append((annotations[i]["description"], col))
                """

                print(i)
                print(annotations.__getitem__(i).description)
                if ("\n" in annotations.__getitem__(i).description):
                    continue
                vertices = annotations.__getitem__(i).bounding_poly.vertices
                #print(annotations.__getitem__(i).description, vertices[3].x, vertices[3].y, vertices[1].x, vertices[1].y)
                anchorVerts = getAnchorVerticies(vertices)
                print(annotations.__getitem__(i).description, anchorVerts)
                drawBounds('./debug.jpg', vertices)
                col = Collider(anchorVerts[0]["x"], anchorVerts[0]["y"], anchorVerts[1]["x"], anchorVerts[1]["y"])
                littleSquares.append((annotations.__getitem__(i).description, col))

            # Test data to make sure it only considers the digits
            toRemove = []
            #largestWidth = 0
            for i in range(len(littleSquares)):
                #largestWidth = max(largestWidth, littleSquares[i][1].x2)
                if (len(littleSquares[i][0]) > 0 and (littleSquares[i][0][0] < '0' or littleSquares[i][0][0] > '9')):
                    toRemove.append(littleSquares[i])
            for i in range(len(toRemove)):
                littleSquares.remove(toRemove[i])
            #largestWidth *= 1.25

            # Find any that contain multiple digits, and find out if they are going right or down then break it up into singulars
            appendToLittleSquares = []
            rmFromLittleSquares = []
            for i in range(len(littleSquares)):
                if (len(littleSquares[i][0]) > 1):
                    strlen = len(littleSquares[i][0])
                    print('wut?!',
                          littleSquares[i][1].x2, littleSquares[i][1].x1, littleSquares[i][1].y2, littleSquares[i][1].y1, 'wut moar', littleSquares[i][1].x2 - littleSquares[i][1].x1, littleSquares[i][1].y2 - littleSquares[i][1].y1)
                    # If it is heading right
                    if (littleSquares[i][1].x2 - littleSquares[i][1].x1 < littleSquares[i][1].y2 - littleSquares[i][1].y1):
                        ySize = littleSquares[i][1].y2 - littleSquares[i][1].y1
                        ySizePer = ySize // strlen
                        print('isit', littleSquares[i][1].y2, littleSquares[i][1].y1, ySize, strlen, ySizePer)

                        # Set the initial box then iterate to adjust the rest
                        for y in range(1, strlen):
                            # Set bounds and character

                            print('THERE', ySize, strlen, ySizePer, littleSquares[i][1].y1)

                            col = Collider(littleSquares[i][1].x1, littleSquares[i][1].y1 + ySizePer * y + 1, littleSquares[i][1].x2, littleSquares[i][1].y1 + ySizePer * (y + 1) + 1)
                            appendToLittleSquares.append((littleSquares[i][0][y], col))
                        rmFromLittleSquares.append(littleSquares[i])
                        col = Collider(littleSquares[i][1].x1, littleSquares[i][1].y1, littleSquares[i][1].x2, littleSquares[i][1].y1 + ySizePer)
                        appendToLittleSquares.append((littleSquares[i][0][0], col))
                    # If it is heading down
                    else:
                        xSize = littleSquares[i][1].x2 - littleSquares[i][1].x1
                        xSizePer = xSize // strlen

                        # Set the initial box then iterate to adjust the rest
                        littleSquares[i][1].x2 = littleSquares[i][1].x1 + xSizePer
                        for x in range(1, strlen):
                            # Set bounds and character
                            print('HERE', xSize, strlen, xSizePer, littleSquares[i][1].y1)

                            col = Collider(littleSquares[i][1].x1 + xSizePer * x + 1, littleSquares[i][1].y1, littleSquares[i][1].x1 + xSizePer * (x + 1) + 1, littleSquares[i][1].y2)
                            appendToLittleSquares.append((littleSquares[i][0][x], col))
                        rmFromLittleSquares.append(littleSquares[i])
                        print('abcd')
                        col = Collider(littleSquares[i][1].x1, littleSquares[i][1].y1, littleSquares[i][1].x1 + xSizePer, littleSquares[i][1].y2)
                        appendToLittleSquares.append((littleSquares[i][0][0], col))
            for i in range(len(appendToLittleSquares)):
                littleSquares.append(appendToLittleSquares[i])

            for i in range(len(rmFromLittleSquares)):
                littleSquares.remove(rmFromLittleSquares[i])

            for i in range(len(littleSquares)):
                littleSquares[i][1].resize()

                im = Image.open('./debug.jpg')

                draw = ImageDraw.Draw(im)

                draw.rectangle([
                    littleSquares[i][1].x1, littleSquares[i][1].y1,
                    littleSquares[i][1].x2, littleSquares[i][1].y2
                ], 'brown')

                im.save('./debug'+ str(i) +'.jpg', 'JPEG')

            # Sort the data by rows and then columns
            sortedSquares = []
            while (len(littleSquares) > 0):
                currIndexToPop = 0
                for i in range(1, len(littleSquares)):
                    # Check for the position relative to the current index to pop
                    if (littleSquares[i][1].y1 == littleSquares[currIndexToPop][1].yMid):
                        if (littleSquares[i][1].x1 <= littleSquares[currIndexToPop][1].xMid):
                            currIndexToPop = i
                    # If it's on a lower row it should be selected right away
                    elif (littleSquares[i][1].y1 < littleSquares[currIndexToPop][1].yMid):
                        currIndexToPop = i
                sortedSquares.append(littleSquares[currIndexToPop])
                littleSquares.pop(currIndexToPop)

            # All data thus far
            print("What survived the purge:")
            for i in range(len(sortedSquares)):
                drawBounds2('./debug.jpg', sortedSquares[i])
                print(sortedSquares[i])

            # Track smallest and largest entry in x and y
            if (len(sortedSquares) < 2):
                print("Found 1 valid entry. Exited incorrectly.")
                exit(-1)
            smallestXEntry = sortedSquares[0]
            largestXEntry = sortedSquares[0]
            smallestYEntry = sortedSquares[0]
            largestYEntry = sortedSquares[0]
            for i in range(len(sortedSquares)):
                if (smallestXEntry[1].x1 > sortedSquares[i][1].x1):
                    smallestXEntry = sortedSquares[i]
                if (largestXEntry[1].x2 < sortedSquares[i][1].x2):
                    largestXEntry = sortedSquares[i]
                if (smallestYEntry[1].y1 > sortedSquares[i][1].y1):
                    smallestYEntry = sortedSquares[i]
                if (largestYEntry[1].y2 < sortedSquares[i][1].y2):
                    largestYEntry = sortedSquares[i]

            # Find out size of min grid
            minGridDimen = 1
            minGridDimen = max(minGridDimen, findSpacesBetweenHoriz(smallestXEntry[1], largestXEntry[1]) + 2)
            print(minGridDimen, smallestXEntry[1].__dict__, largestXEntry[1].__dict__)
            print(minGridDimen, smallestYEntry[1].__dict__, largestYEntry[1].__dict__)

            im = Image.open('./debug.jpg')

            draw = ImageDraw.Draw(im)

            draw.rectangle([
                smallestXEntry[1].x1, smallestXEntry[1].y1,
                smallestXEntry[1].x2, smallestXEntry[1].y2
            ], 'orange')
            draw.rectangle([
                smallestYEntry[1].x1, smallestYEntry[1].y1,
                smallestYEntry[1].x2, smallestYEntry[1].y2
            ], 'green')
            draw.rectangle([
                largestXEntry[1].x1, largestXEntry[1].y1,
                largestXEntry[1].x2, largestXEntry[1].y2
            ], 'yellow')
            draw.rectangle([
                largestYEntry[1].x1, largestYEntry[1].y1,
                largestYEntry[1].x2, largestYEntry[1].y2
            ], 'blue')

            im.save('./debug.jpg', 'JPEG')

            minGridDimen = max(minGridDimen, findSpacesBetweenVert(smallestYEntry[1], largestYEntry[1]) + 2)
            print(minGridDimen)

            # Fill in a basic grid
            grid = []
            for i in range(minGridDimen):
                inner = []
                for j in range(minGridDimen):
                    inner.append(".")
                grid.append(inner)

            # Fill in the smallest x and y entries with guaranteed initial x/y and the other components from eachother
            grid[0][findSpacesBetweenVert(smallestYEntry[1], smallestXEntry[1]) + 1] = smallestXEntry[0]
            grid[findSpacesBetweenHoriz(smallestXEntry[1], smallestYEntry[1]) + 1][0] = smallestYEntry[0]

            # Find spaces between min x/y to place the rest of the entries in the grid
            for i in range(len(sortedSquares)):
                if (sortedSquares[i] == smallestXEntry or sortedSquares[i] == smallestYEntry):
                    continue
                else:
                    x = findSpacesBetweenHoriz(smallestXEntry[1], smallestYEntry[1]) + 1
                    y = findSpacesBetweenVert(smallestYEntry[1], smallestXEntry[1]) + 1
                    grid[x][y] = sortedSquares[i][0]

            '''
            fout = open("solved" + 0 + ".txt", "w")
            f.write(minGridDimen)
            f.write(" ")
            print(minGridDimen)
            for x in range(minGridDimen):
                for y in range(minGridDimen):
                    f.write(grid[x][y])
                    f.write(" ")
                    print(x, y, grid[x][y])
            '''

            if (minGridDimen < 9):
                for x in range(9 - minGridDimen):
                    for y in range(9 - minGridDimen):
                        fileName = x * 9 + y
                        renderGrid = []
                        for i in range(9):
                            subRenderGrid = []
                            for j in range(9):
                                  subRenderGrid[j] = "."
                            renderGrid.append(subRenderGrid)

                        for i in range(x, min(x + minGridDimen, 9)):
                            for j in range(y, min(y + minGridDimen, 9)):
                                renderGrid[i][j] = grid[i - x][j - y]

                        f.open("solved" + fileName + ".txt", "w")
                        f.write(minGridDimen)
                        f.write(" ")
                        for i in range(x, min(x + minGridDimen, 9)):
                            for j in range(y, min(y + minGridDimen, 9)):
                                f.write(renderGrid[i][j])
                                f.write(" ")
    else:
        print("Takes in a single file as input.")



if __name__ == '__main__':
    runDudoku()

