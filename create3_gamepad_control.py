import sys
import sys
from inputs import get_gamepad
import math
import threading
from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3


class Button(object):

    
    def __init__(self, name, deadzone = 0, modifier = 0, analog_press_sensitivity = 0.5):
        self.name = name
        self.value = None
        self.prev_value = None
        self.value = 0
        self.deadzone = deadzone
        self.modifier = modifier
        self.down_state = False
        self.analog_press_sensitivity = analog_press_sensitivity
    def action(self, value):        
        self.prev_value = self.value

        if(self.deadzone > 0 and self.modifier > 0):
            self.value = self.check_deadzone(value / self.modifier)
        else:
            self.value = value

    def is_pressed(self):
        return self.value != None and self.value > self.analog_press_sensitivity

    def is_released(self):
        return self.value != None and self.value < 1 - self.analog_press_sensitivity

    def sate_changed(self):
        return self.prev_value != None and self.prev_value != self.value
    
    def is_pressed_ignore_repeat(self):
        ret = None
        if(self.is_pressed() and self.down_state == False):
            ret = self.down_state = True
        elif(self.is_released() and self.down_state == True):
            ret = self.down_state = False
        return ret

    def check_deadzone(self, joystick_val):
        if(joystick_val > self.deadzone or joystick_val < -self.deadzone):
            return joystick_val
        else:
            return 0
        
