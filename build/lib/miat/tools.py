import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as Lines
from matplotlib.patches import Circle
from pathlib import Path
plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

#%%
color_list=["r","c","orange","g","purple","saddlebrown","deeppink","lime","gray"]

def _set_button_active(button,active):
	button.ax.images[0].set_visible(active)
	button.ax.patch.set_visible(active)
	button.label.set_visible(False)
	button.ax.axis({True:'on',False:'off'}[active])
	button.set_active(active)

class _draggable_lines:
	def __init__(self,axes,position,color,orientation,linestyle):
		self.orientation=orientation
		self.axes=axes
		self.canvas=axes[0].figure.canvas
		self.position=position
		self.lines=[Lines.Line2D(*{0:[[position,position],list(ax.get_ylim())],1:[list(ax.get_xlim()),[position,position]]}[orientation],picker=True,pickradius=4,c=color,linestyle=linestyle) for ax in self.axes]
		self.line_artists=[self.axes[i].add_line(self.lines[i]) for i in range(len(self.axes))]
		self.sid = self.canvas.mpl_connect('pick_event', self.clickonline)
		self.canvas.draw_idle()


	def clickonline(self, event):
		if event.artist in self.lines:
			[line_artist.set_visible(False) for line_artist in self.line_artists]
			self.canvas.draw()
			self.backgrounds=[self.canvas.copy_from_bbox(ax.bbox) for ax in self.axes]
			[line_artist.set_visible(True) for line_artist in self.line_artists]
			self.canvas.draw()
			self.follower = self.canvas.mpl_connect("motion_notify_event", self.followmouse)
			self.releaser = self.canvas.mpl_connect("button_press_event", self.releaseonclick)

	def followmouse(self, event):
		if event.xdata and event.ydata:
			[self.canvas.restore_region(background) for background in self.backgrounds]
			if self.orientation==1:
				[line.set_ydata([event.ydata, event.ydata]) for line in self.lines]
			if self.orientation==0:
				[line.set_xdata([event.xdata, event.xdata]) for line in self.lines]
			[self.axes[i].draw_artist(self.lines[i]) for i in range(len(self.axes))]
			[self.canvas.blit(ax.bbox) for ax in self.axes]

	def releaseonclick(self, event):
		[self.canvas.blit(ax.bbox) for ax in self.axes]
		self.position = {0:self.lines[0].get_xdata()[0],1:self.lines[0].get_ydata()[0]}[self.orientation]
		self.canvas.mpl_disconnect(self.releaser)
		self.canvas.mpl_disconnect(self.follower)

	def clear(self):
		[line.remove() for line in self.lines]
		self.canvas.draw()
		return self.position



class _draggable_circles:
	def __init__(self,ax,position,radius,color,linestyle):
		self.ax=ax
		self.canvas=ax.figure.canvas
		self.position=position
		self.radius=radius
		self.circle=Circle(position,radius,picker=self.circle_picker,color=color,linestyle=linestyle,fill=False)
		
		delta=min([self.ax.get_xlim()[1]-self.ax.get_xlim()[0],self.ax.get_ylim()[1]-self.ax.get_ylim()[0]])

		
		self.center_dot=Circle(position,delta/200,color=color)
		self.circle_artist=self.ax.add_artist(self.circle)
		self.center_dot_artist=self.ax.add_artist(self.center_dot)
		self.center_dot_artist.set_visible(False)
		

		
		self.sid = self.canvas.mpl_connect('pick_event', self.clickonline)
		self.sid_position_finder= self.canvas.mpl_connect('button_press_event',self.click_position_finder)
		self.drag=False
		self.canvas.draw_idle()

	
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
			self.center_dot_artist.set_visible(self.drag)
			self.canvas.draw()

	def clickonline(self, event):
		if event.artist==self.circle:
			self.center_dot_artist.set_visible(False)
			self.circle_artist.set_visible(False)
			self.canvas.draw()
			self.background=self.canvas.copy_from_bbox(self.ax.bbox)
			self.circle_artist.set_visible(True)
			self.center_dot_artist.set_visible(self.drag)
			self.canvas.draw()
			self.follower = self.canvas.mpl_connect("motion_notify_event", self.followmouse)
			self.releaser = self.canvas.mpl_connect("button_press_event", self.releaseonclick)
			self.toggler= self.canvas.mpl_connect("button_press_event",self.toggle_drag)

			
	def followmouse(self, event):
		if event.xdata and event.ydata:
			self.canvas.restore_region(self.background)
			newradius=((self.position[0]-event.xdata)**2+(self.position[1]-event.ydata)**2)**0.5
			centervector=(self.position[0]-self.clickevent_position[0],self.position[1]-self.clickevent_position[1])
			newcenter=(centervector[0]+event.xdata,centervector[1]+event.ydata)
			if not self.drag:
				self.circle.set_radius(newradius)
			if self.drag:
				self.center_dot.set_center(newcenter)
				self.circle.set_center(newcenter)
			self.ax.draw_artist(self.circle_artist)
			self.ax.draw_artist(self.center_dot_artist)
			self.canvas.blit(self.ax.bbox)

	def releaseonclick(self, event):
		if event.button==1:
			self.radius = self.circle.get_radius()
			self.position=self.circle.get_center()
			self.center_dot_artist.set_visible(False)
			self.canvas.mpl_disconnect(self.releaser)
			self.canvas.mpl_disconnect(self.follower)
			self.canvas.mpl_disconnect(self.toggler)
			self.canvas.draw_idle()


	def clear(self):
		self.circle.remove()
		self.canvas.draw()
		return self.radius

