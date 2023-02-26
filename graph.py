from matplotlib import pyplot as plt
import pandas as pd
import datetime

days = pd.date_range(datetime.date(2022, 8, 15), end=datetime.date.today()).to_pydatetime().tolist()



def showPlot(courses, daysBeforeToday = 0):

	for course in courses:
		if daysBeforeToday != 0:
			daylist = days[len(days)-1-daysBeforeToday:]
			averagelist = course.averageByDay[len(course.averageByDay)-1-daysBeforeToday:]
		else:
			daylist = days
			averagelist = course.averageByDay

		axe.plot(daylist, averagelist, '-o', label=course.name)

	plt.title("Grades over Semester")
	plt.xlabel('Date')
	# plt.ylim(.8, 1)

	tickNums = [.795,.825,.875,.895,.925,.975]

	plt.hlines(tickNums, daylist[0], daylist[-1], '0')
	plt.ylabel('Grade')
	plt.legend(loc='lower left')

	import base64
	from io import BytesIO

	buf = BytesIO()
	fig.set_figheight(8)
	fig.set_figwidth(15)

	fig.savefig(buf, format="png")
	# Embed the result in the html output.
	data = base64.b64encode(buf.getbuffer()).decode("ascii")
	return f"<img style='display: block; margin-left: auto; margin-right: auto' src='data:image/png;base64,{data}'/>"

