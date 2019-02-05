from Stepper import Stepper_Motor 
from BOTS import *
from machine import I2C, UART
import time

cube_pos = ["U", "L", "F", "R", "B", "D"]

bottom_stepper = Stepper_Motor(12, 13)
top_stepper = Stepper_Motor(25, 14)
linear_stepper = Stepper_Motor(32, 33)


linear_positions = (-360, -135, 135, 360)   

max_speed = 1500
max_free = 800 
start_speed = 5000
linear_start_speed = 2000
max_linear = 400

over_shoot = 20


uart = UART(1, tx=15, rx=2, baudrate=115200)


I2C_bus = I2C(0, sda=27, scl=26)

cube_servo = Servo (I2C_bus) 

b_close = 0.96 #0.96
top_r_close = 0.8
top_l_close = 0.72

#cube_servo.set_servo (b_close, 5)
cube_servo.set_servo (0.9, 5)
cube_servo.set_servo (0.3, 6)
cube_servo.set_servo (0.3, 7)



def top_l (pos):
  if pos == 0: cube_servo.set_servo (0.3, 6)
  else : cube_servo.set_servo (top_l_close, 6) 
  #time.sleep(0.4)
  
def top_r (pos):
  if pos == 0: 
	cube_servo.set_servo (0.3, 7)
	time.sleep(0.1)
  elif pos == 1 : 
	cube_servo.set_servo (top_r_close, 7)
	time.sleep(0.3)
  else : 
	cube_servo.set_servo (0.69, 7)
	time.sleep(0.05)

def top_both(pos):
  if pos == 1:
	cube_servo.set_servo (top_l_close, 6)
	cube_servo.set_servo (top_r_close, 7)
	time.sleep(0.3)
  elif pos == 0:
	cube_servo.set_servo (0.3, 6)
	cube_servo.set_servo (0.3, 7)
	time.sleep(0.1)
  elif pos == 2:
	cube_servo.set_servo (top_l_close, 6)
	cube_servo.set_servo (top_r_close, 7)
	time.sleep(0.1)	
  else:
	cube_servo.set_servo (0.6, 6)
	cube_servo.set_servo (0.65, 7)
	time.sleep(0.05)
	
  

def bottom(pos):
  if pos==1: 
	cube_servo.set_servo (b_close, 5)
	time.sleep(0.3)
  else: 
	cube_servo.set_servo (0.5, 5)
	time.sleep(0.1)


  
def rotate_cube_t(rotation):
  global cube_pos
  linear_stepper.move_position(linear_positions[1], linear_start_speed, max_linear)
  top_r(1)
  bottom(0)
  top_stepper.move_position(rotation*200, start_speed, max_speed)
  bottom(1)
  top_r(2)
  linear_stepper.move_position(linear_positions[3], linear_start_speed, max_linear)
  top_r(0)
  top_stepper.move_position(0, start_speed, max_free)
  temp = cube_pos[0]
  if rotation == 1:
	cube_pos[0] = cube_pos[2]
	cube_pos[2] = cube_pos[5]
	cube_pos[5] = cube_pos[4]
	cube_pos[4] = temp
  if rotation == -1:
	cube_pos[0] = cube_pos[4]
	cube_pos[4] = cube_pos[5]
	cube_pos[5] = cube_pos[2]
	cube_pos[2] = temp
	
  
  
def rotate_cube_b (rotation):
  global cube_pos
  global short
  linear_stepper.move_position(0,linear_start_speed, max_linear)
  bottom_stepper.move_position (rotation*200, start_speed, max_free)
  top_both(1)
  bottom(0)
  bottom_stepper.move_position (0,start_speed, max_free)
  bottom(1)
  top_both(3)
  short = True
  temp = cube_pos[2]
  if rotation == 1:
	cube_pos[2] = cube_pos[3]
	cube_pos[3] = cube_pos[4]
	cube_pos[4] = cube_pos[1]
	cube_pos[1] = temp
  elif rotation == -1:
	cube_pos[2] = cube_pos[1]
	cube_pos[1] = cube_pos[4]
	cube_pos[4] = cube_pos[3]
	cube_pos[3] = temp
  elif rotation == 2:
	cube_pos[2] = cube_pos[4] 
	cube_pos[4] = temp
	temp = cube_pos[1]
	cube_pos[1] = cube_pos[3]
	cube_pos[3] = temp
  

    

while uart.any() == 0: time.sleep(0.1)
time.sleep(0.5)

num_data = uart.any()
data = uart.read(num_data).decode("ascii")

print (data)

string_pos = 0

cube_servo.set_servo (b_close, 5)

short = False


while string_pos < num_data:
	face = data[string_pos]
	string_pos += 1
	if data[string_pos] == "w":
		w = 1
		string_pos += 1
	else: w = 0
	if data[string_pos] == "2":
		turns = 2
		string_pos +=1
	else: turns = 1
	if data[string_pos] == "'":
		invert = -1
		string_pos += 1
	else: invert = 1
	string_pos +=1
	
	
	print ( face, w, turns, invert)
	
	if face == cube_pos[0] or face == cube_pos[5]: rotate_cube_t(1)
	if face == cube_pos[2]: rotate_cube_b(-1)
	if face == cube_pos[4]: rotate_cube_b(1)
	#if face == cube_pos[1]: rotate_cube_b(2)
	
	if face == cube_pos[3]:
		linear_stepper.move_position(linear_positions[3-w], linear_start_speed, max_linear)
		if short: 
			top_both(2)
			short = False
		else: top_both(1)
		bottom(0)
		top_stepper.move_position(turns*200*invert, start_speed, max_speed, overshoot=over_shoot)		
		bottom(1)
		top_l(0)
		top_r(2)
		linear_stepper.move_position(linear_positions[3], linear_start_speed, max_linear)
		top_r(0)
		top_stepper.move_position(0, start_speed, max_free)
	elif face == cube_pos[1]:
		linear_stepper.move_position(linear_positions[w], linear_start_speed, max_linear)
		if short: 
			top_both(2)
			short = False
		else: top_both(1)
		bottom(0)
		top_stepper.move_position(turns*200*invert, start_speed, max_speed, overshoot=over_shoot)
		temp = cube_pos[0]
		if turns == 1 and invert == 1:
			cube_pos[0] = cube_pos[2]
			cube_pos[2] = cube_pos[5]
			cube_pos[5] = cube_pos[4]
			cube_pos[4] = temp
		if turns == 1 and invert == -1:
			cube_pos[0] = cube_pos[4]
			cube_pos[4] = cube_pos[5]
			cube_pos[5] = cube_pos[2]
			cube_pos[2] = temp
		if turns == 2:
			cube_pos[0] = cube_pos[5]
			cube_pos[5] = temp
			temp = cube_pos[2]
			cube_pos[2] = cube_pos[4]
			cube_pos[4] = temp
		
		bottom(1)
		top_l(0)
		top_r(2)
		linear_stepper.move_position(linear_positions[3], linear_start_speed, max_linear)
		top_r(0)
		top_stepper.move_position(0, start_speed, max_free)

		
linear_stepper.move_position(0,linear_start_speed, 800)
I2C_bus.deinit()
del bottom_stepper
del top_stepper
del linear_stepper