class Controller(object):            

    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    JOYSTICK_LEFT_Y = 'ABS_Y'
    JOYSTICK_LEFT_X = 'ABS_X'
    JOYSTICK_RIGHT_Y = 'ABS_RY'
    JOYSTICK_RIGHT_X = 'ABS_RX'
    BUTTON_LEFT_TRIGGER = 'ABS_Z'
    BUTTON_RIGHT_TRIGGER = 'ABS_RZ'
    BUTTON_LEFT_BUMPER = 'BTN_TL'
    BUTTON_RIGHT_BUMPER = 'BTN_TR'
    BUTTON_A = 'BTN_SOUTH'
    BUTTON_Y = 'BTN_NORTH'
    BUTTON_X = 'BTN_WEST'
    BUTTON_B = 'BTN_EAST'
    BUTTON_THUMB_L = 'BTN_THUMBL'
    BUTTON_THUMB_R ='BTN_THUMBR'
    BUTTON_START = 'BTN_SELECT'
    BUTTON_SELECT = 'BTN_START'
    BUTTON_DPAD_X_AXIS = 'ABS_HAT0X'
    BUTTON_DPAD_Y_AXIS ='ABS_HAT0Y'

    def __init__(self, deadzone = 0, daemon_running = False):
        
        self.deadzone = deadzone
        self.daemon_running = daemon_running
        
        self.joystick_left_y = Button(self.JOYSTICK_LEFT_Y,deadzone,Controller.MAX_JOY_VAL)
        self.joystick_left_x = Button(self.JOYSTICK_LEFT_X,deadzone,Controller.MAX_JOY_VAL)
        self.joystick_right_y = Button(self.JOYSTICK_RIGHT_Y,deadzone,Controller.MAX_JOY_VAL)
        self.joystick_right_x = Button(self.JOYSTICK_RIGHT_X,deadzone,Controller.MAX_JOY_VAL)
        self.button_left_trigger = Button(self.BUTTON_LEFT_TRIGGER,deadzone,Controller.MAX_TRIG_VAL)
        self.button_right_trigger = Button(self.BUTTON_RIGHT_TRIGGER,deadzone,Controller.MAX_TRIG_VAL)
        self.button_left_bumper = Button(self.BUTTON_LEFT_BUMPER)
        self.button_right_bumper = Button(self.BUTTON_RIGHT_BUMPER)
        self.button_a = Button(self.BUTTON_A)
        self.button_y = Button(self.BUTTON_Y)
        self.button_x = Button(self.BUTTON_X)
        self.button_b = Button(self.BUTTON_B)
        self.button_thumb_l = Button(self.BUTTON_THUMB_L)
        self.button_thumb_r = Button(self.BUTTON_THUMB_R)
        self.button_select = Button(self.BUTTON_SELECT)
        self.button_start = Button(self.BUTTON_START)
        self.button_dpad_x_axis = Button(self.BUTTON_DPAD_X_AXIS)
        self.button_dpad_y_axis = Button(self.BUTTON_DPAD_Y_AXIS)

        self.is_present = False

        if(daemon_running):
            self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            print("Controller tread started")
    
    def update_controller_button_states(self):
        
        try:
            events = get_gamepad()
            self.is_present = True
        except:
            print("Failed to get gamepad")
            sys.exit(0)
        
        if(self.is_present == False):
            return
        
        for event in events:
            match event.code:
                case self.JOYSTICK_LEFT_Y: 
                    self.joystick_left_y.action(event.state)
                case self.JOYSTICK_LEFT_X: 
                    self.joystick_left_x.action(event.state)
                case self.JOYSTICK_RIGHT_Y: 
                    self.joystick_right_y.action(event.state)
                case self.JOYSTICK_RIGHT_X: 
                    self.joystick_right_x.action(event.state)
                case self.BUTTON_LEFT_TRIGGER: 
                    self.button_left_trigger.action(event.state)
                case self.BUTTON_RIGHT_TRIGGER: 
                    self.button_right_trigger.action(event.state)
                case self.BUTTON_DPAD_Y_AXIS: 
                    self.button_dpad_y_axis.action(-event.state)
                case self.BUTTON_DPAD_X_AXIS: 
                    self.button_dpad_x_axis.action(event.state)
                case self.BUTTON_LEFT_BUMPER: 
                    self.button_left_bumper.action(event.state)
                case self.BUTTON_RIGHT_BUMPER: 
                    self.button_right_bumper.action(event.state)
                case self.BUTTON_A: 
                    self.button_a.action(event.state)
                case self.BUTTON_Y: 
                    self.button_y.action(event.state)
                case self.BUTTON_X: 
                    self.button_x.action(event.state)
                case self.BUTTON_B:
                    self.button_b.action(event.state)
                case self.BUTTON_SELECT:
                    self.button_select.action(event.state)
                case self.BUTTON_START: 
                    self.button_start.action(event.state)
                case self.BUTTON_THUMB_L:
                    self.button_thumb_l.action(event.state)
                case self.BUTTON_THUMB_R:
                    self.button_thumb_r.action(event.state)

    def print_states(self):
        print(  self.joystick_left_x.value,self.joystick_left_y.value,
                self.joystick_right_x.value,self.joystick_right_y.value,
                self.button_left_trigger.value,self.button_right_trigger.value,
                self.button_left_bumper.value,self.button_right_bumper.value,
                self.button_a.value,self.button_b.value,
                self.button_x.value,self.button_y.value,
                self.button_thumb_l.value,self.button_thumb_r.value,
                self.button_select.value,self.button_start.value,
                self.button_dpad_x_axis.value,self.button_dpad_y_axis.value)

    def _monitor_controller(self):
        while True:
            self.update_controller_button_states()

class ButtonStateMachine(object):
    def __init__(self, num_states = 0, decision_func = None):
        self.funcs = None
        self.num_states = num_states
        self.states = []
        self.current_state = 0
        self.decision_func = decision_func

    def set_state_functions(self,*funcs):
        self.funcs = funcs
        self.num_states = len(self.funcs)
        for func in funcs:
            self.states.append(func)

    def cycle_states(self,decision_key = None):
        if(decision_key == None):
                if(self.decision_func == None):
                    print("Error: no decision function defined")
                    return None
                decision_key = self.decision_func()
        
        for i in range(0,self.num_states):
            if(self.current_state == i and decision_key == True):
                if(self.funcs != None):
                    self.states[i]()
                self.current_state = i+1
                if(self.current_state >= self.num_states):
                    self.current_state = 0
                return self.current_state
    
        return None

