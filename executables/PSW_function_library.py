#!usr/local/Anaconda2023/bin/python3.11

import numpy as np 
import matplotlib.pyplot as plt
from math import *


################################################################
#
# Parker Solar Wind Model, Final Project
# File: <Function Library>
# Author: <Kaycee Conder> 
# Spring 2025 ASTR4610
#
################################################################

#Setting constants necessitated by functions

boltzmann_k     = 1.3807e-29	#km^2 kg s^-2 K^-1
proton_mass     = 1.67e-27		#kilograms
solar_radius    = 6.96e5		#kilometers
T_0             = 5.8e6			#Kelvin



def critical_radius(T):
	'''
	This function calculates Equation 1 in the 
	README file, aka the Critical Radius Equation. 

	This is the radius at which the solar wind 
	transitions from subsonic to supersonic speed.

	Parameters: 
		T: float, temperature of the Solar Corona in Kelvin. 
		This value is constrained between 0.5 million K and 
		4 million K. 

	Returns: 
		r_c: float, the critical radius in kilometers. 
	'''

	#Imposing our temperature constraints
	if T < 0.5e6:
		#Error message violating the lower temperature limit
		raise Exception('Oops! Your temperature value is too low to have real world implications!')


	elif T > 4e6:
		#Error message for violating the upper temperature limit
		raise Exception('Oops! Your temperature value is too high to have real world implications!')


	else: 
		r_c = (T_0/T) * solar_radius

	return r_c



#----------------------------------------------------------------------------------------------------------------------------------------------



def coronal_sound_speed(T):
	'''
	This function calculates Equation 2 in the 
	README file, aka The Coronal Sound Speed 
	Equation. 

	This is this is the speed at which sound waves 
	travel through the Sun's corona, and is 
	described via the 'mostprobable speed' via the 
	Maxwell Speed Distribution.

	Parameters: 
		T: float, temperature of the Sun's corona in Kelvin.
		This value is constranted between 0.5 million K and 
		4 million K. 

	Returns: 
		u_c^2: float, the coronal sound speed, specifically a
		velocity squared, in km^2 s^-2. 
	'''

	#Imposing our temperature constraints
	if T < 0.5e6:
		#Error message violating the lower temperature limit
		raise Exception('Oops! Your temperature value is too low to have real world implications!')


	elif T > 4e6:
		#Error message for violating the upper temperature limit
		raise Exception('Oops! Your temperature value is too high to have real world implications!')


	else:
		u_c_squared = (2*boltzmann_k*T)/proton_mass

	return u_c_squared



#----------------------------------------------------------------------------------------------------------------------------------------------



def df_dr(r,f,u_c_squared, r_c):
	'''
	This function calculates Equation 3 in the 
	README file, aka the Differential Equation For
	The Parker Solar Wind Speed. Here, f represents
	the solar wind speed (u^2) to simplify the 
	calculations. 

	This simply yields the slope of our solar 
	wind speed graph, the likes of which is a 
	function of distance from the Sun r. Said 
	result will be used as our Runge Kutta 4
	function to be integrated. 

	Parameters: 
		r: float, the radius from the Sun in 
		meters. This is the location where you 
		want to know the solar wind speed u. 

		f: float, a given solar wind speed value
		in km^2 s^-2. 

		u_c_squared: float, the coronal sound speed 
		in km^2 s^-2 .

		r_c: float, critical radius in km. 


	Returns: 
		df/dr: float, the derivative of solar wind 
		speed u^2 with respect to distance r. 
	'''


	numerator = ((4 * u_c_squared)/r) * (1 - (r_c/r))

	#Won't divide by zero if speed are equal 
	if u_c_squared == f: 
		denominator = 1e-8
	else: 
		denominator = (1 - (u_c_squared/f))

	return numerator/denominator 



#----------------------------------------------------------------------------------------------------------------------------------------------



