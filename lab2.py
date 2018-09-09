from lab1 import *
import sys
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
import time


'''
    PARTNERS: Daphne Chen and Matthieu Capuano
'''

# Enum that represents the 4 possible different states in the FSM
class RobotState:
    IDLE = 0
    DRONE = 1
    ORDER = 2
    INSPECTION = 3


class StateMachine:

    def __init__(self, state, robot: cozmo.robot.Robot):
        rs = RobotState()
        self.state = rs.IDLE
        self.robot = robot

    def run_robot(self):
        self.robot.camera.image_stream_enabled = True
        self.robot.camera.color_image_enabled = False
        self.robot.camera.enable_auto_exposure()

        latest_image = self.robot.world.latest_image
        new_image = latest_image.raw_image
        new_image.save("./imgs/" + 'TEST' + "_" + timestamp + ".bmp")
        time.sleep(5)


        self.state = IDLE

        while(True):  # Execute until someone terminates Terminator
            if self.state == RobotState.IDLE:
                self.robot_speak('Idle')
                self.execute_idle()
            elif self.state == RobotState.DRONE:
                self.robot_speak('Drone')
                self.execute_drone()
            elif self.state == RobotState.ORDER:
                self.robot_speak('Order')
                self.execute_order()
            elif self.state == RobotState.INSPECTION:
                self.robot_speak('Inspection')
                self.execute_inspection()
            else:
                print('Invalid state, please try again.')
                sys.exit()

    '''
        Helper method that allows Cozmo to say the name of the 
            recognized symbol
        @param: speech is the text that Cozmo will say out loud
    '''
    def robot_speak(self, speech):
        self.robot.say_text(speech).wait_for_completed()


    '''
        Helper method that allows Cozmo to drive at specified speed 
        @param: lwheel_speed is the speed of Cozmo's left wheel in mm/s
        @param: rwheel_speed is the speed of Cozmo's right wheel in mm/s
        @param: duration is the time (optional param) that Cozmo will drive 
            Varying these parameters can allow Cozmo to travel in a straight
                line versus a circle (at different radii)
    '''
    def robot_drive(self, lwheel_speed, rwheel_speed, duration):
        self.robot.drive_wheels(lwheel_speed, rwheel_speed, duration)


    '''
        Monitors a stream of images (in grayscale) from the camera and classifies it
            using the SVM from lab1.
        Robot will say name of recognized symbol then switch to
            that state.
    '''
    def execute_idle(self):
        symbol_classifier = lab1.ImageClassifier()



    '''
        (1) Locates one of the cubes
        (2) Picks up the cube
        (3) Drives forward with the cube for 10cm
        (4) Puts down cube
        (5) Drives backward 10cm (without cube)
        (6) Return to IDLE
    '''
    def execute_drone(self):
        cube = self.robot.world.wait_for_observed_light_cube(include_existing=True)  # Include cubes that are already visible
        pickup_action = self.robot.pickup_object(cube, num_retries=5)  # Allow 5 retries in case of failure
        pickup_action.wait_for_completed()  # Wait for robot pickup action to complete
        # self.robot_drive(25, 25, duration=10)  # Drive forward for 10cm; TODO determine time for 10cm
        self.robot.do_drive(4)  # Drive forward 10cm (4 inches), try instead of above line

        setdown_action = self.robot.place_object_on_ground_here(cube, num_retries=5)  # Allow 5 retries in case of failure
        setdown_action.wait_for_completed()  # Wait for robot setdown action to complete
        self.robot.do_drive(-4)  # Drive backward 10cm (4 inches)

        self.state = IDLE  # Finally return to IDLE after execute_drone completed


    '''
        Use the drive_wheels function to have robot drive in 
            a circle with a radius of 10cm, then return to IDLE.
        TODO: figure out how long the duration needs to be
    '''
    def execute_order(self):
        self.robot.drive_wheels(25, 50)  # TODO: test/modify these params for 10cm radius
        self.state = IDLE


    '''
        (1) Robot drives in square with each side = ~20cm
        *(2) Robot continuously raises and lowers lift while driving in 2-3 second (slow) intervals
        (3) Lower lift at end of INSPECTION
        (4) Return to IDLE
    '''
    def execute_inspection(self):
        drive1 = self.robot.drive_straight(distance_mm(200), speed_mmps(50), in_parallel=True) # Drive for 20cm (200mm); fix speed if necessary
        turn1 = self.robot.turn_in_place(degrees(90))  # Turn 90 degrees to begin next part of square
        raise1 = self.robot.set_lift_height(1.0)  # Raise lift
        lower1 = self.robot.set_lift_height(0.0)  # Lower lift
        drive1.wait_for_completed()
        turn1.wait_for_completed()
        raise1.wait_for_completed()
        lower1.wait_for_completed()

        drive2 = self.robot.drive_straight(distance_mm(200), speed_mmps(50), in_parallel=True)  # Drive for 20cm (200mm); fix speed if necessary
        turn2 = self.robot.turn_in_place(degrees(90))  # Turn 90 degrees to begin next part of square
        raise2 = self.robot.set_lift_height(1.0)  # Raise lift
        lower2 = self.robot.set_lift_height(0.0)  # Lower lift
        drive2.wait_for_completed()
        turn2.wait_for_completed()
        raise2.wait_for_completed()
        lower2.wait_for_completed()

        drive3 = self.robot.drive_straight(distance_mm(200), speed_mmps(50), in_parallel=True)  # Drive for 20cm (200mm); fix speed if necessary
        turn3 = self.robot.turn_in_place(degrees(90)).wait_for_completed()  # Turn 90 degrees to begin next part of square
        raise3 = self.robot.set_lift_height(1.0)  # Raise lift
        lower3 = self.robot.set_lift_height(0.0)  # Lower lift
        drive3.wait_for_completed()
        turn3.wait_for_completed()
        raise3.wait_for_completed()
        lower3.wait_for_completed()

        drive4 = self.robot.drive_straight(distance_mm(200), speed_mmps(50), in_parallel=True)  # Drive for 20cm (200mm); fix speed if necessary
        raise4 = self.robot.set_lift_height(1.0)
        lower4 = self.robot.set_lift_height(0.0)

        self.robot.set_lift_height(0.0, in_parallel=False)  # Lower lift at the end
        self.state = IDLE


