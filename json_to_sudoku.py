import json
import sys

from PIL import Image, ImageDraw

class Collider(object):

    def __init__(self, x1, y1, x2, y2):
        self.HALF_AVG_SIZE = ((x2 - x1) + (y2 - y1)) / 2
        self.xMid = (x2 - x1) / 2 + x1
        self.yMid = (y2 - y1) / 2 + y1

        self.x1 = self.xMid - self.HALF_AVG_SIZE
        self.x2 = self.xMid + self.HALF_AVG_SIZE
        self.y1 = self.yMid - self.HALF_AVG_SIZE
        self.y2 = self.yMid + self.HALF_AVG_SIZE

    def checkCollision(self, col):
        xCol = (self.x1 >= col.x1 and self.x1 <= col.x2) or (self.x2 >= col.x1 and self.x2 <= col.x2)
        yCol = (self.y1 >= col.y1 and self.y1 <= col.y2) or (self.y2 >= col.y1 and self.y2 <= col.y2)
        return xCol and yCol

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
    x0Mid = ((col1.x2 - col1.x1) / 2)
    xDiff = ((col2.x2 - col2.x1) / 2) - x0Mid

    # Account for cases of the same column
    print(col2.x1, "<=", col1.x1 + x0Mid)
    if (col2.x1 <= col1.x1 + x0Mid):
        return -1

    for objs in range(2, 64):
        pastCldr = col1
        for cldrs in range(0, objs):
            cldr = Collider(x0Mid + ((cldrs / objs) * xDiff), yAvg, x0Mid + (((cldrs + 1) / objs) * xDiff), yAvg)
            if (cldr.checkCollision(pastCldr) or cldr.checkCollision(cldr)):
                return spaces
            pastCldr = cldr
        spaces += 1
    return spaces

def findSpacesBetweenVert(col1, col2):
    spaces = 0

    xAvg = ((col1.x2 - col1.x1) + (col2.x2 - col2.x1)) / 2 + (col1.x1 + col2.x1) / 2
    y0Mid = ((col1.y2 - col1.y1) / 2)
    yDiff = ((col2.y2 - col2.y1) / 2) - y0Mid

    # Account for cases of the same row
    print(col2.y1, "<=", col1.y1 + y0Mid)
    if (col2.y1 <= col1.y1 + y0Mid):
        return -1

    for objs in range(2, 64):
        pastCldr = col1
        for cldrs in range(0, objs):
            cldr = Collider(xAvg, y0Mid + ((cldrs / objs) * yDiff), xAvg, y0Mid + (((cldrs + 1) / objs) * yDiff))
            if (cldr.checkCollision(pastCldr) or cldr.checkCollision(cldr)):
                return spaces
            pastCldr = cldr
        spaces += 1
    return spaces

def drawBounds(image_file, vects):
    im = Image.open(image_file)

    draw = ImageDraw.Draw(im)

    draw.polygon([
        vects[0].x, vects[0].y,
        vects[1].x, vects[1].y,
        vects[2].x, vects[2].y,
        vects[3].x, vects[3].y], None, 'red')

    im.save('./debug.jpg', 'JPEG')

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
                vertices = annotations.__getitem__(i).bounding_poly.vertices
                print(annotations.__getitem__(i).description, vertices[0].x, vertices[0].y, vertices[1].x, vertices[1].y)
                drawBounds('./debug.jpg', vertices)
                col = Collider(vertices[0].x, vertices[0].y, vertices[1].x, vertices[1].y)
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
            for i in range(len(littleSquares)):
                if (len(littleSquares[i][0]) > 1):
                    strlen = len(littleSquares[i][0])
                    # If it is heading right
                    if (littleSquares[i][1].x2 - littleSquares[i][1].x1 > littleSquares[i][1].y2 - littleSquares[i][1].y1):
                        ySize = littleSquares[i][1].y2 - littleSquares[i][1].y1
                        ySizePer = ySize / strlen

                        # Set the initial box then iterate to adjust the rest
                        littleSquares[i][1].y2 = littleSquares[i][1].y1 + ySizePer
                        for y in range(1, strlen):
                            # Set bounds and character
                            col = Collider(littleSquares[i][1].x1, littleSquares[i][1].y1 + ySizePer * y + 1, littleSquares[i][1].x2, littleSquares[i][1].y1 + ySizePer * (y + 1) + 1)
                            appendToLittleSquares.append(littleSquares[i][0][y], col)
                        littleSquares[i][0] = littleSquares[i][0][0]
                    # If it is heading down
                    else:
                        xSize = littleSquares[i][1].x2 - littleSquares[i][1].x1
                        xSizePer = xSize / strlen

                        # Set the initial box then iterate to adjust the rest
                        littleSquares[i][1].x2 = littleSquares[i][1].x1 + xSizePer
                        for x in range(1, strlen):
                            # Set bounds and character
                            col = Collider(littleSquares[i][1].x1 + xSizePer * x + 1, littleSquares[i][1].y1, littleSquares[i][1].x1 + xSizePer * (x + 1) + 1, littleSquares[i][1].y2)
                            appendToLittleSquares.append(littleSquares[i][0][x], col)
                        littleSquares[i][0] = littleSquares[i][0][0]
            for i in range(len(appendToLittleSquares)):
                littleSquares.append(appendToLittleSquares[i])

            # Sort the data by rows and then columns
            sortedSquares = []
            while (littleSquares.count() > 0):
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

            print(minGridDimen)
            for x in range(minGridDimen):
                for y in range(minGridDimen):
                    print(x, y, grid[x][y])
    else:
        print("Takes in a single file as input.")


if __name__ == '__main__':
    runDudoku()

