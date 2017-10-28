import json
import sys

class Collider(object):

    def __init__(self, x1, y1, x2, y2):
        self.HALF_AVG_SIZE = ((x2 - x1) + (y2 - y1)) / 2
        xMid = (x2 - x1) / 2
        yMid = (y2 - y1) / 2

        self.x1 = xMid - self.HALF_AVG_SIZE
        self.x2 = xMid + self.HALF_AVG_SIZE
        self.y1 = yMid - self.HALF_AVG_SIZE
        self.y2 = yMid + self.HALF_AVG_SIZE

    def checkCollision(self, col):
        xCol = (self.x1 >= col.x1 and self.x1 <= col.x2) or (self.x2 >= col.x1 and self.x2 <= col.x2)
        yCol = (self.y1 >= col.y1 and self.y1 <= col.y2) or (self.y2 >= col.y1 and self.y2 <= col.y2)
        return xCol and yCol

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

            xMin = 0
            xMax = 0
            yMin = 0
            yMax = 0
            for i in range(len(littleSquares)):
                xMin = min(xMin, littleSquares[i][1])
                xMax = max(xMax, littleSquares[i][1])
                yMin = min(yMin, littleSquares[i][2])
                yMax = max(yMax, littleSquares[i][2])


    else:
        print("Takes in a single file as input.")