class toolbarbutton(ToolBase):
	def __init__(self,*args,**kwargs):
		self.image=kwargs.pop('image')
		self.func=kwargs.pop('func')
		self.description=kwargs.pop('description')
		ToolBase.__init__(self, *args, **kwargs)
		self.toggle(True)

	def toggle(self,active):
		self._active=active
		
	def trigger(self, *args, **kwargs):
		if self._active:
			self.func()




class circles_tool:
	def __init__(self,ax,marker_group_size,linestyle,clear):
		self.marker_group_size=marker_group_size
		self.canvas=ax.figure.canvas
		self.markers=[]
		self.linestyle=linestyle
		self.clear=clear
		self.ax=ax
		self.tm = self.canvas.manager.toolmanager
		self.tb=self.canvas.manager.toolbar


		self.add_tool=self.tm.add_tool('add',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'add_{}_circles_icon.png'.format(marker_group_size)),
					func=self.add_f,
					description='Add circles',
					)
		
		self.remove_tool=self.tm.add_tool('remove',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'remove_{}_circles_icon.png'.format(marker_group_size)),
					func=self.delete_f,
					description='Remove circles',
					)
		
		self.tb.add_tool(self.add_tool, "foo",0)
		self.tb.add_tool(self.remove_tool, "foo",1)
		
		self.check_marker_count()
		
	def add_f(self):
		current_radii=np.array([[marker.radius for marker in markergroup] for markergroup in self.markers]).flatten()
		xlimits_array=np.linspace(*self.ax.get_xlim(),100)
		ylimits_array=np.linspace(*self.ax.get_ylim(),100)
		center=(xlimits_array[50],ylimits_array[50])
		possible_radii=xlimits_array[55:]-center[0]
		selected_color=color_list[len(self.markers)]
		selected_radii=[]
		for i in range(self.marker_group_size):
			while True:
				random_radii=np.random.choice(possible_radii)
				if (random_radii not in selected_radii) and (abs((random_radii-current_radii)/(possible_radii[0]-possible_radii[-1]))>0.05).all():
					selected_radii.append(random_radii)
					break
		self.markers.append([_draggable_circles(self.ax,center,selected_radii[marker],selected_color,self.linestyle) for marker in range(self.marker_group_size)])
		self.check_marker_count()
		
	def delete_f(self):
		[marker.clear() for marker in self.markers[-1]]
		del self.markers[-1:]
		self.check_marker_count()
		
	def check_marker_count(self):
		if len(self.markers)==len(color_list):
			self.add_tool.toggle(False)
		elif len(self.markers)<len(color_list) and len(self.markers)>0:
			self.add_tool.toggle(True)
			self.remove_tool.toggle(True)
		elif len(self.markers)==0:
			self.remove_tool.toggle(False)
		
	def returnpositions(self):
		if self.clear:
			unsorted=[[marker.clear() for marker in markergroup] for markergroup in self.markers]
			self.canvas.draw_idle()
		if not self.clear:
			unsorted=[[marker.radius for marker in markergroup] for markergroup in self.markers]
		for i in unsorted:
			i.sort()
		return unsorted
	
	def handle_close(self,event):
		self.canvas.stop_event_loop()
		
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
	
		plt.get_current_fig_manager().window.showMaximized()

		circles_tool_obj=circles_tool(ax,markergroupsize,linestyle,clear)
		plt.show()

		ax.figure.canvas.mpl_connect('close_event', circles_tool_obj.handle_close)
		
		ax.figure.canvas.start_event_loop()
		
		return circles_tool_obj.returnpositions()




