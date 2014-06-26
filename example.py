import time

import l8
l = l8.L8Serial("/dev/ttyACM0")

l.back_light(l8.Colour(255, 255, 0))

l.set_light(4, 6, l8.Colour(50, 100, 10))

import random
mtx = [ [ l8.Colour(random.randrange(20,255), random.randrange(20, 255), random.randrange(0, 255)) for i in range(8) ] for j in range(8) ]
l.send_matrix(mtx)

time.sleep(1)

l.send_clear()

