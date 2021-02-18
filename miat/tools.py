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


class _draggable_lines:
	def __init__(self,axes,position,color,orientation,linestyle):
		self.orientation=orientation
		self.axes=axes
		self.canvas=axes[0].figure.canvas
		self.position=position
		if orientation=='vertical':
			self.lines=[Lines.Line2D([position,position],list(ax.get_ylim()),picker=True,pickradius=4,c=color,linestyle=linestyle) for ax in self.axes]
		if orientation=='horizontal':
			self.lines=[Lines.Line2D(list(ax.get_xlim()),[position,position],picker=True,pickradius=4,c=color,linestyle=linestyle) for ax in self.axes]
			
		self.line_artists=[self.axes[i].add_line(self.lines[i]) for i in range(len(self.axes))]
		self.canvas.draw_idle()


	def start_event(self, event):
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
			if self.orientation=='vertical':
				[line.set_xdata([event.xdata, event.xdata]) for line in self.lines]
			if self.orientation=='horizontal':
				[line.set_ydata([event.ydata, event.ydata]) for line in self.lines]
			[self.axes[i].draw_artist(self.lines[i]) for i in range(len(self.axes))]
			[self.canvas.blit(ax.bbox) for ax in self.axes]

	def releaseonclick(self, event):
		[self.canvas.blit(ax.bbox) for ax in self.axes]
		if self.orientation=='vertical':
			self.position=self.lines[0].get_xdata()[0]
		if self.orientation=='horizontal':
			self.position=self.lines[0].get_ydata()[0]

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

		self.canvas.draw_idle()

	
	def circle_picker(self,circle,mouseevent):
		if (mouseevent.xdata is None) or (mouseevent.ydata is None):
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
		self.initial_click_position=(event.xdata,event.ydata)

	def drag_circle(self,event):
		if event.xdata and event.ydata:
			self.canvas.restore_region(self.background)
			centervector=(self.position[0]-self.initial_click_position[0],self.position[1]-self.initial_click_position[1])
			newcenter=(centervector[0]+event.xdata,centervector[1]+event.ydata)
			self.center_dot.set_center(newcenter)
			self.circle.set_center(newcenter)
			self.ax.draw_artist(self.circle_artist)
			self.ax.draw_artist(self.center_dot_artist)
			self.canvas.blit(self.ax.bbox)


	
	def change_circle_size(self, event):
		if event.xdata and event.ydata:
			self.canvas.restore_region(self.background)
			newradius=((self.position[0]-event.xdata)**2+(self.position[1]-event.ydata)**2)**0.5
			self.circle.set_radius(newradius)
			self.ax.draw_artist(self.circle_artist)
			self.ax.draw_artist(self.center_dot_artist)
			self.canvas.blit(self.ax.bbox)


	def start_event(self, event):
		self.center_dot_artist.set_visible(False)
		self.circle_artist.set_visible(False)
		self.canvas.draw()
		self.background=self.canvas.copy_from_bbox(self.ax.bbox)
		self.circle_artist.set_visible(True)
		self.releaser = self.canvas.mpl_connect("button_press_event", self.releaseonclick)

		if event.button==1:
			self.canvas.draw_idle()
			self.follower = self.canvas.mpl_connect("motion_notify_event", self.change_circle_size)

		if event.button==3:
			self.click_position_finder(event)
			self.center_dot_artist.set_visible(True)
			self.canvas.draw_idle()
			self.follower = self.canvas.mpl_connect("motion_notify_event", self.drag_circle)

	def releaseonclick(self, event):
		self.radius = self.circle.get_radius()
		self.position=self.circle.get_center()
		self.center_dot_artist.set_visible(False)
		self.canvas.mpl_disconnect(self.follower)
		self.canvas.mpl_disconnect(self.releaser)
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



