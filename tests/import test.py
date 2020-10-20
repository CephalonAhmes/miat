# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 23:40:57 2020

@author: Philippe
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


radii=miat.lines_buttons.main(fig,1)