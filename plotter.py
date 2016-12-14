""" matman <github.com/fiedlr/matman> """

import numpy as np
import matplotlib.pyplot as plt

class Plotter:
	""" Gives results a graphical interpretation """
	def __init__(self, analyser):
		self.__analyser = analyser
		# Plt config
		plt.grid(True)

	def __autolabel(self, rects, ax, labels):
		""" http://matplotlib.org/examples/api/barchart_demo.html """
		key = 0
		for rect in rects:
			height = rect.get_height()
			ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
		    	labels[key], ha='center', va='bottom')
			key+=1

	def plot_error_time(self):
		""" Make diff plots according to the data """
		plt.figure()

		# Graph according to data
		difflist = self.__analyser.time_conversion()
		plt.scatter(*zip(*difflist))

		# Save graph
		plt.title('Avg. error to avg. time')
		plt.xlabel('time')
		plt.ylabel('error')
		plt.savefig('graph1.png')

	def plot_easiness(self):
		""" Make diff plots according to the data """
		plt.figure()
	
		difflist = self.__analyser.difficulty_list()[-10:]
		x_val = tuple([x[0] for x in difflist])
		y_val = tuple([y[1] for y in difflist])
		labels = tuple([self.__analyser.get_items()[item[0]]['question'] for item in difflist])

		ind = np.arange(len(x_val))
		width = 0.35

		fig, ax = plt.subplots()
		rects = ax.bar(ind, y_val, width, color='r')

		# Assign questions
		self.__autolabel(rects, ax, labels)

		ax.set_xticks(ind + width)
		ax.set_xticklabels(x_val)
		plt.title('Top 10 easiest questions')
		plt.xlabel('item id')
		plt.ylabel('difficulty')
		plt.savefig('graph2.png')


	def plot_difficulty(self):
		""" Make diff plots according to the data """
		plt.figure()

		difflist = self.__analyser.difficulty_list()[:10]
		x_val = tuple([x[0] for x in difflist])
		y_val = tuple([y[1] for y in difflist])
		labels = tuple([self.__analyser.get_items()[item[0]]['question'] for item in difflist])

		ind = np.arange(len(x_val))
		width = 0.35

		fig, ax = plt.subplots()
		rects = ax.bar(ind, y_val, width, color='r')

		# Assign questions
		self.__autolabel(rects, ax, labels)

		ax.set_xticks(ind + width)
		ax.set_xticklabels(x_val)
		plt.title('Top 10 hardest questions')
		plt.xlabel('item id')
		plt.ylabel('difficulty')
		plt.savefig('graph3.png')

	def plot_difficulty_levels(self):
		""" Make plots according to data """
		plt.figure()
		skillstat = self.__analyser.skillstat()
		x_val = []; y_val = []; labels = []
		width = 0.35
		for key, skill in skillstat.items():
			for lvl in skill:
				x_val.append(self.__analyser.get_skills()[key][lvl[0]]['label'])
				if key != 2076:
					y_val.append(lvl[1])
				else:
					y_val.append(math.log(lvl[1]))
			ind = np.arange(len(x_val))
			fig, ax = plt.subplots()
			ax.scatter(ind, tuple(y_val))
			ax.plot(ind, tuple(y_val))
			ax.set_xticks(ind)
			ax.set_xticklabels(x_val)
			# Saves
			plt.title('Difficulty to level rise')
			plt.xlabel('skill lvl')
			plt.ylabel('difficulty')
			plt.savefig('graph'+key+'.png')
			# Clear the canvas for the next graph
			x_val = []; y_val = []; labels = [];
			plt.clf()

	def plot_visualization_vs_difficulty(self):
		fig = plt.figure()
		
		visuallist = self.__analyser.visualstat()
		x_val = tuple([x for x in visuallist.keys()])
		y_val = tuple([y[1] for y in visuallist.values()])

		ind = np.arange(len(x_val))
		width = 0.35

		ax = fig.add_subplot(111)
		rects = ax.bar(ind, y_val, width, color='r')

		ax.set_xticks(ind + width)
		ax.set_xticklabels(x_val)
		ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=45)
		plt.title('')
		plt.xlabel('visualization')
		plt.ylabel('difficulty')
		plt.tight_layout()
		plt.savefig('graph6.png')
		
	def run(self):
		""" Plot all the results """
		self.plot_error_time()
		self.plot_easiness()
		self.plot_difficulty()
		self.plot_difficulty_levels()
		self.plot_visualization_vs_difficulty()