def map(v, in_min, in_max, out_min, out_max):
	# Check that the value is at least in_min
	if v < in_min:
		v = in_min
	# Check that the value is at most in_max
	if v > in_max:
		v = in_max
	return (v - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def joy_to_diff_drive(joy_x, joy_y):
    left = joy_x * math.sqrt(2.0)/2.0 + joy_y * math.sqrt(2.0)/2.0
    right = -joy_x * math.sqrt(2.0)/2.0 + joy_y * math.sqrt(2.0)/2.0
    return [left, right]

def joy_to_diff_drive2(joy_x, joy_y):
    if(joy_x == 0 and joy_y == 0):
        return (0,0) 
     #   convert to polar coordinates
    theta = math.atan2(joy_y, joy_x)
    r = math.sqrt(joy_x * joy_x + joy_y * joy_y)
    # this is the maximum r for a given angle    
    if abs(joy_x) > abs(joy_y):
        max_r = abs(r / joy_x)
    else:
        max_r = abs(r / joy_y)

    # this is the actual throttle  
    magnitude = r / max_r

    turn_damping = 1.5 # for example
    left = magnitude * (math.sin(theta) + math.cos(theta) / turn_damping)
    right = magnitude * (math.sin(theta) - math.cos(theta) / turn_damping)

    return (left, right)

def joy_to_diff_drive3(x, y, minJoystick, maxJoystick, minSpeed, maxSpeed):	
    # If x and y are 0, then there is not much to calculate...
	if x == 0 and y == 0:
		return (0, 0)
    

	# First Compute the angle in deg
	# First hypotenuse
	z = math.sqrt(x * x + y * y)

	# angle in radians
	rad = math.acos(math.fabs(x) / z)

	# and in degrees
	angle = rad * 180 / math.pi

	# Now angle indicates the measure of turn
	# Along a straight line, with an angle o, the turn co-efficient is same
	# this applies for angles between 0-90, with angle 0 the coeff is -1
	# with angle 45, the co-efficient is 0 and with angle 90, it is 1

	tcoeff = -1 + (angle / 90) * 2
	turn = tcoeff * math.fabs(math.fabs(y) - math.fabs(x))
	turn = round(turn * 100, 0) / 100

	# And max of y or x is the movement
	mov = max(math.fabs(y), math.fabs(x))

	# First and third quadrant
	if (x >= 0 and y >= 0) or (x < 0 and y < 0):
		rawLeft = mov
		rawRight = turn
	else:
		rawRight = mov
		rawLeft = turn

	# Reverse polarity
	if y < 0:
		rawLeft = 0 - rawLeft
		rawRight = 0 - rawRight

	# minJoystick, maxJoystick, minSpeed, maxSpeed
	# Map the values onto the defined rang
	rightOut = map(rawRight, minJoystick, maxJoystick, minSpeed, maxSpeed)
	leftOut = map(rawLeft, minJoystick, maxJoystick, minSpeed, maxSpeed)

	return (leftOut, rightOut)

create3_name = None

robot = Create3(Bluetooth(name=create3_name))
joy = Controller(deadzone=0.2,daemon_running=True)

change_speed_button = ButtonStateMachine(3, joy.button_a.is_pressed_ignore_repeat)

@event(robot.when_play)
async def play(robot):
    print('starting event trigger')
    # await play_one_up_tune()
    running = True
    robot_speed = 30

    while running:
        
        if (joy.button_select.is_pressed()):
            running = False

        if(joy.button_start.is_pressed()):
            await robot.dock() 
            running = False


        match change_speed_button.cycle_states():
            case 0: 
                robot_speed = 10
            case 1: 
                robot_speed = 20
            case 2: 
                robot_speed = 30

        [vl,vr] = joy_to_diff_drive3(joy.joystick_left_x.value,joy.joystick_left_y.value,-1,1,-robot_speed,robot_speed)

        if(joy.button_dpad_y_axis.value == 1):
            vl = robot_speed
            vr = robot_speed

        if(joy.button_dpad_y_axis.value == -1):
            vl = -robot_speed
            vr = -robot_speed

        if(joy.button_dpad_x_axis.value == 1):
            vl = robot_speed
            vr = -robot_speed

        if(joy.button_dpad_x_axis.value == -1):
            vl = -robot_speed
            vr = robot_speed

        await robot.set_wheel_speeds(vl, vr)
               
    sys.exit(0) 

robot.play()

