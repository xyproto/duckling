Measurements
------------

Measured on an old i686 laptop, trying to figure out which combinations of settings to use.

Update, Buffer, NoPsyco
Min FPS: 2.13356089592
Max FPS: 416.666656494			(best max, has little meaning)
Avg FPS: 2.14236441301

Update, Buffer, Psyco
Min FPS: 3.16455698013
Max FPS: 322.580657959
Avg FPS: 3.62431769678			(best average)

NoUpdate, Buffer, Psyco
Min FPS: 2.67737627029
Max FPS: 20.7039337158
Avg FPS: 2.83928850305

NoUpdate, Buffer, NoPsyco
Min FPS: 3.52858161926			(best minimum, doesn't use psyco, has a good average but
Max FPS: 22.0264320374			bad maximum).
Avg FPS: 3.54369260343

Conclusion so far:
	Check if psyco is possible to import at start
	Yes? Use update. No? Use flip.

Update, NoBuffer, Psyco
Min FPS: 3.49650359154
Max FPS: 384.615386963
Avg FPS: 3.88814009633
 
NoUpdate, Buffer, NoPsyco		(Best minimum and average so far)
Min FPS: 4.52898550034
Max FPS: 20.2020206451
Avg FPS: 4.53851686324

NoUpdate, Buffer, Psyco
Min FPS: 3.23519897461
Max FPS: 303.030303955
Avg FPS: 3.24037592935

