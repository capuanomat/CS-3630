import sys
import time
import cozmo
import datetime
from cozmo.util import degrees, distance_mm, speed_mmps

from Lab1_Soln import *

class RobotState:
    IDLE = 0
    DRONE = 1
    ORDER = 2
    INSPECTION = 3


def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    robot.camera.color_image_enabled = False
    robot.camera.enable_auto_exposure()

    # Getting & Training the classifier
    img_clf = ImageClassifier()
    train_classifier(img_clf)
    # test_classifier(img_clf)

    STATE = RobotState.IDLE

    while True:
        if STATE == RobotState.IDLE:
            STATE = execute_idle(robot, img_clf)
        elif STATE == RobotState.DRONE:
            robot_speak(robot, 'Drone')
            STATE = execute_drone(robot)
        elif STATE == RobotState.ORDER:
            robot_speak(robot, 'Order')
            STATE =execute_order(robot)
        elif STATE == RobotState.INSPECTION:
            robot_speak(robot, 'Inspection')
            STATE = execute_inspection(robot)
        else:
            print('Invalid state, please try again.')
            sys.exit()


def execute_idle(robot, img_clf):
    time.sleep(2)

    # Get the latest image in raw form and cast it as an array
    latest_image = robot.world.latest_image
    new_image = np.array(latest_image.raw_image)
    arr_image = np.array([new_image])

    # Extract the image features and predict the label from it
    image_features = img_clf.extract_image_features(arr_image)
    predicted_label = img_clf.predict_labels(image_features)

    # Print the predicted label and make the robot say it
    print("PREDICTED LABEL at: ", datetime.datetime.date())
    print(predicted_label)
    robot.say_text(predicted_label[0]).wait_for_completed()

    # Save the image (need to get the raw imagae again)
    timestamp = datetime.datetime.now().strftime("%dT%H%M%S%f")
    temp_image = latest_image.raw_image
    temp_image.save("image" + str(predicted_label[0]) + timestamp + ".jpg")

    if predicted_label[0] == "Drone":
        return RobotState.DRONE
    elif predicted_label[0] == "Order":
        return RobotState.ORDER
    elif predicted_label[0] == "Inspection":
        return RobotState.INSPECTION
    else:
        return RobotState.IDLE


def robot_speak(robot, speech):
    robot.say_text(speech).wait_for_completed()

"""
    (1) Locates one of the cubes
    (2) Picks up the cube
    (3) Drives forward with the cube for 10cm
    (4) Puts down cube
    (5) Drives backward 10cm (without cube)
    (6) Return to IDLE
"""
def execute_drone(robot):
    cube = robot.world.wait_for_observed_light_cube(include_existing=True)  # Include cubes that are already visible
    pickup_action = robot.pickup_object(cube, num_retries=5)  # Allow 5 retries in case of failure
    pickup_action.wait_for_completed()  # Wait for robot pickup action to complete
    # robot_drive(25, 25, duration=10)  # Drive forward for 10cm; TODO determine time for 10cm
    robot.do_drive(4)  # Drive forward 10cm (4 inches), try instead of above line

    setdown_action = robot.place_object_on_ground_here(cube, num_retries=5)  # Allow 5 retries in case of failure
    setdown_action.wait_for_completed()  # Wait for robot setdown action to complete
    robot.do_drive(-4)  # Drive backward 10cm (4 inches)

    return RobotState.IDLE  # Finally return to IDLE after execute_drone completed


"""
    Use the drive_wheels function to have robot drive in 
        a circle with a radius of 10cm, then return to IDLE.
    TODO: figure out how long the duration needs to be
"""
def execute_order(robot):
    robot.drive_wheels(25, 50)  # TODO: test/modify these params for 10cm radius
    return RobotState.IDLE

"""
    (1) Robot drives in square with each side = ~20cm
    *(2) Robot continuously raises and lowers lift while driving in 2-3 second (slow) intervals
    (3) Lower lift at end of INSPECTION
    (4) Return to IDLE
"""
def execute_inspection(robot):
    for i in range(4):  # for each side of the square
        inspection_helper(robot)
    robot.set_lift_height(0.0, in_parallel=False).wait_for_completed()  # Lower lift at the end
    return RobotState.IDLE


def inspection_helper(robot):
    robot.set_lift_height(1.0, in_parallel=True)
    robot.drive_straight(distance_mm(200), speed_mmps(50), in_parallel=True).wait_for_completed()
    robot.set_lift_height(0, in_parallel=True)
    robot.turn_in_place(degrees(90), in_parallel=True).wait_for_completed()


def train_classifier(img_clf):
    # load images
    (train_raw, train_labels) = img_clf.load_data_from_folder('./train/')

    # convert images into features
    train_data = img_clf.extract_image_features(train_raw)

    print(train_data)

    # train model and test on training data
    img_clf.train_classifier(train_data, train_labels)


if __name__ == '__main__':
    cozmo.setup_basic_logging()

    try:
        cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)