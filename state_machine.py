
import sys
import cozmo
import datetime
import time


def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    robot.camera.color_image_enabled = False
    robot.camera.enable_auto_exposure()

    while True:
        time.sleep(1)
        latest_image = robot.world.latest_image
        new_image = latest_image.raw_image

        timestamp = datetime.datetime.now().strftime("%dT%H%M%S%f")
        new_image.save("_DAPHNE_IS_A_DAPHNE_" + timestamp + ".jpg")


if __name__ == '__main__':
    cozmo.setup_basic_logging()

    try:
        cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)