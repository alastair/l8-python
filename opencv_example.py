# Stream webcam video to l8smartlight
# By Carlos Garcia Saura ( http://carlosgs.es )

import time

import numpy as np
import cv
import cv2
cap = cv2.VideoCapture(0)

width = 640 #leave None for auto-detection
height = 480 #leave None for auto-detection
cap.set(cv.CV_CAP_PROP_FRAME_WIDTH,width)
cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT,height)

cap.set(cv.CV_CAP_PROP_FPS,30)

import l8
l = l8.L8Bt("EX:AM:PL:EM:AC:AD")

time.sleep(1)

l.back_light(l8.Colour(0,0,0))
l.send_clear()

#import random
#mtx = [ [ l8.Colour(0,0,0) for i in range(8) ] for j in range(8) ]

#for i in range(255):
#	mtx[4][4] = l8.Colour(i,0,0)
#	l.send_matrix(mtx)
#	l.back_light(l8.Colour(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
#	time.sleep(1)
#l.set_light(4, 4, l8.Colour(0,0,0))

#import random
#for i in range(16):
#	l.set_light(4, 4, l8.Colour(i,0,0))
#	l.back_light(l8.Colour(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
#	time.sleep(1)
#l.set_light(4, 4, l8.Colour(0,0,0))


gamma = 1.5
def adaptColor(c):
	global gamma
	#gamma = 1.
	
	c.r = float(c.r)/255.
	c.g = float(c.g)/255.
	c.b = float(c.b)/255.
	
	r = c.r**gamma
	g = c.g**gamma
	b = c.b**gamma
	
	rgb = r+g+b
	crgb = c.r+c.g+c.b
	if crgb != 0:
		constant = 255.*float(rgb)/float(crgb)
	else:
		constant = 255.
	
	r = int(round(constant*r))
	g = int(round(constant*g))
	b = int(round(constant*b))
	
	#r = int(round(255.*(c.r/255.)**gamma))
	#g = int(round(255.*(c.g/255.)**gamma))
	#b = int(round(255.*(c.b/255.)**gamma))

	if r > 255: r = 255
	if g > 255: g = 255
	if b > 255: b = 255
	return l8.Colour(r,g,b)


while(1):
	_,frame = cap.read()
	
	src = np.array([[0,0],[480,0],[480,480]],np.float32)
	dst = np.array([[0,0],[480,0],[480,480]],np.float32)
	M_aff = cv2.getAffineTransform(src, dst)
	frame = cv2.warpAffine(frame, M_aff, (480,480))
	
	#frame = cv2.GaussianBlur(frame, ksize=(0,0), sigmaX=20)
	
	scaled_frame = cv2.resize(frame,(8,8),interpolation=cv2.INTER_AREA)
	scaled_frame_big = cv2.resize(scaled_frame,(480,480), interpolation=cv2.INTER_NEAREST)
	
	mtx = [ [ adaptColor(l8.Colour(scaled_frame[j][i][2],scaled_frame[j][i][1],scaled_frame[j][i][0])) for i in range(8) ] for j in range(8) ]
	l.send_matrix(mtx)
	cv2.imshow("frame",frame)
	
	cv2.imshow("result",scaled_frame_big)
	
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break
	if key == ord('g'):
		gamma -= 0.01
		print(gamma)

time.sleep(1)

l.send_clear()
cv2.destroyAllWindows()
cap.release()

