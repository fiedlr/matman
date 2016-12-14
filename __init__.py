""" matman <github.com/fiedlr/matman> """

from main import Analyser
from plotter import Plotter

def run(skillfile, itemfile, datafile):

	""" Run a game with the chosen config - accessible through terminal """
	analysis = Analyser(skillfile, itemfile, datafile)

	print("Welcome to MATMAN, an analyser of the MatMat.cz dataset.")
	print("Extracting the data...")

	analysis.build()
	analysis.run()

	count_entries = analysis.get_num_entries()
	validity = 1 - round((count_entries['invalid'] + count_entries['fake']) / count_entries['all'], 2)
	print("Number of all entries:", count_entries['all'], "| Invalid entries:", count_entries['invalid'], "| Fake entries:", count_entries['fake'], "(Valid samples make up:", validity*100, "%)")

	print("Proceeding with the analysis...")

	students = analysis.analyse_students()

	print("Average response time:", round(students[0], 2), "| Average success rate:", round(students[1], 2), "| Average error:", round(students[2], 2))
	print("Success rate standard deviation:", round(students[3], 2))
	print("Number of students:", len(analysis.get_students()))
	print("Estimated number of fakers:", students[4], "| Under average perf.:", students[5], "| Over average perf.:", students[6])

	items_diff = analysis.analyse_items()
	skills_diff = analysis.analyse_skills()

	# Plot the results
	plotter = Plotter(analysis)
	plotter.run()

	print("Done. You can see the results in the project's root folder.")

# Run the analysis with these files
run("skills.csv", "items.csv", "answers.csv")
