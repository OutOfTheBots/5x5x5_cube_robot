from machine import Pin
import time

class Stepper_Motor: 
	
	def __init__(self, linear_dir_pin, linear_step_pin, bottom_dir_pin, bottom_step_pin, top_dir_pin, top_step_pin):
		self.linear_dir = Pin(linear_dir_pin, Pin.OUT)
		self.linear_step = Pin(linear_step_pin, Pin.OUT) 
		self.linear_dir.value(0)
		self.linear_step.value(0)
		self.linear_pos_count = 0
		
		self.bottom_dir = Pin(bottom_dir_pin, Pin.OUT)
		self.bottom_step = Pin(bottom_step_pin, Pin.OUT) 
		self.bottom_dir.value(0)
		self.bottom_step.value(0)
		self.bottom_pos_count = 0
		
		self.top_dir = Pin(top_dir_pin, Pin.OUT)
		self.top_step = Pin(top_step_pin, Pin.OUT) 
		self.top_dir.value(0)
		self.top_step.value(0)
		self.top_pos_count = 0

	
	def move_position(self, motor, position, speed, max_speed, overshoot=0):  
		rampup_count = 0
		n = 0
		
		if motor == 0:
			step = self.linear_step.value
			direction = self.linear_dir.value
			total_step = abs(position - self.linear_pos_count) + overshoot 
			if position > self.linear_pos_count: 
				direction(1)
				change = 1
			else: 
				direction(0)
				change = -1
			self.linear_pos_count = position		
		elif motor == 1:
			step = self.bottom_step.value
			direction = self.bottom_dir.value
			total_step = abs(position - self.bottom_pos_count) + overshoot 
			if position > self.bottom_pos_count: 
				direction(1)
				change = 1
			else: 
				direction(0)
				change = -1
			self.bottom_pos_count = position			
		elif motor == 2:
			step = self.top_step.value
			direction = self.top_dir.value
			total_step = abs(position - self.top_pos_count) + overshoot			
			if position > self.top_pos_count: 
				direction(1)
				change = 1
			else: 
				direction(0)
				change = -1
			self.top_pos_count = position
				
		delay = time.sleep_us
		half_count = total_step // 2

		
		for loop in range(total_step):			
			if rampup_count == 0:
			  n += 1
			  speed = speed - ( (2 * speed) / (4 * n +1) )
			  if speed < max_speed:				
				speed = max_speed				
				rampup_count = n			  
			  if n > half_count : rampup_count = next
			elif loop + rampup_count > total_step:
			  n -= 1
			  speed = (speed * (4 * n + 1) / (4 * n - 1))	 		  
			step(1)
			step(0)
			delay(int(speed))		
		
		if change == -1: direction(1) 
		else: direction(0)
		time.sleep(0.05)
		for loop in range(overshoot):
			step(1)
			step(0)
			delay(int(speed))

	def move_2_motor_90(self, bottom_dir, top_dir, speed, max_speed, overshoot=0):  
		if bottom_dir > 0: 
			self.bottom_dir.value(1)
			bot_val = 1
			self.bottom_pos_count += 200
		else: 
			self.bottom_dir.value(0)
			bot_val = 0
			self.bottom_pos_count -= 200
		if top_dir > 0: 
			self.top_dir.value(1)
			top_val = 1
			self.top_pos_count += 200
		else: 
			self.top_dir.value(0)
			top_val = 0
			self.top_pos_count -= 200

		rampup_count = 0
		n = 0
		delay = time.sleep_us
		step_bottom = self.bottom_step.value
		step_top = self.top_step.value
		total_step  = 200 + overshoot

		
		for loop in range(total_step):			
			if rampup_count == 0:
			  n += 1
			  speed = speed - ( (2 * speed) / (4 * n +1) )
			  if speed < max_speed:				
				speed = max_speed				
				rampup_count = n			  
			  if n > 100 : rampup_count = next
			elif loop + rampup_count > total_step:
			  n -= 1
			  speed = (speed * (4 * n + 1) / (4 * n - 1))	 		  
			step_bottom(1)
			step_bottom(0)
			step_top(1)
			step_top(0)
			delay(int(speed))
			print(loop) 

		time.sleep(0.05)
		if bot_val == 0: self.bottom_dir.value(1)
		else: self.bottom_dir.value(0)		
		if top_val == 0: self.top_dir.value(1)
		else: self.top_dir.value(0) 
		for loop in range(overshoot): 
			step_bottom(1)
			step_bottom(0)
			step_top(1)
			step_top(0)
			delay(int(speed))

			
	def zero_position(self, motor):
		if motor == 0 : self.linear_pos_count = 0
		elif motor == 1: self.bottom_pos_count = 0
		elif motor == 2: self.top_pos_count = 0

	
	def read_position(self):
		return (self.linear_pos_count, self.bottom_pos_count, self.top_pos_count)