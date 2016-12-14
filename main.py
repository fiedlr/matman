""" matman <github.com/fiedlr/matman> """

import csv
import sys
import math
import codecs
import statistics

def update_avg(avg, nvals, new_val):
	""" Updates an already existing average """
	return (avg + (new_val / nvals)) * (nvals / (nvals + 1)) if nvals else new_val

def open_csv(filename):
	""" Opens a csv file in utf8 and returns a csvr object """
	file = codecs.open(filename, encoding='utf8')
	# Decode the file
	reader = csv.reader(file)
	# Skip the header
	next(reader)
	# Return the reader object
	return reader

class Analyser:
	""" The scanner class """

	# STATSAMPLE = {'nanswers': 0, 'ncorrect': 0, 'avgresp': 0, 'avgerr': 0}

	def __init__(self, skillfile, itemfile, datafile):
		# Too many attributes

		# Save the filenames
		self.__skillfile = skillfile
		self.__itemfile = itemfile
		self.__datafile = datafile
		# Entries counter
		self.__count_entries = {'all': 0, 'fake': 0, 'invalid': 0}
		# Create the analysis structures
		self.__items = {}
		self.__students = {}
		self.__skills = {
			# Counting
			'1870': {
				'1871': {'label': 'numbers_leq_10', 'count': 0, 'avgdiff': 0}, 
				'1872': {'label': 'numbers_leq_20', 'count': 0, 'avgdiff': 0}
			}, 
			# Addition
			'1893': {
				'1894': {'label': 'addition_leq_10', 'count': 0, 'avgdiff': 0},
				'1895': {'label': 'addition_leq_20', 'count': 0, 'avgdiff': 0},
				'1896': {'label': 'addition_leq_100', 'count': 0, 'avgdiff': 0}
			},
			# Subtraction
			'2018': {
				'2019': {'label': 'subtraction_leq_10', 'count': 0, 'avgdiff': 0},
				'2020': {'label': 'subtraction_leq_20', 'count': 0, 'avgdiff': 0},
				# arbitrary
				'2021': {'label': 'subtraction_leq_100', 'count': 0, 'avgdiff': 0}
			},
			# Multiplication
			'2076': {
				'2077': {'label': 'multiplication_small', 'count': 0, 'avgdiff': 0},
				'2133': {'label': 'multiplication_big', 'count': 0, 'avgdiff': 0}
			},
			# Division
			'2234': {
				'2235': {'label': 'division1', 'count': 0, 'avgdiff': 0}
			}
		}
		# Stat containers
		self.__success_sd = 0 # success standard deviation
		self.__est = {'fakers': 0, 'underavg': 0, 'overavg': 0} # estimates
		self.__savg = {'success': 0, 'resp': 0, 'err': 0} # student general avgs
		self.__skillstat = {}
		self.__visualstat = {'written_question': [0, 0], 'object_counting': [0, 0], 'object_counting_with_numbers': [0, 0], 'object_selection_answer': [0, 0], 'number_line_answer': [0, 0], 'multiplication_visualization_field': [0, 0], 'division_visualization_baskets': [0, 0]} # stats about the visual types
		self.__time_conversion = [] # avg. error to avg. time
		self.__difficulty_list = []
		# Set a higher limit for the csv reader
		csv.field_size_limit(sys.maxsize)

	def build(self):
		""" Create a temp db for storing item defs """
		csvr = open_csv(self.__itemfile)
		# Process the output
		for entry in csvr:
			item = str(entry[0]); visual = str(entry[3]); skill = str(entry[4]); skills = (str(entry[5]), str(entry[6]), str(entry[7])); question = str(entry[1])
			self.__items[item] = {'nanswers': 0, 'ncorrect': 0, 'avgresp': 0, 'medresp': 0, 'avgerr': 0, 'resps': [], 'visual': visual, 'skill': skill, 'skills': skills, 'question': question}

	def run(self):
		""" Runs through the dataset """
		# Open the file in UTF8 to avoid errors
		csvr = open_csv(self.__datafile)
		# Process the output
		for entry in csvr:
			# Increase the counters
			self.__count_entries['all'] += 1
			# Filter out irrelevant answers
			try:
				answer = int(entry[6])
			except ValueError:
				self.__count_entries['invalid'] += 1
				continue
		    # Any answer greater than 500 is surely a scam
			if answer > 500:
				self.__count_entries['fake'] += 1
				continue
		    # Basic conversions
			item = str(entry[2]); student = str(entry[3]); time = float(entry[4]); correct = int(entry[5]); expected = int(entry[7]); 
			
			# Calculate error
			dev = abs(answer - expected)

			# Recalculate item averages
			self.__items[item]['avgresp'] = (
				update_avg(self.__items[item]['avgresp'], self.__items[item]['nanswers'], time)
			)
			self.__items[item]['avgerr'] = (
				update_avg(self.__items[item]['avgerr'], self.__items[item]['nanswers'], dev)
			)
			# Store for median calculation
			self.__items[item]['resps'].append(time)
			# Items counter
			self.__items[item]['ncorrect'] += correct
			self.__items[item]['nanswers'] += 1

			# Recalculate student averages
			if student not in self.__students:
				# Add student to "database"
				self.__students[student] = {'nanswers': 0, 'ncorrect': 0, 'avgresp': 0, 'avgerr': 0}
			else:
				self.__students[student]['avgresp'] = (
					update_avg(self.__students[student]['avgresp'], self.__students[student]['nanswers'], time)
				)
				self.__students[student]['avgerr'] = (
					update_avg(self.__students[student]['avgerr'], self.__students[student]['nanswers'], dev)
				)
			# Students counter
			self.__students[student]['ncorrect'] += correct
			self.__students[student]['nanswers'] += 1

	def __guess_faker(self, avgresp, avgerr):
		""" Estimate faker status against the avgs """
		return avgresp < self.__savg['resp'] and avgerr > self.__savg['err']

	def __guess_underavg(self, avgresp, avgerr, srate):
		""" Estimates underavg status against the avgs """
		return avgresp < self.__savg['resp'] and avgerr > self.__savg['err'] and srate < self.__savg['success']

	def __guess_overavg(self, avgresp, avgerr, srate):
		""" Estimates overavg status against the avgs """
		return avgresp > self.__savg['resp'] and avgerr < self.__savg['err'] and srate > self.__savg['success']

	def analyse_students(self):
		""" Runs through the results and makes the appropriate averages """
		nstudents = len(self.__students)
		for s in self.__students.values():
			srate = float(s['ncorrect']) / s['nanswers']
			#if s['avgresp'] <= 2000:
			self.__time_conversion.append((s['avgresp'], s['avgerr']))
			self.__savg['success'] += srate
			self.__savg['resp'] += s['avgresp']
			self.__savg['err'] += s['avgerr']
		# Calculate averages
		self.__savg['success'] /= nstudents
		self.__savg['resp'] /= nstudents
		self.__savg['err'] /= nstudents
		# Calculate success standard deviation
		standard_dev = 0
		# Estimate the possible number of fakers, overavgs and underavgs
		for s in self.__students.values():
			srate = float(s['ncorrect']) / s['nanswers']
			standard_dev += (srate - self.__savg['success']) ** 2
			self.__est['fakers'] += int(self.__guess_faker(s['avgresp'], s['avgerr']))
			self.__est['overavg'] += int(self.__guess_overavg(s['avgresp'], s['avgerr'], srate))
			self.__est['underavg'] += int(self.__guess_underavg(s['avgresp'], s['avgerr'], srate))
		self.__success_sd = math.sqrt(standard_dev / nstudents) 
		return [self.__savg['resp'], self.__savg['success'], self.__savg['err'], self.__success_sd, self.__est['fakers'], self.__est['underavg'], self.__est['overavg']]

	def analyse_items(self):
		""" Go through items, categorize them and analyse them accordingly to their difficulty """
		for key, i in self.__items.items():
			# Calculate the median
			i['medresp'] = statistics.median(i['resps'])
			# Calculate difficulty
			difficulty = round((i['avgerr'] * i['medresp']) / (i['ncorrect'] / i['nanswers']), 2)
			i['difficulty'] = difficulty
			# Output for analysis
			self.__difficulty_list.append((key, difficulty))
			# Group difficulties to skills
			skill = str(i['skills'][0]); skillcat = str(i['skills'][1])
			# Gaps
			if skill == skillcat == 2018 or len(skillcat) == 0:
				skillcat = '2021'
			self.__skills[skill][skillcat]['avgdiff'] = (
				update_avg(self.__skills[skill][skillcat]['avgdiff'], self.__skills[skill][skillcat]['count'], difficulty)
			)
			self.__skills[skill][skillcat]['count'] += 1
			# Group itemstats to visuals
			self.__visualstat[i['visual']][0] += 1
			self.__visualstat[i['visual']][1] += i['difficulty']
		# Calculate averages for visualizations
		for visualavg in self.__visualstat.values():
			visualavg[1] /= visualavg[0]
		self.__difficulty_list = sorted(self.__difficulty_list, key=lambda item: item[1], reverse=True)
		return self.__difficulty_list

	def analyse_skills(self):
		""" Sort difficulties in the skill levels for analysis """
		skillstat = {}
		for key, skill in self.__skills.items():
			if key not in skillstat:
				skillstat[key] = []
			# Output for plotting
			for i, level in skill.items():
				skillstat[key].append((i, level['avgdiff']))
			# Sort in an ascending order
			skillstat[key] = sorted(skillstat[key], key=lambda item: item[1])
		# Save to state
		self.__skillstat = skillstat
		return skillstat

	def get_skills(self):
		""" Get the skills processed dataset """
		return self.__skills

	def get_items(self):
		""" Get the items processed dataset """
		return self.__items

	def get_students(self):
		""" Get the students processed dataset """
		return self.__students

	def get_num_entries(self):
		""" Puts the results in a meaningful data object for Plotter """
		return self.__count_entries

	def time_conversion(self):
		""" Return avg time to avg error conversion """
		return self.__time_conversion

	def difficulty_list(self):
		""" Get the items sorted by their difficulty """
		return self.__difficulty_list

	def visualstat(self):
		""" Visualization statistics """
		return self.__visualstat

	def skillstat(self):
		""" Get the skill statistics """
		return self.__skillstat
