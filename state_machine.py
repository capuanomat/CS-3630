
import sys
import cozmo
import datetime
import time

from lab1 import *

def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    robot.camera.color_image_enabled = False
    robot.camera.enable_auto_exposure()

    img_clf = ImageClassifier()
    train_classifier(img_clf)

    while True:
        time.sleep(0.5)
        latest_image = robot.world.latest_image
        new_image = latest_image.raw_image

        predicted_label = img_clf.predict_labels(new_image)

        print(predicted_label)

        robot.say_text(predicted_label).wait_for_completed()

        timestamp = datetime.datetime.now().strftime("%dT%H%M%S%f")
        new_image.save("_DAPHNE_IS_A_DAPHNE_" + timestamp + ".jpg")


def train_classifier(img_clf):
    # load images
    (train_raw, train_labels) = img_clf.load_data_from_folder('./train/')

    # convert images into features
    train_data = img_clf.extract_image_features(train_raw)

    # train model and test on training data
    img_clf.train_classifier(train_data, train_labels)

if __name__ == '__main__':
    cozmo.setup_basic_logging()

    try:
        cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)