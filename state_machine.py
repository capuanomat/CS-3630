
import sys
import cozmo
import datetime
import time
import numpy as np
from skimage import color

from Lab1_Soln import *

def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    robot.camera.color_image_enabled = False
    robot.camera.enable_auto_exposure()

    img_clf = ImageClassifier()
    train_classifier(img_clf)
    test_classifier(img_clf)

    while True:
        time.sleep(2)
        latest_image = robot.world.latest_image
        new_image = np.array(latest_image.raw_image)

        print("......................----------")
        print(new_image.shape)

        arr_image = np.array([new_image])

        print("......................----------")
        print(arr_image.shape)

        image_features = img_clf.extract_image_features(arr_image)

        
        predicted_label = img_clf.predict_labels(image_features)

        print(predicted_label)

        robot.say_text(predicted_label[0]).wait_for_completed()

        timestamp = datetime.datetime.now().strftime("%dT%H%M%S%f")

        temp_image = latest_image.raw_image
        temp_image.save("_DAPHNE_IS_A_DAPHNE_" + str(predicted_label[0]) + timestamp + ".jpg")


def train_classifier(img_clf):
    # load images
    (train_raw, train_labels) = img_clf.load_data_from_folder('./train/')

    # convert images into features
    train_data = img_clf.extract_image_features(train_raw)

    print(train_data)

    # train model and test on training data
    img_clf.train_classifier(train_data, train_labels)

def test_classifier(img_clf):

    (test_raw, test_labels) = img_clf.load_data_from_folder('./test/')

    test_data = img_clf.extract_image_features(test_raw)

    predicted_labels = img_clf.predict_labels(test_data)

    print("\nTraining results")
    print("=============================")
    print("Confusion Matrix:\n",metrics.confusion_matrix(test_labels, predicted_labels))
    print("Accuracy: ", metrics.accuracy_score(test_labels, predicted_labels))
    print("F1 score: ", metrics.f1_score(test_labels, predicted_labels, average='micro'))

if __name__ == '__main__':
    cozmo.setup_basic_logging()

    try:
        cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)