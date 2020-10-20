import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as Lines
from matplotlib.patches import Circle
from matplotlib.widgets import Button
from pathlib import Path
#%%
color_list=["r","c","orange","g","purple","saddlebrown","deeppink","lime","gray"]

class draggable_lines:
	def __init__(self,axes,position,color,orientation,linestyle):
		self.orientation=orientation
		self.axes=axes
		self.canvas=axes[0].figure.canvas
		self.position=position
		self.lines=[Lines.Line2D(*{0:[[position,position],list(ax.get_ylim())],1:[list(ax.get_xlim()),[position,position]]}[orientation],picker=True,pickradius=4,c=color,linestyle=linestyle) for ax in self.axes]
		[self.axes[i].add_line(self.lines[i]) for i in range(len(self.axes))]
		self.sid = self.canvas.mpl_connect('pick_event', self.clickonline)
		self.canvas.draw_idle()

	def clickonline(self, event):
		if event.artist in self.lines:
			self.follower = self.canvas.mpl_connect("motion_notify_event", self.followmouse)
			self.releaser = self.canvas.mpl_connect("button_press_event", self.releaseonclick)

	def followmouse(self, event):
		if self.orientation==1:
			[line.set_ydata([event.ydata, event.ydata]) for line in self.lines]
		if self.orientation==0:
			[line.set_xdata([event.xdata, event.xdata]) for line in self.lines]
		self.canvas.draw_idle()

	def releaseonclick(self, event):
		self.position = {0:self.lines[0].get_xdata()[0],1:self.lines[0].get_ydata()[0]}[self.orientation]
		self.canvas.mpl_disconnect(self.releaser)
		self.canvas.mpl_disconnect(self.follower)

	def clear(self):
		[line.remove() for line in self.lines]
		self.canvas.draw()
		return self.position



class draggable_circles:
	def __init__(self,ax,position,radius,color,linestyle):
		self.ax=ax
		self.canvas=ax.figure.canvas
		self.position=position
		self.radius=radius
		self.circle=Circle(position,radius,picker=self.circle_picker,color=color,linestyle=linestyle,fill=False)
		self.ax.add_artist(self.circle)
		self.sid = self.canvas.mpl_connect('pick_event', self.clickonline)
		self.sid_position_finder= self.canvas.mpl_connect('button_press_event',self.click_position_finder)
		self.canvas.draw_idle()
		self.closed=False
		self.drag=False
	
	def circle_picker(self,circle,mouseevent):
		if mouseevent.xdata is None:
			return False, dict()
		xdata,ydata = circle.get_center()
		radius=circle.get_radius()
		tolerance = 0.05
		d = np.sqrt(
			(xdata - mouseevent.xdata)**2 + (ydata - mouseevent.ydata)**2)

		if d>=radius*(1-tolerance) and d<=radius*(1+tolerance):
			pickx = xdata
			picky = ydata
			props = dict(pickx=pickx, picky=picky)
			return True,props
		else:
			return False, dict()
		
	
	def click_position_finder(self,event):
		self.clickevent_position=(event.xdata,event.ydata)

	def toggle_drag(self,event):
		if event.button==3:
			self.radius = self.circle.get_radius()
			self.position=self.circle.get_center()
			self.drag=not self.drag

	def clickonline(self, event):
		if event.artist==self.circle:
			self.follower = self.canvas.mpl_connect("motion_notify_event", self.followmouse)
			self.releaser = self.canvas.mpl_connect("button_press_event", self.releaseonclick)
			self.toggler= self.canvas.mpl_connect("button_press_event",self.toggle_drag)
			
	def followmouse(self, event):
		newradius=((self.position[0]-event.xdata)**2+(self.position[1]-event.ydata)**2)**0.5
		centervector=(self.position[0]-self.clickevent_position[0],self.position[1]-self.clickevent_position[1])
		newcenter=(centervector[0]+event.xdata,centervector[1]+event.ydata)
		if not self.drag:
			self.circle.set_radius(newradius)
		if self.drag:
			self.circle.set_center(newcenter)
		self.canvas.draw_idle()

	def releaseonclick(self, event):
		if event.button==1:
			self.radius = self.circle.get_radius()
			self.position=self.circle.get_center()
			self.canvas.mpl_disconnect(self.releaser)
			self.canvas.mpl_disconnect(self.follower)
			self.canvas.mpl_disconnect(self.toggler)

	def clear(self):
		self.circle.remove()
		self.canvas.draw()
		return self.radius


