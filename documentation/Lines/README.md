The line tool allows you to measure deltas and positions on a figure. Let's start with an example. We want to analyse a sine with noise

	import matplotlib.pyplot as plt
	import miat.tools as miat
	import numpy as np

	x=np.linspace(0,20,100)
	y=np.sin(x)+np.random.uniform(-0.3,0.3,100)

	fig=plt.figure()

	ax0 = fig.add_subplot(211)
	ax0.plot(x,y)
	ax0.set_title('sine function')

	ax1 = fig.add_subplot(212)
	ax1.plot(x,y)
	ax1.set_ylim(-0.2,1.2)

	vlines,hlines=miat.lines_tool.main(fig,2,axes=[ax0])

Here, the lines_tool.main takes a figure object. If you want to specify which axes the lines appear on, use the axes argument with a list of the axes. By default, they'll show up on all the axes, so it might not work too well if the axes are completely different from each other.

If you run this, you will see this:
![](https://github.com/CephalonAhmes/miat/blob/main/documentation/Lines/Figure_1.png?raw=true)

Use the green buttons to add vertical/horizontal lines, and the red ones, which you don't see yet, to delete them. Click on a line to move it and click again to lock it in place.

To measure the sine amplitude and period, I'd do something like this:
![](https://github.com/CephalonAhmes/miat/blob/main/documentation/Lines/Figure_2.png?raw=true)

and 

	amplitude=vlines[0][1]-vlines[0][0]
	period=hlines[0][1]-hlines[0][0]

