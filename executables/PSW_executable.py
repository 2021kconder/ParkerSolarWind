#!usr/local/Anaconda2023/bin/python3.11



import PSW_function_library as PSW
import numpy as np
from math import *
import matplotlib.pyplot as plt



################################################################
#
# Parker Solar Wind Model, Final Project
# File: <Main Executable>
# Author: <Kaycee Conder> 
# Spring 2025 ASTR4610
#
################################################################

# ----------------
# Input Parameters 
# ----------------

'''The following section is where you will modify your input values
for the program. Please note the restrictions on each of the input 
values, indicated by the 'Range' note next to each input. Your value
MUST exist within this range or the program will return an exception.

The coronal temperature range spans the plausible/phyiscally significant
temperatures of the corona. 

The radial distance range spans the location of the Critical Radius, 
defined as Equation 1 in the README file, to the orbit of Jupiter. 
'''

#The temperature of the Corona of the Sun.
corona_temperature = 4e6 #Kelvin, Range: 0.5e6 K to 4e6 K

#The distance at which you want to find the speed of the solar wind.
radial_distance = 200e6 #Kilometers, Range: Critical Radius to 766.44e6 km

#Location where you want to save all output files.
output_filepath_RK4 ='/d/cha1/kconder/PHYS4840_labs/final_project/RK4_solarwind_data.txt'	#RK4 solar wind data location
output_filepath_PSW_graph = '/d/cha1/kconder/PHYS4840_labs/final_project/parker_solar_wind_plot.png'	#Parker Solar Wind results plot
output_filepath_p_spiral = '/d/cha1/kconder/PHYS4840_labs/final_project/parker_spiral_plot.png'	#parker Spiral results plot

# ----------------------
# Determining Key Values
# ----------------------

'''
The following utilizes previously established
definitions from the PSW_function_library to 
find the following quantities. These values 
are necessary to integrate the Parker Solar 
Wind Equation & find the dependence of solar 
wind speed [km s^-1] on distance from the Sun 
[km]: 

Critical Radius: Radius at which solar wind
transitions from subsonic to supersonic speed.
Units of kilometers. 

Coronal Sound Speed: Speed at which sound
waves travel through the Sun's Corona. 
Specifically gives this speed squared. Units
of km^2 s^-2.
'''

r_c = PSW.critical_radius(corona_temperature) #critical radius
u_c_squared = PSW.coronal_sound_speed(corona_temperature) #coronal sound speed

# ------------------------------
# Integrating Via Runge Kutta 4
# ------------------------------

'''
The following utilizes the Runge Kutta 4 
method of solving ODEs to find the 
dependence of solar winid on distance from 
the Sun. 

An output file will be generated via your
given filepath in the 'Input Parameters' 
Section 
'''

#Setting initial conditions

r_0 = r_c * 1.01			#initial radial distance, critical radius
f_0 = u_c_squared * 1.01	#initial velocity squared, coronal sound speed (where f=u^2)
h = 1e6 					#step size
N = 5000 					#number of steps 

def RK4_solar_wind(r0, f0, h, N):
	'''
	This function utilzies the RK4 method 
	of integration to find the dependence 
	of solar wind speed on distance from 
	the Sun. 

	Here, our function to integrate is
	defined in the PSW_function_library. 

	Parameters: 
		r0: float, initial radial distance [km]

		f0: float, initial solar wind speed 
		squared [km^2 s^-2]

		h: float, step size

		N = int, number of steps

	Returns: 
		r_vals, u_vals: numpy arrays, radial distance 
		values and solar wind speed values squared 
		[km] and [km^2 s^-2].
	'''

	r_vals = [r0]
	f_vals = [f0]
	r = r0
	f = f0 

	for i in range(N): 
		k1 = h * PSW.df_dr(r,f, u_c_squared, r_c)
		k2 = h * PSW.df_dr(r+0.5*h, f+0.5*k1, u_c_squared, r_c)
		k3 = h * PSW.df_dr(r+0.5*h, f+0.5*k2, u_c_squared, r_c)
		k4 = h * PSW.df_dr(r+ h, f+ k3, u_c_squared, r_c)

		f += (k1 + 2*k2 + 2*k3 + k4) /6
		r += h 


		r_vals.append(r)
		f_vals.append(f)


	return np.array(r_vals), np.array(f_vals)

#Performing the integration via the above definition
r_vals_initial, f_vals_initial = RK4_solar_wind(r_0, f_0, h, N)

#Constraining our r values to inside the orbit of Juptier 
r_vals = []
u_vals = []

for i in range(len(r_vals_initial)):
	if r_vals_initial[i] < 766.44e6:
		r_vals.append(r_vals_initial[i])
		u_vals.append(sqrt(f_vals_initial[i])) #finding the solar wind speed from solar wind speed squared (RK4 output)