class _circles_tool_class:
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
		self.sid = self.canvas.mpl_connect('button_press_event', self._circle_selector)
		
	def _circle_selector(self,event):
		contains=np.array([marker.circle.contains(event)[0] for marker in self.markers])
		if (contains==True).any():
			self.markers[np.where(contains==True)[0][0]].start_event(event)
	
	def add_f(self):
		xlimits=self.ax.get_xlim()
		ylimits=self.ax.get_ylim()
		delta=min([xlimits[1]-xlimits[0],ylimits[1]-ylimits[0]])
		targeted_circle_spawning_radius=delta/5

		targeted_circle_spawning_center=((xlimits[1]-xlimits[0])/2,(ylimits[1]-ylimits[0])/2)
		selected_color=color_list[int(len(self.markers)/self.marker_group_size)]
		
		self.markers.extend((_draggable_circles(self.ax,targeted_circle_spawning_center,targeted_circle_spawning_radius,selected_color,self.linestyle) for marker in range(self.marker_group_size)))
		self.check_marker_count()
		
	def delete_f(self):
		[marker.clear() for marker in self.markers[-self.marker_group_size:]]
		del self.markers[-self.marker_group_size:]
		self.check_marker_count()
		
	def check_marker_count(self):
		if len(self.markers)/self.marker_group_size==len(color_list):
			self.add_tool.toggle(False)
		elif len(self.markers)/self.marker_group_size<len(color_list) and len(self.markers)>0:
			self.add_tool.toggle(True)
			self.remove_tool.toggle(True)
		elif len(self.markers)==0:
			self.remove_tool.toggle(False)
			
	def sort_positions(self, unsorted):
		sorted_array=np.empty([0,self.marker_group_size])
		for i in range(0,len(unsorted), self.marker_group_size):
			group=np.sort(unsorted[np.arange(i,i+self.marker_group_size)])
			sorted_array=np.vstack((sorted_array,group))
		return sorted_array
		
	def returnpositions(self):
		if self.clear:
			unsorted=np.array([marker.clear() for marker in self.markers])
			self.canvas.draw_idle()
		if not self.clear:
			unsorted=np.array([marker.position for marker in self.markers])

		return self.sort_positions(unsorted)

	
	def handle_close(self,event):
		self.canvas.stop_event_loop()


class _lines_tool_class:
	def __init__(self,canvas,marker_group_size,linestyle,axes,clear):
		self.marker_group_size=marker_group_size
		self.canvas=canvas
		self.v_markers,self.h_markers=[],[]
		self.linestyle=linestyle
		self.clear=clear
		
		if axes==None:
			self.axes=self.canvas.figure.get_axes()
		else:
			self.axes=axes
		
		self.tm = self.canvas.manager.toolmanager
		self.tb=self.canvas.manager.toolbar


		self.add_v_tool=self.tm.add_tool('add_v',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'add_{}_vbar_icon.png'.format(marker_group_size)),
					func=(lambda: self.add_f(self.v_markers,'vertical')),
					description='Add vertical lines',
					)
		
		self.remove_v_tool=self.tm.add_tool('remove_v',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'remove_{}_vbar_icon.png'.format(marker_group_size)),
					func=(lambda: self.delete_f(self.v_markers,'vertical')),
					description='Remove vertical lines',
					)
		self.add_h_tool=self.tm.add_tool('add_h',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'add_{}_hbar_icon.png'.format(marker_group_size)),
					func=(lambda: self.add_f(self.h_markers,'horizontal')),
					description='Add horizontal lines',
					)
		
		self.remove_h_tool=self.tm.add_tool('remove_h',
					toolbarbutton,
					image=str(Path(__file__).parent / "icons/" / 'remove_{}_hbar_icon.png'.format(marker_group_size)),
					func=(lambda: self.delete_f(self.h_markers,'horizontal')),
					description='Remove horizontal lines',
					)
		
		self.tb.add_tool(self.add_v_tool, "foo",0)
		self.tb.add_tool(self.remove_v_tool, "foo",1)
		self.tb.add_tool(self.add_h_tool, "foo",2)
		self.tb.add_tool(self.remove_h_tool, "foo",3)
		
		
		self.check_marker_count()
		self.sid = self.canvas.mpl_connect('button_press_event', self._line_selector)
		
	def _line_selector(self,event):
		if event.button==1:
			vertical_contains=np.array([marker.lines[0].contains(event)[0] for marker in self.v_markers])
			horizontal_contains=np.array([marker.lines[0].contains(event)[0] for marker in self.h_markers])
			if (vertical_contains==True).any():
				self.v_markers[np.where(vertical_contains==True)[0][0]].start_event(event)
			elif (horizontal_contains==True).any():
				self.h_markers[np.where(horizontal_contains==True)[0][0]].start_event(event)
		
	def add_f(self,markers_list,orientation):
		selected_color=color_list[int(len(markers_list)/self.marker_group_size)]
		if orientation=='vertical':
			ax_min,ax_max=self.canvas.figure.get_axes()[0].get_xlim()
		if orientation=="horizontal":
			ax_min,ax_max=self.canvas.figure.get_axes()[0].get_ylim()
		starting_position=ax_min+(ax_max-ax_min)/15
		markers_list.extend((_draggable_lines(self.axes,starting_position,selected_color,orientation,self.linestyle) for marker in range(self.marker_group_size)))
		self.check_marker_count()
		
	def delete_f(self,markers_list,orientation):
		[marker.clear() for marker in markers_list[-self.marker_group_size:]]
		del markers_list[-self.marker_group_size:]
		self.check_marker_count()
		
	def check_marker_count(self):
		if len(self.v_markers)/self.marker_group_size==len(color_list):
			self.add_v_tool.toggle(False)
		elif len(self.v_markers)/self.marker_group_size<len(color_list) and len(self.v_markers)>0:
			self.add_v_tool.toggle(True)
			self.remove_v_tool.toggle(True)
		elif len(self.v_markers)==0:
			self.remove_v_tool.toggle(False)
		
		if len(self.h_markers)/self.marker_group_size==len(color_list):
			self.add_h_tool.toggle(False)
		elif len(self.h_markers)/self.marker_group_size<len(color_list) and len(self.h_markers)>0:
			self.add_h_tool.toggle(True)
			self.remove_h_tool.toggle(True)
		elif len(self.h_markers)==0:
			self.remove_h_tool.toggle(False)

		self.canvas.draw_idle()

	def sort_positions(self, unsorted):
		sorted_array=np.empty([0,self.marker_group_size])
		for i in range(0,len(unsorted), self.marker_group_size):
			group=np.sort(unsorted[np.arange(i,i+self.marker_group_size)])
			sorted_array=np.vstack((sorted_array,group))
		return sorted_array
		
		
	def returnpositions(self):
		if self.clear:
			v_unsorted=np.array([marker.clear() for marker in self.v_markers])
			h_unsorted=np.array([marker.clear() for marker in self.h_markers])
			self.canvas.draw_idle()
		if not self.clear:
			v_unsorted=np.array([marker.position for marker in self.v_markers])
			h_unsorted=np.array([marker.position for marker in self.h_markers])

		return self.sort_positions(v_unsorted), self.sort_positions(h_unsorted)

	def handle_close(self,event):
		self.canvas.stop_event_loop()

