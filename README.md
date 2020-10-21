This library's purpose is to help measuring graphics and figures directly in you python IDLE instead of having to save them, then use programs like ImageJ to measure data on them. 

If you want to use this, just pip install miat.

From there, using from miat_pkg import miat will allow you to use miat's tools. There aren't many for now, but I'll eventually add more. The tools currently in place will allow you to add horizontal and vertcal bars to a figure or image, which is useful for measuring deltas, for example. The second tool allows you to add circular markers to a figure. One usecase I can think of would be to measure circular diffraction patterns.

All markers can be used in groups of 1, 2 or 3, which will have the same color. The lines too can span across multiple axes, or specific axes if you provide the necessary axes list parameter. This library also works for imshow figures, although it is a bit slow, since I haven't really optimisez it yet.


An example would be something like this:


"""
	import numpy as np
	import matplotlib.pyplot as plt
	from miat_pkg import miat

	fig=plt.figure()

	a=np.arange(20)
	b=np.arange(20)
	ax0 = fig.add_subplot(111)
	ax0.plot(a,b)
	ax0.set_ylabel('b')
	ax0.set_title('ab')


	vertical_positions,horizontal_positions=miat.lines_buttons.main(fig,1)


	fig=plt.figure()

	a=np.arange(20)
	b=np.arange(20)
	ax0 = fig.add_subplot(111)
	ax0.plot(a,b)
	ax0.set_ylabel('b')
	ax0.set_title('ab')


	radii=miat.circles_buttons.main(ax0,1)
"""