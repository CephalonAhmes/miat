The circle tool allows you to measure a radius on a figure. Let's start with an example. We want to analyse the zeeman_effect.png image.

	import matplotlib.pyplot as plt
	import miat.tools as miat
	import matplotlib.image as mpimg


	img= mpimg.imread('zeeman_effect_image.png')
	fig=plt.figure()

	ax0 = fig.add_subplot(111)
	ax0.imshow(img)
	ax0.set_title('circular diffusion pattern')

So, we've created the figure. All we have to do is pass this figure to the circles_tool function with a few parameters:


	radii=miat.circles_tool(ax0,2)

Notice how the main function takes an ax object, not a figure object. The secomd parameter represents how many circles you want to have in one group (meaning they'll have the same color). You can also use the linestyle argument if you want something other than plain old 'solid'. By default, all the markers are removed once you're done. If you want to change this behavior, just set the clear argument to False.

You'll get something like this: ![](https://github.com/CephalonAhmes/miat/blob/main/documentation/Circles/Figure_1.png?raw=true)

There are now new tools in the toolbar, which are used to add/remove circle markers (to remove, use the red buttons). After you use them, left-click on a circle and move the mouse to resize. If you right-click instead, you can move it around. Click again to lock it in place in either case.



Adjust as you want, an end results looks like this: ![](https://github.com/CephalonAhmes/miat/blob/main/documentation/Circles/Figure_2.png?raw=true)

Close the figure to return to your code and get the results returned to you. The result will be a numpy array of shape (X,Y), the X rows are for each marker group and the Y columns are for each marker in a group. 
