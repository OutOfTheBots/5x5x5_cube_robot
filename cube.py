from cube_5x5x5_stepper import Stepper_Motor
from BOTS import *
from machine import I2C, UART
import time

cube_pos = ["U", "L", "F", "R", "B", "D"]

top_gripper_state = 0
bottom_gripper_state = 0
bottom_gripper_state = 0

stepper = Stepper_Motor(32, 33, 12, 13, 25, 14)

linear_positions = (-360, -135, 135, 360)    

max_speed = 750 
max_cube_rotate = 450  
max_free = 450 
start_speed = 6000
linear_start_speed = 3000
max_linear = 400

over_shoot = 8

wait_gap = 0.3

rot_face = False


uart = UART(1, tx=15, rx=2, baudrate=115200) 


I2C_bus = I2C(0, sda=27, scl=26)

cube_servo = Servo (I2C_bus) 

b_servo = (0.4, 0.7, 0.97) 
l_servo = (0.4, 0.57, 0.76) 
r_servo = (0.16, 0.65, 0.77) 
cube_servo.set_servo (0.91, 5)
cube_servo.set_servo (l_servo[0], 6)
cube_servo.set_servo (r_servo[0], 7)

#stepper.move_position(2, 200,5000, 2000) 


def rot_cube_t_pos(rotation):  
  global cube_pos
  temp = cube_pos[0]
  if rotation == 1:
	cube_pos[0] = cube_pos[2]
	cube_pos[2] = cube_pos[5]
	cube_pos[5] = cube_pos[4]
	cube_pos[4] = temp
  elif rotation == -1:
	cube_pos[0] = cube_pos[4] 
	cube_pos[4] = cube_pos[5]
	cube_pos[5] = cube_pos[2]
	cube_pos[2] = temp
  else:
	cube_pos[0] =  cube_pos[5]
	cube_pos[5] = temp
	temp = cube_pos[2]
	cube_pos[2] = cube_pos[4]
	cube_pos[4] = temp

	
def rot_cube_b_pos(rotation):
  global cube_pos
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
	

while uart.any() == 0: time.sleep(0.1)
time.sleep(0.5)

num_data = uart.any()
data = uart.read(num_data).decode("ascii")

print (data)

total_moves = 0

for loop in range(len(data)): 
	if data[loop] == " ": total_moves += 1

print("total_moves = ", total_moves)

solution = [["E", 1, 1, 1]]

for loop in range(total_moves): solution.append(["E", 1, 1, 1])

move_number = 0
string_pos = 0

while string_pos < num_data:
	solution[move_number][0] = data[string_pos]
	string_pos += 1
	if data[string_pos] == "w":
		solution[move_number][1] = 1
		string_pos += 1
	else: solution[move_number][1] = 0
	if data[string_pos] == "2":
		solution[move_number][2] = 2
		string_pos +=1
	else: solution[move_number][2] = 1
	if data[string_pos] == "'":
		solution[move_number][3] = -1
		string_pos += 1
	else: solution[move_number][3] = 1
	string_pos +=1 
	move_number +=1
	
	
cube_servo.set_servo (b_servo[2], 5)

#setup first move if on face 3 or 1
if solution[0][0] == cube_pos[3] or solution[0][0] == cube_pos[1]:
	if solution[0][0] == cube_pos[3]: 
		stepper.move_position(0, linear_positions[3 - solution[0][1]] , linear_start_speed, max_linear)
		rot_face = False
	else: 
		stepper.move_position(0, linear_positions[solution[0][1]] , linear_start_speed, max_linear)
		rot_face = True
	#close both top
	cube_servo.set_servo (l_servo[2], 6)
	cube_servo.set_servo (r_servo[2], 7)
	time.sleep(0.3)
	#open b gripper
	cube_servo.set_servo (b_servo[0], 5)
	time.sleep(0.1)


