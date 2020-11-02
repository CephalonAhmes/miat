The circle tool allows you to measure radii on a figure. Let's start with an example. We want to analyse the zeeman effect image.

	import matplotlib.pyplot as plt
	import miat.tools as miat
	import matplotlib.image as mpimg


	img= mpimg.imread('zeeman_effect_image.png')
	fig=plt.figure()

	ax0 = fig.add_subplot(111)
	ax0.imshow(img)
	ax0.set_title('circular diffusion pattern')


	radii=miat.circles_tool.main(ax0,2)

Notice how the main function takes an ax object, not a figure object.

You'll get something like this: ![](https://github.com/CephalonAhmes/miat/blob/V0.0.8/documentation/Circles/Figure_2.png?raw=true). Notice the green buttons in the bottom-left corner? They are used to add/remove circle markers (to remove, use the red buttons). After you use them, click on a circle and move the mouse to resize. If you right-click after having selected a circle, you can move it around. Click again to lock it in place.



Adjust as you want, an end results looks like this: ![](https://github.com/CephalonAhmes/miat/blob/V0.0.8/documentation/Circles/Figure_1.png?raw=true)

To get a delta, use radii[0][1]-radii[0][0].