from machine import Pin
import time

class Stepper_Motor:
	
	def __init__(self, dir_pin, step_pin):
		self.dir = Pin(dir_pin, Pin.OUT)
		self.step = Pin(step_pin, Pin.OUT)
		self.dir.value(0)
		self.step.value(0)
		self.pos_count = 0
	
	def move_position(self, position, speed, max_speed, overshoot=0):  
		rampup_count = 0
		n = 0
		total_step = abs(position - self.pos_count) + overshoot 
		half_count = total_step // 2
		
		step = self.step.value
		delay = time.sleep_us
		
		if position > self.pos_count: 
		  self.dir.value(1)
		  change = 1
		else: 
		  self.dir.value(0)
		  change = -1		
		
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
			self.pos_count += change
			delay(int(speed))		
		
		if change == -1: self.dir.value(1) 
		else: self.dir.value(0)
		change *= -1
		time.sleep(0.05)
		for loop in range(overshoot):
			step(1)
			step(0)
			self.pos_count += change
			delay(int(speed))			
		
	def zero_position(self):
		self.pos_count = 0
	
	def read_position(self):
		return self.pos_count 