class circles_buttons:
	def __init__(self,ax,marker_group_size,linestyle,clear):
		self.marker_group_size=marker_group_size
		self.canvas=ax.figure.canvas
		self.markers=[]
		self.linestyle=linestyle
		self.closed=False
		self.clear=clear
		self.ax=ax
		
		
		ypos,height,width= 0.0, 0.07, 0.07
		add_data=(plt.axes([0.0,ypos,height,width]), 'add_{}_circles_icon.png'.format(marker_group_size),self.add_f)
		del_data=(plt.axes([0.05,ypos,height,width]), 'remove_{}_circles_icon.png'.format(marker_group_size),self.delete_f)
		self.buttons_data=[add_data,del_data]
		
		add_button=self.activate_button(*self.buttons_data[0])
		del_button=self.activate_button(*self.buttons_data[1])
		self.buttons=[add_button,del_button]
		
		self.check_marker_count()
		
	def activate_button(self,loc,impath:str,func):
		path = Path(__file__).parent / "icons/" / impath
		temp_button_ref=Button(loc,'',image=plt.imread(path))
		temp_button_ref.on_clicked(lambda event: func(event))
		return temp_button_ref
	
	def add_f(self,event):
		current_radii=np.array([[marker.radius for marker in markergroup] for markergroup in self.markers]).flatten()
		limits_array=np.linspace(*self.ax.get_xlim(),100)
		center=(limits_array[50],limits_array[50])
		possible_radii=limits_array[50:]-center[0]
		selected_color=color_list[len(self.markers)]
		selected_radii=[]
		for i in range(self.marker_group_size):
			while True:
				random_radii=np.random.choice(possible_radii)
				if (random_radii not in selected_radii) and (abs((random_radii-current_radii)/(possible_radii[0]-possible_radii[-1]))>0.01).all():
					selected_radii.append(random_radii)
					break
		self.markers.append([draggable_circles(self.ax,center,selected_radii[marker],selected_color,self.linestyle) for marker in range(self.marker_group_size)])
		self.check_marker_count()
		
	def delete_f(self,event):
		[marker.clear() for marker in self.markers[-1]]
		del self.markers[-1:]
		self.check_marker_count()
		
	def check_marker_count(self):
		if len(self.markers)==len(color_list):
			self.buttons[0]=False
		elif len(self.markers)<len(color_list) and len(self.markers)>0:
			if self.buttons[0]==False:
				self.buttons[0]=self.activate_button(*self.buttons_data[0])
			if self.buttons[1]==False:
				self.buttons[1]=self.activate_button(*self.buttons_data[1])
		elif len(self.markers)==0:
			self.buttons[1]=False
		self.canvas.draw_idle()
		
	def returnpositions(self):
		if self.clear:
			unsorted=[[marker.clear() for marker in markergroup] for markergroup in self.markers]
			button_axes=self.canvas.figure.get_axes()[-2:]
			[button_axes[i].axis('off') for i in range(2)]
			self.canvas.draw_idle()
		if not self.clear:
			unsorted=[[marker.radius for marker in markergroup] for markergroup in self.markers]
		for i in unsorted:
			i.sort()
		return unsorted
	
	def handle_close(self,event):
		self.closed=True
		
	def main(ax,markergroupsize:int=1,linestyle='solid',clear=True):
		"""
		Adds two buttons on the figure that allow you to add circles on the plot. Click on the green one to add a circle group.
		The red one removes the last group.
		Click on the edge of a circle to select it and change its radius. Right click after having selected a circle to drag it. Left click again to lock selected circle

		Parameters
		----------
		ax : figure ax
			figure.add_suplot() object
		markergroupsize : int
			How many circles you want in a group. All the circles in said group will be the same color and their radius will be in the same
			sub-list in the returned list. The default is 1.
		linestyle : TYPE, optional
			Circle linestyle. The default is 'solid'.
		clear : bool, optional
			Remove all circles from the figure after it is closed. Useful if you still want to do something with it, like saving it.
			If you want to have the markers stay, set to False. The default is True.

		Raises
		------
		draggable_markersError
			

		Returns
		-------
		list
			list of the radii of all circles. Has the form [[group1],[group2],[group3]]. Each group sub-list is sorted

		"""
	
		if markergroupsize>3 or markergroupsize<1:
			raise draggable_markersError("Only supports marker groups sizes in the interval [1,3]")
		if plt.get_backend()!='Qt5Agg':
			raise draggable_markersError("Requires interactive backend. Switch to Qt5Agg by using plt.switch_backend('Qt5Agg'). This closes all current figures")
	
	
		circles_buttons_obj=circles_buttons(ax,markergroupsize,linestyle,clear)
		
		ax.figure.canvas.mpl_connect('close_event', circles_buttons_obj.handle_close)
		plt.get_current_fig_manager().window.showMaximized()
		plt.show()
		
		while circles_buttons_obj.closed==False:
			plt.pause(5)
		
		
		return circles_buttons_obj.returnpositions()




