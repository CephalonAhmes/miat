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

vlines,hlines=miat.lines_tool(fig,2,axes=[ax0])