def main():
    try:
        cozmo.connect(run)
        sm = StateMachine()
        sm.run_robot()

    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)


if __name__ == "__main__":
    main()




'''
Sources used:

http://cozmosdk.anki.com/docs/generated/cozmo.camera.html#cozmo.camera.Camera  # Used for idle

https://www.pydoc.io/pypi/cozmo-1.0.1/autoapi/world/index.html#world.World.wait_for_observed_light_cube  # Used for execute_drone method

https://github.com/anki/cozmo-python-sdk/blob/master/examples/tutorials/01_basics/05_motors.py  # Used for execute_order; drive method

https://github.com/anki/cozmo-python-sdk/blob/master/examples/tutorials/04_cubes_and_objects/05_cube_stack.py  # Used for execute_drone method; example usage of SDK functions

https://github.com/anki/cozmo-python-sdk/blob/master/examples/tutorials/04_cubes_and_objects/07_lookaround.py  # Used for execute_drone method; for set down cube function
https://www.pydoc.io/pypi/cozmo-1.0.1/autoapi/robot/index.html#robot.Robot.place_object_on_ground_here  # also this

https://github.com/anki/cozmo-python-sdk/blob/master/docs/source/tutorial-advanced.rst  # For do_drive method within execute_drone

https://github.com/anki/cozmo-python-sdk/blob/master/examples/tutorials/01_basics/02_drive_and_turn.py  # For execute_inspection method of driving in a square and turning

https://github.com/anki/cozmo-python-sdk/blob/master/examples/tutorials/01_basics/05_motors.py  # Used for execute_inspection to raise/lower lift

'''