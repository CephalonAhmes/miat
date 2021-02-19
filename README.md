miat-Manual Image Analysis Tools


Are you trying to measure some parameters on a figure using Python without using any curve-fitting tools? Whatever the reason for this, the process that comes with this method is generally very slow. Create the figure, save it, open it using a specific tool such as ImageJ, manually add the marker shapes you want to add, write down all the values, and then transfer those back to your Python script, so that you can finish your analysis, perhaps with a new figure made with the parameters you just measured on a large sample of figures.



I know how excrutiatingly slow and error-prone this procedure can be, as I had to live through it multiple times over my academic career. That's also why I made this library based on matplotlib.


What miat does is provide a few basic tools you might need, but with the added convenience of being available directly in your Python IDE in a blocking manner, meaning that it suspends the process and waits for you to complete your measurments before resuming. The advantage of this is that you can create a figure, measure some parameter, and use those values immediately after (you could save them, or append them to a list and do some additional calculations, for example).


Interested? The library is available on PyPI, so `pip install miat` will allow you to use it.


From there, importing miat.tools will allow you to use miat. There aren't many of them for now, but it's stil a work-in-progress. The tools currently in place will allow you to add horizontal and vertcal bars to a figure or image, which is useful for measuring deltas, among other things. The second tool allows you to add circular markers to a figure. One usecase I can think of would be to measure circular diffraction patterns. This library also works for imshow figures.


I have added some documentation [here](https://github.com/CephalonAhmes/miat/tree/main/documentation)
