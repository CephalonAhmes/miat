import matplotlib.pyplot as plt
import miat.tools as miat
import matplotlib.image as mpimg


img= mpimg.imread('zeeman_effect_image.png')
fig=plt.figure()

ax0 = fig.add_subplot(111)
ax0.imshow(img)
ax0.set_title('circular diffusion pattern')

radii=miat.circles_tool(ax0,2)