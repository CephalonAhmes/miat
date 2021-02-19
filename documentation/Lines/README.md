The line tool allows you to measure deltas and positions on a figure. Let's start with an example. We want to analyse a sine with noise, which I'll generate below. The figure also has a second ax with a defferent view.

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

We then just pass the figure object to the function below:

	vlines,hlines=miat.lines_tool(fig,2,axes=[ax0])

The second argument specifies how many markers you want in each group. If you want to specify which axes the lines appear on, use the axes argument with a list of the axes. By default, they'll show up on all the axes, so it might not work too well if the axes are completely different from each other. Finally, all the markers are removed once you're done by default. If you want to change this behavior, just set the clear argument to False.

If you run this, you will see this:
![](https://github.com/CephalonAhmes/miat/blob/main/documentation/Lines/Figure_1.png?raw=true)

Use the green buttons to add vertical/horizontal lines, and the red ones, to delete them. Click on a line to move it and click again to lock it in place.

To measure the sine amplitude and period, I'd do something like this:
![](https://github.com/CephalonAhmes/miat/blob/main/documentation/Lines/Figure_2.png?raw=true)


Close the figure to return to your code. The results are returned to you in vlines and hlines. The result for each will be a numpy array of shape (X,Y), the X rows are for each marker group and the Y columns are for each marker in a group. 


