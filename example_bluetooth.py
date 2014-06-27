import time
import l8
l = l8.L8Bt("EX:AM:PL:EM:AC:AD")

l.send_clear()

l.back_light(l8.Colour(255, 255, 0))

time.sleep(1)

l.set_light(4, 6, l8.Colour(50, 100, 10))

time.sleep(1)

import random
for i in range(100):
	mtx = [ [ l8.Colour(random.randrange(20,255), random.randrange(20, 255), random.randrange(0, 255)) for i in range(8) ] for j in range(8) ]
	l.send_matrix(mtx)
	time.sleep(0.1)

time.sleep(1)

l.send_clear()

