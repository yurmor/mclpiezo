verbose = False
from ctypes import cdll, c_int, c_uint, c_double
import atexit
from time import sleep
import numpy as np

class Madpiezo():
	def __init__(self):
		# provide valid path to Madlib.dll. Madlib.h and Madlib.lib should also be in the same folder
		path_to_dll = 'Madlib.dll'
		self.madlib = cdll.LoadLibrary(path_to_dll)
		
		self.handler = self.mcl_start()
		atexit.register(self.mcl_close)
	def mcl_start(self):
		"""
		Requests control of a single Mad City Labs Nano-Drive.

		Return Value:
			Returns a valid handle or returns 0 to indicate failure.
		"""
		mcl_init_handle = self.madlib['MCL_InitHandle']
		
		mcl_init_handle.restype = c_int
		handler = mcl_init_handle()
		if(handler==0):
			print "MCL init error"
			return
		if verbose: print "handler = ", handler
		return 	handler
	def mcl_read(self,axis_number):
		"""
		Read the current position of the specified axis.
	
		Parameters:
			axis [IN] Which axis to move. (X=1,Y=2,Z=3,AUX=4)
			handle [IN] Specifies which Nano-Drive to communicate with.
		Return Value:
			Returns a position value or the appropriate error code.
		"""
		mcl_single_read_n = self.madlib['MCL_SingleReadN']
		mcl_single_read_n.restype = c_double
		return  mcl_single_read_n(c_uint(axis_number), c_int(self.handler))
	def mcl_write(self,position, axis_number):
		"""
		Commands the Nano-Drive to move the specified axis to a position.
	
		Parameters:
			position [IN] Commanded position in microns.
			axis [IN] Which axis to move. (X=1,Y=2,Z=3,AUX=4)
			handle [IN] Specifies which Nano-Drive to communicate with.
		Return Value:
			Returns MCL_SUCCESS or the appropriate error code.
		"""
		mcl_single_write_n = self.madlib['MCL_SingleWriteN']
		mcl_single_write_n.restype = c_int
		error_code = mcl_single_write_n(c_double(position), c_uint(axis_number), c_int(self.handler))
		
		if(error_code !=0):
			print "MCL write error = ", error_code
		return error_code
	def goxy(self,x_position,y_position):
		self.mcl_write(x_position,1)
		self.mcl_write(y_position,2)
	def goz(self,z_position):
		self.mcl_write(z_position,3)
	def get_position(self):
		return self.mcl_read(1), self.mcl_read(2), self.mcl_read(3)
	def mcl_close(self):
		"""
		Releases control of all Nano-Drives controlled by this instance of the DLL.
		"""
		mcl_release_all = self.madlib['MCL_ReleaseAllHandles']
		mcl_release_all()

if __name__ == "__main__":
	
	#simple scanning example
	
	# intialize the piezo
	piezo = Madpiezo()

	#will scan over a rectangular area, from (x1, y1) to (x2, y2) 
	#with len_x steps in x-direction and len_y steps in y-direction
	
	len_x = 64  # number of steps in x-direction
	len_y = 64  # number of steps in y-direction 
	x1, x2 = 0.,16. # x coordinates
	y1, y2 = 0., 16. # y coordinates
	z_postion = 50. # z position 
	
	wait_time = 0.01 # time to wait (seconds) after moving piezo to next position

	#create a 2d grid of x and y scanning positions
	x_pattern, y_pattern = np.meshgrid(np.linspace(x1, x2, len_x), np.linspace(y1, y2, len_y))
	scan_shape = np.shape(x_pattern)
	
	results = np.zeros(scan_shape) # create array to store the results of the measurements 
	
	#go to the origin of the scan
	piezo.goxy(x1,y1)
	piezo.goz(z_postion)
	
	# move the piezo over the scan area
	for index in np.ndindex(scan_shape):
		# go to the next position
		piezo.goxy(x_pattern[index],y_pattern[index])
		sleep(wait_time)

		# do some measurements here by calling measure_something() function and store the result
		# results(index) = measure_something() 
		
		print("Current position x,y,z = ", piezo.get_position())
	
