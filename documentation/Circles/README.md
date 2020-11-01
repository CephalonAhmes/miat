The circle too allows you to measure radii on a figure. Let's start with an example. We want to analyse the zeeman effect image.

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

You'll get something like ![this]()