#Saving data to data file 
RK4_sw_data = np.column_stack((r_vals, u_vals)) #generating columns 
np.savetxt(output_filepath_RK4, RK4_sw_data, header='R Values [m] U Values [m s^-1]', delimiter=',', fmt='%d')

# -------------
# Interpolation
# -------------

'''
The following uses methods of linear interpolation
to find the solar wind speed at our input radial 
distance. 
'''

#First finding the closest RK4 r-values to our input r-value. 
#Specifically, the points directly to the left and to the right. 
left_point, right_point = PSW.closest_points(r_vals, radial_distance)


def interpolating(left_point, right_point, r_values, u_values, my_rval):
	'''
	This function utilizes properties of a line via two points and
	linear interpolation to find the solar wind speed for our input 
	r-value. 

	Parameters: 
		left_point: float, left point straddling input r-value [km]

		right_point: float, right piont straddling input r-value [km]

		r_values: numpy array, set of r-values from RK4 integration [km]

		u_values: numpy array, set of u-values from RK4 integration [km s^-1]

		my_rval: float, input r-value [km]

	Returns: 
		my_uval: float, solar wind speed at input radius
	'''

	#Index of our closes points 
	left_index = r_values.index(left_point)
	right_index = r_values.index(right_point)

	#Setting arrays with closest r and u values 
	closest_r = np.array([left_point, right_point], dtype=float)
	closest_u = np.array([float(u_values[left_index]), float(u_values[right_index])])

	#Finding slope and interept of line b/w points straddling input r-value 
	slope, intercept = PSW.linear_properties(left_point, right_point, closest_u[0], closest_u[1])

	#Finding u-value corresponding to input r-value via y=mx+b
	my_uval = PSW.y_from_line(my_rval, slope, intercept)


	return my_uval

#Finding our solar wind speed!
input_solar_wind_speed = interpolating(left_point, right_point, r_vals, u_vals, radial_distance)

# -----------------------------------
# Printing & Visualizing Final Answer
# -----------------------------------

'''
The following prints and graphs out the value of our 
solar wind speed at the input r-value, relative to the 
rest of the generated speeds and distances from our RK4 
integration.
'''

#Printing out the final answer 
print('Solar Wind Speed at a distance of', radial_distance, 'km from the Sun =', input_solar_wind_speed ,'km s^-1')

#Setting font to Times New Roman for our plots
plt.rcParams['font.family']= 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

#Plotting our velocity & distance distribution 

fig, ax = plt.subplots()

ax.plot(r_vals, u_vals, color='darkgreen')
ax.axvline(radial_distance, 0, 1200, linestyle='dashed', color='indigo', label=f'Input Radius, {(radial_distance)} km')
ax.axvline(r_c, 0, 1200, linestyle='dotted', color='maroon', label=f'Critical Radius, {round(r_c,3)} km')
ax.scatter(radial_distance, input_solar_wind_speed, color='purple', marker='*', label=f'Speed at Input Radius = {round(input_solar_wind_speed,3)} km/s$^2$', s=100)
ax.axvline(149e6, 0, 1200, linestyle='dotted', color='cadetblue', label='Earth Distance, 149$^{10}$ km')
ax.set_xlabel('Radial Distance From Sun [km]')
ax.set_ylabel('Solar Wind Speed [km/s]')
ax.legend()

plt.savefig(output_filepath_PSW_graph)
#plt.show()


# ----------------
# Parker Spiral 
# ----------------

'''
The following is not integral to the calculation
of the solar wind speed at the input radial distnace, 
however, it provides an additional visualization via
The Parker Spiral. The Parker Spiral is discussed 
in further detail in the README file, but in essence, 
it depicts the dispersion of the Sun's Mangetic field 
given its rotation speed and the velocity of the solar 
wind (calculated in the above sections).

'''

#Setting constants
solar_omega = 2.7e-6 #Solar angular velocity [rad s^-1]

#Setting two difference cases for plotting parameters, given input radius