for moves in range(move_number):
	print()
	print(solution[moves])
	
	if solution[moves][0] == cube_pos[0] or solution[moves][0] == cube_pos[5]:
		print("posiotion 0 or 5")
		#move to linear postion for rotation
		stepper.move_position(0, linear_positions[1], linear_start_speed, max_linear)  
		#open left griper and close r gripper
		cube_servo.set_servo (l_servo[0], 6)
		cube_servo.set_servo (r_servo[2], 7)
		time.sleep(wait_gap)
		#open bottom gripper
		cube_servo.set_servo (b_servo[0], 5)
		time.sleep(0.1)		
	
		if top_gripper_state < 1: 
			#rotate top gripper/cube
			stepper.move_position(2, stepper.read_position()[2] + 200, start_speed, max_cube_rotate) 
			rot_cube_t_pos(1)
			top_gripper_state += 1			
			#close bottom gripper
			cube_servo.set_servo (b_servo[2], 5)
			time.sleep(0.3)
			#part open right gripper
			cube_servo.set_servo (r_servo[1], 7)
			time.sleep(0.1)
			wait_gap = 0.1
		else: 
			#rotate top gripper/cube
			stepper.move_position(2, stepper.read_position()[2] - 200, start_speed, max_cube_rotate)
			rot_cube_t_pos(-1)
			top_gripper_state -= 1			
			#close bottom gripper
			cube_servo.set_servo (b_servo[2], 5)
			time.sleep(0.3)
			#part open right gripper
			cube_servo.set_servo (r_servo[1], 7)
			time.sleep(0.1)
			wait_gap = 0.1
		stepper.move_position(0, 200, linear_start_speed, max_linear)
		#open r gripper all the way now 
		cube_servo.set_servo (r_servo[0], 7)
		
			
	if solution[moves][0] == cube_pos[2] or solution[moves][0] == cube_pos[4]: 
		print ("position 2 or 4")
		if solution[moves][0] == cube_pos[2]: spin_dir = -1
		else: spin_dir = 1
		#move linear to spin
		stepper.move_position(0, 200, linear_start_speed, max_linear)
		#open both top
		cube_servo.set_servo (l_servo[0], 6)
		cube_servo.set_servo (r_servo[0], 7)
		time.sleep(0.1)
		#rotate bottom and side if needed
		if top_gripper_state == -1:	stepper.move_2_motor_90(spin_dir, 1, start_speed, max_free)
		elif top_gripper_state == 1: stepper.move_2_motor_90(spin_dir, -1, start_speed, max_free)
		else: stepper.move_position(1, 200 * spin_dir, start_speed, max_free)		
		#return top_gripper_state to zero
		stepper.move_position(2, 0, start_speed, max_free)								
		top_gripper_state = 0
		bottom_gripper_state = spin_dir
		rot_cube_b_pos(spin_dir)		
		
		#move to next linear possition for next face		
		if solution[moves][0] == cube_pos[3]: 
			stepper.move_position(0, linear_positions[3 - solution[moves][1]] , linear_start_speed, max_linear)
			rot_face = False
		else: 
			stepper.move_position(0, linear_positions[solution[moves][1]] , linear_start_speed, max_linear)
			rot_face = True
			
		
		#close both top
		cube_servo.set_servo (l_servo[2], 6)
		cube_servo.set_servo (r_servo[2], 7)
		time.sleep(0.3)
		
		'''
		#open b half way
		cube_servo.set_servo (b_servo[1], 5)
		time.sleep(0.1)
		#rotate bottom back to zero
		stepper.move_position(1, 0, start_speed, max_free)
		#open b gripper
		cube_servo.set_servo (b_servo[0], 5)
		'''
		#open b 
		cube_servo.set_servo (b_servo[0], 5)
		time.sleep(0.2)
		

		
			
	if solution[moves][0] == cube_pos[3] or solution[moves][0] == cube_pos[1]:
		
		if bottom_gripper_state == 0:		
			#test for double turn
			if solution[moves][2] == 2:
				if top_gripper_state == 0: turn_dir = (solution[moves + 1][3] * -1)
				elif top_gripper_state < 0: turn_dir = 1 
				else: turn_dir = -1
				stepper.move_position(2, stepper.read_position()[2] + (400*turn_dir), start_speed, max_speed, overshoot=over_shoot)
				top_gripper_state += (2*turn_dir)
				if rot_face: rot_cube_t_pos(2)
			else: 
				stepper.move_position(2, stepper.read_position()[2] + (200*solution[moves][3]), start_speed, max_speed, overshoot=over_shoot)
				top_gripper_state += solution[moves][3]
				if rot_face: rot_cube_t_pos(solution[moves][3])
			#close b gripper
			cube_servo.set_servo (b_servo[2], 5)
			time.sleep(0.3)
			#part open top
			cube_servo.set_servo (l_servo[1], 6)
			cube_servo.set_servo (r_servo[1], 7)
			time.sleep(0.1)
			wait_gap = 0.1
		else:
			#test for double turn
			if solution[moves][2] == 2:
				if top_gripper_state == 0: turn_dir = (solution[moves + 1][3] * -1)
				elif top_gripper_state < 0: turn_dir = 1 
				else: turn_dir = -1				
				stepper.move_2_motor_90(bottom_gripper_state*-1, turn_dir, start_speed, max_free)				
				stepper.move_position(2, stepper.read_position()[2] + (200*turn_dir), start_speed, max_speed, overshoot=over_shoot)
				top_gripper_state += (2*turn_dir)
				if rot_face: rot_cube_t_pos(2)
			else: 
				stepper.move_2_motor_90(bottom_gripper_state*-1, (200*solution[moves][3]), start_speed, max_free, overshoot=over_shoot)   
				top_gripper_state += solution[moves][3]
				if rot_face: rot_cube_t_pos(solution[moves][3])
			bottom_gripper_state = 0
			#close b gripper
			cube_servo.set_servo (b_servo[2], 5)
			time.sleep(0.3)
			#part open top
			cube_servo.set_servo (l_servo[1], 6)
			cube_servo.set_servo (r_servo[1], 7)
			time.sleep(0.1)
			wait_gap = 0.1			

	if solution[moves + 1][0] == cube_pos[3] or solution[moves + 1][0] == cube_pos[1]:
		if solution[moves + 1][0] == cube_pos[3]: 
			stepper.move_position(0, linear_positions[3 - solution[moves + 1][1]] , linear_start_speed, max_linear)
			rot_face = False
		else: 
			stepper.move_position(0, linear_positions[solution[moves + 1][1]] , linear_start_speed, max_linear)
			rot_face = True
		#close both top
		cube_servo.set_servo (l_servo[2], 6)
		cube_servo.set_servo (r_servo[2], 7)
		time.sleep(0.3)
		#open b gripper
		cube_servo.set_servo (b_servo[0], 5)
		time.sleep(0.1)

stepper.move_position(0, 200,linear_start_speed, max_linear)
#open both top
cube_servo.set_servo (l_servo[0], 6)
cube_servo.set_servo (r_servo[0], 7)
time.sleep(0.1)
#zero top gripper
stepper.move_position(2, 0,start_speed, max_speed)
#zero linear		
stepper.move_position(0, 0,linear_start_speed, max_linear)

I2C_bus.deinit()
del stepper