def closest_points(r_values, my_rval):
	'''
	This function calculates the two r-points, 
	from out set of RK4 r values, that are 
	'straddle' our input r value. 

	This is done so by utilzing our equal
	r-step divides to find the point to
	the left and right of our input 
	distance. See the README for a visual
	explanation of the logic.

	Parameters: 
		r_values: numpy array, set of r
		valules, in km, generated from our 
		Runge Kutta 4 integration. 

		my_rval: float, input distance
		r at which we want to find the
		solar wind speed. 


	Returns: 
		left_point, right point: floats, the 
		values of the points straddling
		my_rval. 
	'''


	#Initializing values & empty array
	difference = []
	right_point = 0
	left_point = 0

	'''Iterate through r-values to find one closest to given input 
	r-value.'''
	for i in range(len(r_values)):
		difference.append(abs(r_values[i]-my_rval)) #distance between our input r_value and RK4 list of r values

	closest_point_value = r_values[int(np.argwhere(difference == min(difference)))] #value of closest r point
	closest_point_index = int(np.argwhere(r_values == closest_point_value)) #index of closest r point


	'''Using our equal r-value spacing and indexing to find the
	surrounding r-value points.'''
	closest_right_distance = abs(r_values[closest_point_index+1]-my_rval) #distance b/w our r_val and the point right of the closest point
	closest_left_distance = abs(r_values[closest_point_index-1]-my_rval)  #distance b/w our r_val and the point left of the closest point


	#Accounting for our limiting cases...
	if my_rval < r_values[0]:
		raise Exception('Oops! Your input distance value is too small, and outside our model range!')

	elif my_rval > r_values[-1]:

		raise Exception('Oops! Your input distance value is too large, and outside our model range!')

	elif closest_point_index == 0:
		#When our closest RK4 r value point doesn't have a point to its left
		left_point = r_values[0]
		right_point = r_values[1]

	elif closest_point_index == len(r_values) -1: 
		#When our closest RK4 r value point doesn't have a point to its right
		left_point = r_values[-2]
		right_point = r_values[-1]

	#Accounting for general cases...
	elif closest_left_distance < closest_right_distance:
		#Point right of closest RK4 r value is not straddling
		right_point = float(closest_point_value)
		left_point = float(r_values[closest_point_index-1])


	elif closest_left_distance > closest_right_distance:
		#Point left of closest RK4 r value is not straddling
		left_point = float(closest_point_value)
		right_point = float(r_values[closest_point_index+1])

	return left_point, right_point



#----------------------------------------------------------------------------------------------------------------------------------------------



def y_from_line(x_val, slope, intercept): 
	'''
	This function uses the basic y=mx+b
	format to find the y value given a
	known slope, x value,and y-intercept.

	In the context of our problem, the 
	x-value will be our input r-value 
	in km, the sloep and intercept are
	determined via stats.linregress, and 
	the y value is our solar wind speed. 


	Parameters:
		x_val: float, our input r-value 
		in kilometers. 

		slope: float, slope of line b/w
		the points straddling our input
		r-value via stats.linregress.

		intercept: float, y-intercept
		of line b/w the points straddling 
		our input r-value via stats.linregress.

	Returns: 
		y_value: float, the solar wind speed
		in km s^-1 at our given r-input value. 
	''' 

	y_value = (slope * x_val) + intercept

	return y_value



#----------------------------------------------------------------------------------------------------------------------------------------------



def linear_properties(x1, x2, y1, y2):
	'''
	This function acts similar to stats.linregress, 
	using the properties of a straight line to calculate 
	the slope and intercept of a line via two points 
	along said line.

	Parameters: 
		x1: float, leftmost x value. Leftmost r-value 
		in our case [km]. 
		
		x2: float, rightmost x value. Rightmost r-value
		in our case [km].

		y1: float, corresponding y value for x1. 
		Solar wind speed in our case [km s^-1]

		y2: float, corresponding y value for x2. 
		Solar wind speed in our case [km s^-1]

	Returns: 
		slope, intercept: floats, slope and intercept
		of line defined by our two input points. 
	'''

	slope = (y2-y1)/(x2-x1)
	intercept = y1 - (slope*x1)

	return slope, intercept
	


#----------------------------------------------------------------------------------------------------------------------------------------------



def dphi_dr(solar_omega, u_value):
	'''
	This function defines our Equation 
	in the README file, aka the DEQ for the 
	Sun's Magnetic Field position angle. 

	Parameters: 
		solar_omega: float, solar rotation 
		speed [rad/s]

		u_value: float, solar wind velocity
		speed [km s^-1]

	Returns: 
		dphi_dr: float, DEQ value. 
	'''

	return -solar_omega/u_value



#----------------------------------------------------------------------------------------------------------------------------------------------



def euler_method_parker(solar_omega, r_values, u_values):
	'''
	This function calculates the values needed to plot the 
	Parker Spiral, specifically angle phi and radius r
	of the Sun's magnetic field. This is done via Euler's 
	Method, implemented w/respect to Equation 4 in the
	README file. 

	Parameters: 
		solar_omega: float, angular velocity of the sun [rad/s]

		r_values: numpy array, r-values of distances from the 
		Sun via the RK4 integration [km].

		u_values: numpy array, solar wind velocity values
		from RK4 integration [km s^-1].

	Returns: 
		phi_values: numpy array, phi values for our Parker Spiral.
	'''

	#Initializing array
	phi0 = 0
	phi = [phi0]

	#Looping through RK4 generated r-values...
	for i in range(len(r_values)-1):
		dR = 1e6	#our h value from the RK4 integration 
		dphi = -solar_omega * dR / u_values[i] #from dPhi_dR equation
		phi.append(phi[-1] + dphi) #angle at next dPhi step

	
	return np.array(phi)



#----------------------------------------------------------------------------------------------------------------------------------------------


print('ParkerSolarWind Function Library Updated.')