class lines_buttons:
	def __init__(self,canvas,marker_group_size,linestyle,axes,clear):
		self.marker_group_size=marker_group_size
		self.canvas=canvas
		self.markers=[[],[]]
		self.linestyle=linestyle
		self.closed=False
		self.clear=clear
		
		if axes==None:
			self.axes=self.canvas.figure.get_axes()
		else:
			self.axes=axes

		
		markerindex_dic={'v':0,'h':1}
		ypos,height,width= 0.0, 0.07, 0.07
		add_v_data=(plt.axes([0.0,ypos,height,width]), 'add_{}_vbar_icon.png'.format(marker_group_size),self.add_f,markerindex_dic['v'])
		del_v_data=(plt.axes([0.05,ypos,height,width]), 'remove_{}_vbar_icon.png'.format(marker_group_size),self.delete_f,markerindex_dic['v'])
		add_h_data=(plt.axes([0.1,ypos,height,width]), 'add_{}_hbar_icon.png'.format(marker_group_size),self.add_f,markerindex_dic["h"])
		del_h_data=(plt.axes([0.15,ypos,height,width]), 'remove_{}_hbar_icon.png'.format(marker_group_size),self.delete_f,markerindex_dic['h'])
		self.buttons_data=[[add_v_data,del_v_data],[add_h_data,del_h_data]]
		
		add_v_button=self.activate_button(*self.buttons_data[0][0])
		del_v_button=self.activate_button(*self.buttons_data[0][1])
		add_h_button=self.activate_button(*self.buttons_data[1][0])
		del_h_button=self.activate_button(*self.buttons_data[1][1])
		self.buttons=[[add_v_button,del_v_button],[add_h_button,del_h_button]]
		
		self.check_marker_count(markerindex_dic['v'])
		self.check_marker_count(markerindex_dic['h'])
		
	def activate_button(self,loc,impath:str,func,orientation):
		path = Path(__file__).parent / "icons/" / impath
		temp_button_ref=Button(loc,'',image=plt.imread(path))
		temp_button_ref.on_clicked(lambda event: func(event,orientation))
		return temp_button_ref
	
	def add_f(self,event,orientation):
		current_positions=np.array([[marker.position for marker in markergroup] for markergroup in self.markers[orientation]]).flatten()
		possible_positions_x=np.linspace(*self.canvas.figure.get_axes()[0].get_xlim(),100)[10:-10]
		possible_positions_y=np.linspace(*self.canvas.figure.get_axes()[0].get_ylim(),100)[10:-10]
		possible_positions=[possible_positions_x,possible_positions_y][orientation]
		selected_color=color_list[len(self.markers[orientation])]
		selected_positions=[]
		for i in range(self.marker_group_size):
			while True:
				random_position=np.random.choice(possible_positions)
				if (random_position not in selected_positions) and (abs((random_position-current_positions)/(possible_positions[0]-possible_positions[-1]))>0.01).all():
					selected_positions.append(random_position)
					break
		self.markers[orientation].append([draggable_lines(self.axes,selected_positions[marker],selected_color,orientation,self.linestyle) for marker in range(self.marker_group_size)])
		self.check_marker_count(orientation)
		
	def delete_f(self,event,orientation):
		[marker.clear() for marker in self.markers[orientation][-1]]
		del self.markers[orientation][-1:]
		self.check_marker_count(orientation)
		
	def check_marker_count(self,orientation):
		if len(self.markers[orientation])==len(color_list):
			self.buttons[orientation][0]=False
		elif len(self.markers[orientation])<len(color_list) and len(self.markers[orientation])>0:
			if self.buttons[orientation][0]==False:
				self.buttons[orientation][0]=self.activate_button(*self.buttons_data[orientation][0])
			if self.buttons[orientation][1]==False:
					self.buttons[orientation][1]=self.activate_button(*self.buttons_data[orientation][1])
		elif len(self.markers[orientation])==0:
			self.buttons[orientation][1]=False
		self.canvas.draw_idle()
		
	def returnpositions(self):
		if self.clear:
			unsorted=[[[marker.clear() for marker in markergroup] for markergroup in self.markers[orientation]] for orientation in range(len(self.markers))]
			button_axes=self.canvas.figure.get_axes()[-4:]
			[button_axes[i].axis('off') for i in range(4)]
			self.canvas.draw_idle()
		if not self.clear:
			unsorted=[[[marker.position for marker in markergroup] for markergroup in self.markers[orientation]] for orientation in range(len(self.markers))]
		for i in range(len(unsorted)):
			for ii in unsorted[i]:
				ii.sort()
		return unsorted
	
	def handle_close(self,event):
		self.closed=True
		
	def main(figure,markergroupsize:int=1,linestyle='solid',axes=None,clear=True):
		"""
		Adds four buttons on the figure that allow you to add lines on the plot. Click on the green ones to add a line group of corresponding orientation (vertical or horizontal).
		The red ones remove the last group of said orientation. 


		Parameters
		----------
		figure : plt.figure() object
			
		markergroupsize : int
			How many lines you want in a group. All the lines in said group will be the same color and their positions will be in the same
			sub-list in the returned list. The default is 1.
		linestyle : TYPE, optional
			The default is 'solid'.
		axes : list of plt.add_subplot() objects, optional
			Wich axes you want the lines to appear in. The default is 'All of them'.
		clear : bool, optional
			Remove all lines from the figure after it is closed. Useful if you still want to do something with it, like saving it.
			If you want to have the markers stay, set to False. The default is True.

		Raises
		------
		draggable_markersError
			

		Returns
		-------
		list
			list of the positions of all lines. Has the form [[[vertical group1],[vertical group2],[vertical group3]],[[horizontal group1],[horizontal group2],[horizontal group3]]]. Each group sub-list is sorted

		"""
	
		if markergroupsize>3 or markergroupsize<1:
			raise draggable_markersError("Only supports marker groups sizes in the interval [1,3]")
		if plt.get_backend()!='Qt5Agg':
			raise draggable_markersError("Requires interactive backend. Switch to Qt5Agg by using plt.switch_backend('Qt5Agg'). This closes all current figures")
	
	
		lines_buttons_obj=lines_buttons(figure.canvas,markergroupsize,linestyle,axes,clear)
		
		figure.canvas.mpl_connect('close_event', lines_buttons_obj.handle_close)
		plt.get_current_fig_manager().window.showMaximized()
		plt.show()
		
		while lines_buttons_obj.closed==False:
			plt.pause(5)
		
		
		return lines_buttons_obj.returnpositions()

class draggable_markersError(Exception):
	pass





if __name__=='__main__':
	#testing figure
	fig=plt.figure()
	
	a=np.arange(20)
	b=np.arange(20)
	ax0 = fig.add_subplot(211)
	ax0.plot(a,b)
	ax0.set_ylabel('b')
	ax0.set_title('ab')
	ax0.get_xaxis().set_visible(False)
	
	a=np.arange(20)
	b=np.arange(20)
	ax1 = fig.add_subplot(212)
	ax1.plot(a,b)
	ax1.set_xlabel('a')
	ax1.set_ylabel('b')
	
	pos=lines_buttons.main(fig,2)