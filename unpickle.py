
def run_quickstart():
    # [START vision_quickstart]
    import io
    import os
    import sys
    import pickle

    # The name of the image file to annotate
    with io.open(sys.argv[1], 'rb') as image_file:
        print(pickle.load(image_file))


    #print(json.dumps(response))
    # [END vision_quickstart]


if __name__ == '__main__':
    run_quickstart()