class lines_tool:
	def __init__(self,canvas,marker_group_size,linestyle,axes,clear):
		self.marker_group_size=marker_group_size
		self.canvas=canvas
		self.markers=[[],[]]
		self.linestyle=linestyle
		self.clear=clear
		
		if axes==None:
			self.axes=self.canvas.figure.get_axes()
		else:
			self.axes=axes
		
		self.tm = self.canvas.manager.toolmanager
		self.tb=self.canvas.manager.toolbar
		markerindex_dic={'v':0,'h':1}


		self.add_v_tool=self.tm.add_tool('add_v',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'add_{}_vbar_icon.png'.format(marker_group_size)),
					func=(lambda: self.add_f(markerindex_dic['v'])),
					description='Add vertical lines',
					)
		
		self.remove_v_tool=self.tm.add_tool('remove_v',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'remove_{}_vbar_icon.png'.format(marker_group_size)),
					func=(lambda: self.delete_f(markerindex_dic['v'])),
					description='Remove vertical lines',
					)
		self.add_h_tool=self.tm.add_tool('add_h',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'add_{}_hbar_icon.png'.format(marker_group_size)),
					func=(lambda: self.add_f(markerindex_dic['h'])),
					description='Add horizontal lines',
					)
		
		self.remove_h_tool=self.tm.add_tool('remove_h',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'remove_{}_hbar_icon.png'.format(marker_group_size)),
					func=(lambda: self.delete_f(markerindex_dic['h'])),
					description='Remove horizontal lines',
					)
		
		self.tb.add_tool(self.add_v_tool, "foo",0)
		self.tb.add_tool(self.remove_v_tool, "foo",1)
		self.tb.add_tool(self.add_h_tool, "foo",2)
		self.tb.add_tool(self.remove_h_tool, "foo",3)
		
		self.buttons=[[self.add_v_tool,self.remove_v_tool],[self.add_h_tool,self.remove_h_tool]]
		
		self.check_marker_count(markerindex_dic['v'])
		self.check_marker_count(markerindex_dic['h'])
		
	def add_f(self,orientation):
		current_positions=np.array([[marker.position for marker in markergroup] for markergroup in self.markers[orientation]]).flatten()
		possible_positions_x=np.linspace(*self.canvas.figure.get_axes()[0].get_xlim(),100)[10:-10]
		possible_positions_y=np.linspace(*self.canvas.figure.get_axes()[0].get_ylim(),100)[10:-10]
		possible_positions=[possible_positions_x,possible_positions_y][orientation]
		selected_color=color_list[len(self.markers[orientation])]
		selected_positions=[]
		for i in range(self.marker_group_size):
			while True:
				random_position=np.random.choice(possible_positions)
				if (random_position not in selected_positions) and (abs((random_position-current_positions)/(possible_positions[0]-possible_positions[-1]))>0.05).all():
					selected_positions.append(random_position)
					break
		self.markers[orientation].append([_draggable_lines(self.axes,selected_positions[marker],selected_color,orientation,self.linestyle) for marker in range(self.marker_group_size)])
		self.check_marker_count(orientation)
		
	def delete_f(self,orientation):
		[marker.clear() for marker in self.markers[orientation][-1]]
		del self.markers[orientation][-1:]
		self.check_marker_count(orientation)
		
	def check_marker_count(self,orientation):
		if len(self.markers[orientation])==len(color_list):
			self.buttons[orientation][0].toggle(False)
		elif len(self.markers[orientation])<len(color_list) and len(self.markers[orientation])>0:
			self.buttons[orientation][0].toggle(True)
			self.buttons[orientation][1].toggle(True)
		elif len(self.markers[orientation])==0:
			self.buttons[orientation][1].toggle(False)
		self.canvas.draw_idle()

		
	def returnpositions(self):
		if self.clear:
			unsorted=[[[marker.clear() for marker in markergroup] for markergroup in self.markers[orientation]] for orientation in range(len(self.markers))]
			self.canvas.draw_idle()
		if not self.clear:
			unsorted=[[[marker.position for marker in markergroup] for markergroup in self.markers[orientation]] for orientation in range(len(self.markers))]
		for i in range(len(unsorted)):
			for ii in unsorted[i]:
				ii.sort()
		return unsorted
	
	def handle_close(self,event):
		self.canvas.stop_event_loop()
		
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
	
	
		lines_tool_obj=lines_tool(figure.canvas,markergroupsize,linestyle,axes,clear)
		
		figure.canvas.mpl_connect('close_event', lines_tool_obj.handle_close)
		plt.get_current_fig_manager().window.showMaximized()
		plt.show()
		
		figure.canvas.start_event_loop()
		
		
		return lines_tool_obj.returnpositions()

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
	
	pos=lines_tool.main(fig,2)

	fig=plt.figure()
	
	a=np.arange(20)
	b=np.arange(20)
	ax0 = fig.add_subplot(111)
	ax0.plot(a,b)
	ax0.set_ylabel('b')
	ax0.set_title('ab')
	ax0.set_xlabel('a')
	
	rad=circles_tool.main(ax0,1,clear=True)