if radial_distance < 150e6: 
	r_vals_new = r_vals[0:149] #setting a smaller r-value range to visualize the spiral easier
	u_vals_new = u_vals[0:149]
	phi_vals = PSW.euler_method_parker(solar_omega, r_vals_new, u_vals_new)

	#Creating multiple spirals (incriments of pi/4)
	dPhi = np.pi/4

	phi_one = phi_vals				#dPhi = 0
	phi_two = phi_one + dPhi		#dPhi = pi/4
	phi_three = phi_two + dPhi		#dPhi = pi/2
	phi_four = phi_three + dPhi		#dPhi = 3*pi/4
	phi_five = phi_four + dPhi		#dPhi = pi
	phi_six = phi_five + dPhi		#dPhi = 5*pi/4
	phi_seven = phi_six + dPhi		#dPhi = 3*pi/2
	phi_eight = phi_seven + dPhi 	#dPhi = 7*pi/4


	#Setting phi and radius ranges to plot necessary circles
	phi_circle = np.linspace(0, 2*np.pi, 50)
	earth_rad_circ = np.full(50, 149e6)
	venus_rad_circ = np.full(50, 108.64e6 )
	input_rad_circ = np.full(50, radial_distance)

	#Plotting our spirals in a polar coordinate plot
	fig, ax = plt.subplots(subplot_kw={'projection':'polar'})

	#Plotting the B field lines 
	ax.plot(phi_one, r_vals_new, color='darkgreen', label='Sun Magnetic Field')
	ax.plot(phi_two, r_vals_new, color='lightseagreen', alpha=0.5)
	ax.plot(phi_three, r_vals_new, color='darkgreen')
	ax.plot(phi_four, r_vals_new, color='lightseagreen', alpha=0.5)
	ax.plot(phi_five, r_vals_new, color='darkgreen')
	ax.plot(phi_six, r_vals_new, color='lightseagreen', alpha=0.5)
	ax.plot(phi_seven, r_vals_new, color='darkgreen')
	ax.plot(phi_eight, r_vals_new, color='lightseagreen', alpha=0.5)

	#Plotting problem specific locations/reference locations
	ax.scatter(0, radial_distance, color='purple', marker='*', label=f'Input Radius, {round(radial_distance,3)} km', s=100)
	ax.plot(phi_circle, earth_rad_circ, color='cyan', linestyle='dashed', label='Earth Radius')
	ax.plot(phi_circle, input_rad_circ, color='indigo', linestyle='dashed')
	ax.plot(phi_circle, venus_rad_circ, color='goldenrod', linestyle='dashed', label='Venus Radius')

	#Setting plot lables/visuals
	ax.legend(loc='lower left', bbox_to_anchor=(0.5 + np.cos(20)/2, 0.5 + np.sin(20)/2))	
	ax.set_xlabel('Solar Magnetic Field Angular Position')


	plt.savefig(output_filepath_p_spiral)
	plt.show()


else: 

	#Calculating our angular position valus for magnetic field via Euler's Method
	phi_vals = PSW.euler_method_parker(solar_omega, r_vals, u_vals)

	#Creating multiple spirals (incriments of pi/4)
	dPhi = np.pi/4

	phi_one = phi_vals				#dPhi = 0
	phi_two = phi_one + dPhi		#dPhi = pi/4
	phi_three = phi_two + dPhi		#dPhi = pi/2
	phi_four = phi_three + dPhi		#dPhi = 3*pi/4
	phi_five = phi_four + dPhi		#dPhi = pi
	phi_six = phi_five + dPhi		#dPhi = 5*pi/4
	phi_seven = phi_six + dPhi		#dPhi = 3*pi/2
	phi_eight = phi_seven + dPhi 	#dPhi = 7*pi/4


	#Setting phi and radius ranges to plot necessary circles
	phi_circle = np.linspace(0, 2*np.pi, 50)
	earth_rad_circ = np.full(50, 149e6)
	jup_rad_circ = np.full(50, 766.44e6 )
	input_rad_circ = np.full(50, radial_distance)

	#Plotting our spirals in a polar coordinate plot
	fig, ax = plt.subplots(subplot_kw={'projection':'polar'})

	#Plotting the B field lines 
	ax.plot(phi_one, r_vals, color='darkgreen', label='Sun Magnetic Field')
	ax.plot(phi_two, r_vals, color='lightseagreen', alpha=0.5)
	ax.plot(phi_three, r_vals, color='darkgreen')
	ax.plot(phi_four, r_vals, color='lightseagreen', alpha=0.5)
	ax.plot(phi_five, r_vals, color='darkgreen')
	ax.plot(phi_six, r_vals, color='lightseagreen', alpha=0.5)
	ax.plot(phi_seven, r_vals, color='darkgreen')
	ax.plot(phi_eight, r_vals, color='lightseagreen', alpha=0.5)

	#Plotting problem specific locations/reference locations
	ax.scatter(0, radial_distance, color='purple', marker='*', label=f'Input Radius, {round(radial_distance,3)} km', s=100)
	ax.plot(phi_circle, earth_rad_circ, color='cyan', linestyle='dashed', label='Earth Radius')
	ax.plot(phi_circle, input_rad_circ, color='indigo', linestyle='dashed')
	ax.plot(phi_circle, jup_rad_circ, color='darkorange', linestyle='dashed', label='Jupiter Radius')

	#Setting plot lables/visuals
	ax.legend(loc='lower left', bbox_to_anchor=(0.5 + np.cos(20)/2, 0.5 + np.sin(20)/2))	
	ax.set_xlabel('Solar Magnetic Field Angular Position')


	plt.savefig(output_filepath_p_spiral)
	#plt.show()
