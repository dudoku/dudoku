import json
import sys

class Collider(object):

    def __init__(self, x1, y1, x2, y2):
        self.HALF_AVG_SIZE = ((x2 - x1) + (y2 - y1)) / 2
        self.xMid = (x2 - x1) / 2
        self.yMid = (y2 - y1) / 2

        self.x1 = self.xMid - self.HALF_AVG_SIZE
        self.x2 = self.xMid + self.HALF_AVG_SIZE
        self.y1 = self.yMid - self.HALF_AVG_SIZE
        self.y2 = self.yMid + self.HALF_AVG_SIZE

    def checkCollision(self, col):
        xCol = (self.x1 >= col.x1 and self.x1 <= col.x2) or (self.x2 >= col.x1 and self.x2 <= col.x2)
        yCol = (self.y1 >= col.y1 and self.y1 <= col.y2) or (self.y2 >= col.y1 and self.y2 <= col.y2)
        return xCol and yCol

def findSpacesBetweenHoriz(col1, col2):
    spaces = 0

    yAvg = ((col1.y2 - col1.y1) + (col2.y2 - col2.y1)) / 2 + (col1.y1 + col2.y1) / 2
    x0Mid = ((col1.x2 - col1.x1) / 2)
    xDiff = ((col2.x2 - col2.x1) / 2) - x0Mid
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
    for objs in range(2, 64):
        pastCldr = col1
        for cldrs in range(0, objs):
            cldr = Collider(xAvg, y0Mid + ((cldrs / objs) * yDiff), xAvg, y0Mid + (((cldrs + 1) / objs) * yDiff))
            if (cldr.checkCollision(pastCldr) or cldr.checkCollision(cldr)):
                return spaces
            pastCldr = cldr
        spaces += 1
    return spaces

if __name__ == '__main__':
    if True:
    #if len(sys.argv) != 1:
        with open("test.json") as f:
        #with open(sys.argv[1]) as f:
            data = json.load(f)
            annotations = data["responses"][0]["textAnnotations"]

            # Create a collection of squares with strings and center x, y coords
            littleSquares = []
            for i in range(len(annotations)):
                #print(annotations[i])
                #print("Dest:", annotations[i]["description"])
                print(annotations[i]["description"])
                vertices = annotations[i]["boundingPoly"]["vertices"]
                col = Collider(vertices[0]["x"], vertices[0]["y"], vertices[1]["x"], vertices[1]["y"])
                littleSquares.append((annotations[i]["description"], col))

            # Test data to make sure it only considers the digits
            toRemove = []
            for i in range(len(littleSquares)):
                if (littleSquares[i][0] < '0' or littleSquares[i][0] > '9'):
                    toRemove.append(littleSquares[i])
            for i in range(len(toRemove)):
                littleSquares.remove(toRemove[i])

            # Safe to assume that data is ordered by rows and then columns

            # All data thus far
            print("What survived the purge:")
            for i in range(len(littleSquares)):
                print(littleSquares[i])

            # Cover all cases, with breaks throughout
            for y in range(len(littleSquares) - 1):
                for x in range(len(littleSquares) - 1):
                    spaces = findSpacesBetweenHoriz(littleSquares[x][1], littleSquares[x + 1][1])
                    print("Horiz spaces between", x, y, "is", spaces)
            for y in range(len(littleSquares) - 1):
                for x in range(len(littleSquares) - 1):
                    spaces = findSpacesBetweenVert(littleSquares[x][1], littleSquares[x + 1][1])
                    print("Vertical spaces between", x, y, "is", spaces)
    else:
        print("Takes in a single file as input.")
