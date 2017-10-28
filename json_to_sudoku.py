import json
import sys

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
                col = Collider(vertices[0].x, vertices[0].y, vertices[1].x, vertices[1].y)
                littleSquares.append((annotations.__getitem__(i).description, col))

            # Test data to make sure it only considers the digits
            toRemove = []
            for i in range(len(littleSquares)):
                if (len(littleSquares[i][0]) > 0 and (littleSquares[i][0][0] < '0' or littleSquares[i][0][0] > '9')):
                    toRemove.append(littleSquares[i])
            for i in range(len(toRemove)):
                littleSquares.remove(toRemove[i])

            # Find any that contain multiple digits, and find out if they are going right or down then break it up into singulars
            for i in range(len(littleSquares)):
                if (len(littleSquares[i][0]) > 1):
                    # If it is heading right
                    if (littleSquares[i][1].x2 - littleSquares[i][1].x1 > littleSquares[i][1].y2 - littleSquares[i][1].y1):
                        ySize = littleSquares[i][1].y2 - littleSquares[i][1].y1
                    # If it is heading down
                    else:
                        xSize = littleSquares[i][1].x2 - littleSquares[i][1].x1

            # Safe to assume that data is ordered by rows and then columns

            # All data thus far
            print("What survived the purge:")
            for i in range(len(littleSquares)):
                print(littleSquares[i])

            # Track smallest and largest entry in x and y
            if (len(littleSquares) < 2):
                print("Found 1 valid entry. Exited incorrectly.")
                exit(-1)
            smallestXEntry = littleSquares[0]
            largestXEntry = littleSquares[0]
            smallestYEntry = littleSquares[0]
            largestYEntry = littleSquares[0]
            for i in range(len(littleSquares)):
                if (smallestXEntry[1].x1 > littleSquares[i][1].x1):
                    smallestXEntry = littleSquares[i]
                if (largestXEntry[1].x2 < littleSquares[i][1].x2):
                    largestXEntry = littleSquares[i]
                if (smallestYEntry[1].y1 > littleSquares[i][1].y1):
                    smallestYEntry = littleSquares[i]
                if (largestYEntry[1].y2 < littleSquares[i][1].y2):
                    largestYEntry = littleSquares[i]

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
            for i in range(len(littleSquares)):
                if (littleSquares[i] == smallestXEntry or littleSquares[i] == smallestYEntry):
                    continue
                else:
                    x = findSpacesBetweenHoriz(smallestXEntry[1], smallestYEntry[1]) + 1
                    y = findSpacesBetweenVert(smallestYEntry[1], smallestXEntry[1]) + 1
                    grid[x][y] = littleSquares[i][0]

            print(minGridDimen)
            for x in range(minGridDimen):
                for y in range(minGridDimen):
                    print(x, y, grid[x][y])

            """
            row = 0
            column = 0
            # Cover all cases, with breaks throughout
            for y in range(len(littleSquares) - 1):
                for x in range(len(littleSquares) - 1):
                    # Stop checking horizontal spaces if clearly on a different row
                    if ():
                        row += 1
                    else:
                        spaces = findSpacesBetweenHoriz(littleSquares[x][1], littleSquares[x + 1][1])
                        print("Horiz spaces between", x, y, "is", spaces)
            for y in range(len(littleSquares) - 1):
                for x in range(len(littleSquares) - 1):
                    spaces = findSpacesBetweenVert(littleSquares[x][1], littleSquares[x + 1][1])
                    print("Vertical spaces between", x, y, "is", spaces)
            """
    else:
        print("Takes in a single file as input.")


if __name__ == '__main__':
    runDudoku()

