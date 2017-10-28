
def run_quickstart():
    # [START vision_quickstart]
    import io
    import os
    import sys
    import pickle

    # Imports the Google Cloud client library
    # [START migration_import]
    from google.cloud import vision
    from google.cloud.vision import types
    # [END migration_import]

    # Instantiates a client
    # [START migration_client]
    client = vision.ImageAnnotatorClient()
    # [END migration_client]

    # The name of the image file to annotate
    with io.open(sys.argv[1], 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image).text_annotations
    print(response)

    #print(json.dumps(response))
    # [END vision_quickstart]


if __name__ == '__main__':
    run_quickstart()