def lines_tool(figure,markergroupsize:int=1,linestyle='solid',axes=None,clear=True):
	"""
	Adds four buttons on the figure that allow you to add lines on the plot. Click on the green ones to add a line group of corresponding orientation (vertical or horizontal).
	The red ones remove the last group of said orientation. 


	Parameters
	----------
	figure : plt.figure() object
		
	markergroupsize : int
		How many lines you want in a group. All the lines in said group will be the same color and their positions will be in the same
		sub-list in the returned list. The default is 1.
	linestyle : string, optional
		The default is 'solid'. This is the usual linestyle argument, anything that lines2D will accept works.
	axes : list of plt.add_subplot() objects, optional
		Wich axes you want the lines to appear in. The default is 'All of them'.
	clear : bool, optional
		Remove all lines from the figure after it is closed. Useful if you still want to do something with it, like saving it, or use more tools.
		If you want to have the markers stay, set to False. The default is True.

	Raises
	------
	draggable_markersError
		

	Returns
	-------
	numpy array
		arrays of the positions of all lines.The first one is vertical lines and the second horizontal. Each row of the array is one marker group. Each group sub-list is sorted

	"""
	if markergroupsize>3 or markergroupsize<1:
		raise draggable_markersError("Only supports marker groups sizes in the interval [1,3]")
	if plt.get_backend()!='Qt5Agg':
		raise draggable_markersError("Requires interactive backend. Switch to Qt5Agg by using plt.switch_backend('Qt5Agg'). This closes all current figures")

	lines_tool_obj=_lines_tool_class(figure.canvas,markergroupsize,linestyle,axes,clear)
	figure.canvas.mpl_connect('close_event', lines_tool_obj.handle_close)
	plt.get_current_fig_manager().window.showMaximized()
	plt.show()
	
	figure.canvas.start_event_loop()
	return lines_tool_obj.returnpositions()

def circles_tool(ax,markergroupsize:int=1,linestyle='solid',clear=True):
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

	circles_tool_obj=_circles_tool_class(ax,markergroupsize,linestyle,clear)
	plt.show()

	ax.figure.canvas.mpl_connect('close_event', circles_tool_obj.handle_close)
	
	ax.figure.canvas.start_event_loop()
	
	return circles_tool_obj.returnpositions()

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
	
	pos=lines_tool(fig,2)

	fig=plt.figure()
	
	a=np.arange(20)
	b=np.arange(20)
	ax0 = fig.add_subplot(111)
	ax0.plot(a,b)
	ax0.set_ylabel('b')
	ax0.set_title('ab')
	ax0.set_xlabel('a')
	
	rad=circles_tool(ax0,3,clear=True)
