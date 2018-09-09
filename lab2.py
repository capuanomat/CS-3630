from lab1 import *
import sys
import cozmo

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
        action = self.robot.pickup_object(cube, num_retries=5)  # Allow 5 retries in case of failure
        action.wait_for_completed()  # Wait for robot action to complete
        self.robot_drive(25, 25, duration=10)
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
        (2) Robot continuously raises and lowers lift while driving in 2-3 second slow intervals
        (3) Lower lift at end of INSPECTION
        (4) Return to IDLE
    '''
    def execute_inspection(self):
        self.state = IDLE



def main():
    sm = StateMachine()
    sm.run_robot()

if name == "__main__":
    main()


'''
Sources used:

http://cozmosdk.anki.com/docs/generated/cozmo.camera.html#cozmo.camera.Camera  # Used for idle

https://www.pydoc.io/pypi/cozmo-1.0.1/autoapi/world/index.html#world.World.wait_for_observed_light_cube  # Used for execute_drone method

https://github.com/anki/cozmo-python-sdk/blob/master/examples/tutorials/01_basics/05_motors.py  # Used for execute_order; drive method

https://github.com/anki/cozmo-python-sdk/blob/master/examples/tutorials/04_cubes_and_objects/05_cube_stack.py  # Used for execute_drone method; example usage of SDK functions

'''