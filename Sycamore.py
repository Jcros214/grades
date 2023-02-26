# Sycamore Module
# imports
import re
from matplotlib import pyplot as plt

import requests
from bs4 import BeautifulSoup
import datetime
# Google Sheets
# import gspread
import pandas as pd
# from oauth2client.service_account import ServiceAccountCredentials
from typing import Dict

days = pd.date_range(datetime.date(2023, 1, 5), end=datetime.date.today()).to_pydatetime().tolist()
days: list[datetime.date]


rootURL = 'https://app.sycamoreschool.com'

class Day:
	def __init__(self, date: datetime.date) -> None:
		self.date = date
		self.earned = 0
		self.possible = 0
		self.runningScore = 0
		self.runningWeight = 0

class Assignment:
	def __init__(self, name, earned, possible, date):
		self.name = name
		self.date = datetime.datetime.strptime(date, r'%m/%d/%y')
		self.earned = earned
		self.possible = possible
		self.score = self.earned/self.possible

	def __repr__(self) -> str:
		return f"{self.name} - {self.earned}/{self.possible} - {self.date.strftime(r'%m/%d/%y')}"

class Section:
	def __init__(self, data: list[Assignment], weight, name) -> None:
		self.data = data
		self.name = name
		self.earned = 0
		self.possible = 0

		self.weightByDay = []

		self.weight = weight
		self.adjWeight = weight

		self.value = self.sectionAverage()

		self.timeline = {}
		self.timeline: Dict[datetime.datetime, Day]

		for day in days:
			self.timeline[day] = Day(day)

		for assignment in self.data:
			self.timeline[assignment.date].earned += assignment.earned
			self.timeline[assignment.date].possible += assignment.possible
		

		runningEarned = 0
		runningPossible = 0

		for day in days:
			for assignment in self.data:
				if assignment.date == day:
					runningEarned += assignment.earned
					runningPossible += assignment.possible
					try:
						self.timeline[day].runningScore = runningEarned / runningPossible
					except: pass
				else:
					try:
						self.timeline[day].runningScore = runningEarned / runningPossible
					except: pass

		


	def sectionAverage(self):
		for assignment in self.data:
			self.earned += assignment.earned
			self.possible += assignment.possible
		return (self.earned/self.possible)*self.weight
	
	def sectionAverageAtDay(self, day):
		return self.timeline[day].runningScore
		# score = 0
		# for assignment in self.data:
		# 	if assignment.date <= day:
		# 		self.earned += assignment.earned
		# 		self.possible += assignment.possible
		# return (self.earned/self.possible)*self.weightAtDay(day)
	
	def weightAtDay(self, day):
		for assignment in self.data:
			if assignment.date <= day:
				return self.weight
		return 0

class Course:
	def __init__(self, classlist: list[Assignment], name='') -> None:
		self.data = classlist
		self.name =  name

		self.averageByDay = []
		self.sections = []
		self.sections: list[Section]
		self.sectionDFs = []
		self.df = pd.DataFrame(index=days)
		self.average = 0
		self.earnedWeight = 0


		self.splitIntoSections()
		self.earnedWeight = sum([section.weight for section in self.sections])
		self.get_average()

		for day in days:
			sectionAverages = []
			sectionWeights = []
			for section in self.sections:
				section: Section
				sectionAverages.append(section.sectionAverageAtDay(day))
				sectionWeights.append(section.weightAtDay(day))


			simpleAverage = sum([avg*weight for avg, weight in zip(sectionAverages, sectionWeights)])
			try:
				dailyaverage = simpleAverage/sum(sectionWeights)
			except ZeroDivisionError:
				dailyaverage = None
				
			# dailyaverage = sum([avg*weight for avg, weight in zip(sectionAverages, sectionWeights)])/sum(sectionWeights)

			pass

			self.averageByDay.append(dailyaverage)



		# for section in self.sections:
		# 	section: Section

		# 	dfData = {
		# 		'earned':   [section.timeline[day].earned                      for day in section.timeline], 
		# 		'possible': [section.timeline[day].possible                    for day in section.timeline], 
		# 		'average':  [section.timeline[day].runningScore*section.weight for day in section.timeline]
		# 	}

		# 	tmpDF = pd.DataFrame(dfData, days)
		# 	self.sectionDFs += [tmpDF]
		
		# for dfnum, frame in enumerate(self.sectionDFs):
		# 	frame: pd.DataFrame
		# 	self.df = self.df.join(frame, rsuffix=f"-{dfnum}")

		# for day in self.sections:
		# 	...


		# get total average by row
		# for index, row in self.df.iterrows():

		# 	self.averageByDay.append(sum([row.iloc[ind] for ind in range(2, len(row), 3)])/(self.earnedWeight))


	def splitIntoSections(self) -> None:
		outlist = []
		curSection = []

		sectWeights = {}

		for row in self.data:
			if type(row[-1]) is str:
				try:
					sectWeights[len(sectWeights)] = float(row[-1][:-2])/100, row[1]
				except ValueError:
					pass
		del(row)


		pass
		for assignment in self.data:
			# Check valid assignment

			# EX:
			# [nan, '08/23/22', 'Verse Memory - Jeremiah 17:9', 14.0, 14.0, 'x1', '14', '100.0', nan]

			isAssignment = True
			isSection = True

			corrTypeAssignment = [[float], [str], [str], [float], [float], [str], [str], [str], [str, float]]
			for index, val in enumerate(assignment):
				if not type(val) in corrTypeAssignment[index]:
					isAssignment = False

			corrTypeSection = [[str], [str], [str], [float], [float], [str], [str], [str], [str]]
			
			for index, val in enumerate(assignment):
				if not type(val) in corrTypeSection[index]:
					isSection = False
			
			if isAssignment and isSection:
				raise ValueError("This is a bug.")


			if isAssignment:
				assignment[3] = assignment[3] if assignment[3] > 0 else 0
				curSection.append(Assignment(assignment[2],assignment[3],assignment[4], date=assignment[1]))
			elif isSection:
				outlist += [curSection]
				curSection = []
			else:
				# print(f"Subsection header? {assignment}")
				pass

		outlist += [curSection]
		outlist.pop(0)

		for section in outlist:
			sect = sectWeights[outlist.index(section)]
			self.sections.append(Section(section, sect[0], sect[1]))

	def get_average(self):
		for section in self.sections:
			self.average += ((section.earned/section.possible))*(section.weight)
		self.average = (self.average/self.earnedWeight)


class User:
	def __init__(self, creds, debug = False):
		self.debug = debug

		self.username = creds.username
		self.password = creds.password
		self.payload = {
			'MIME Type': 'application/x-www-form-urlencoded',
			'loginheight': 558,
			'entered_schid': 2947,
			'entered_login': self.username,
			'entered_password': self.password,
			'entered_language': 1
	    }

		self.classes = []
		self.courses = []

		self.getGrades()

		
		# if(self.useSheets):
		# 	for userClass in self.classes:
		# 		self.googleSheet(userClass)

	# get classIDs and classNames, and store as Class in self.classes
	def getClasses(self, r: str):
		if self.debug:
			print('Finding classes....')

		# ex: 
		# <a onclick="doclass(389179)">Bible 9/10: Boys A</a>

		section_break_str = '<tr class="se-bg-gray se-bold">'

		_r = r.split(section_break_str)[1]


		pattern = r'<a onclick=[\'\"]doclass\(([\d]{6})\)[\"\']>([A-Za-z0-9: \/]+)<\/a>'

		matches = re.finditer(pattern, _r)

		output = []


		for match in matches:
			output.append({'id':int(match.group(1)), 'name':str(match.group(2))})
			
			if self.debug:
				print(str(match.group(2)))
		if (len(output) == 0):
			raise UserWarning("No classes found. Check your username and password.")
		
		return output

	def getGrades(self):
		with requests.session() as s:
			s.post(f"{rootURL}/index.php", data=self.payload)
			r = s.get(f"{rootURL}/mystudent.php?task=grades")

			table = BeautifulSoup(r.content, 'html.parser').find('table')

			classes = self.getClasses(str(table))

			outclasses = []

			for Class in classes:
				r = s.get(f"{rootURL}/mystudent.php?task=viewdetail&sid=1266875&subjectid=0&classid={Class['id']}&quarter=1")

				table = BeautifulSoup(r.content, 'html.parser').find('table').find_next('table')

				outputTable = pd.read_html(r.content)[2]
				
				outputTable[3] = pd.to_numeric(outputTable[3], errors='coerce')
				outputTable[4] = pd.to_numeric(outputTable[4], errors='coerce')

				#outputTable_isValidAssignment = outputTable[outputTable[0]!="E" and outputTable[0]!="A" and outputTable[0]!="D"]

				outputTable = outputTable[outputTable[0].ne("E")]
				outputTable = outputTable[outputTable[0].ne("D")]
				outputTable = outputTable[outputTable[0].ne("A")]

				listout = outputTable.values.tolist()

				listout = listout[1:] #remove header row
				
				outclasses += [Course(listout, Class['name'])]
		self.courses = outclasses

	def getAssignments(self, course: str, date: datetime.date):
		assignments = []

		for _course in self.courses:
			if _course.name == course:
				course = _course
				break

		if type(course) == str:
			raise ValueError("Course not found.")

		course: Course
		section: Section
		assignment: Assignment

		for section in course.sections:
			for assignment in section.data:
				if assignment.date.year == date.year and assignment.date.month == date.month and assignment.date.day == date.day:
					assignments += [assignment]
		return assignments
		

	def showPlot(self, daysBeforeToday = 0):
		fig, ax = plt.subplots()

		if daysBeforeToday > len(days):
			daysBeforeToday = len(days)-1


		ymin = 1
		course: Course
		min_date = None
		max_date = None
		courses = self.courses
		for course in self.courses:
			if daysBeforeToday != 0:
				# Create new list of non-zero values
				averagelist = [avg for avg in course.averageByDay[len(course.averageByDay)-1-daysBeforeToday:] if avg != 0]
				daylist = [date for date, avg in zip(days[len(days)-1-daysBeforeToday:], course.averageByDay[len(course.averageByDay)-1-daysBeforeToday:]) if avg != 0]
				pass
			else:
				averagelist = [avg for avg in course.averageByDay if avg != 0]
				daylist = [date for date, avg in zip(days, course.averageByDay) if avg != 0]
			
			ymin = min(ymin, min([a for a in averagelist if a != None]))
				
			if daylist:
				min_date = min(daylist) if min_date is None else min(min_date, min(daylist))
				max_date = max(daylist) if max_date is None else max(max_date, max(daylist))
			ax.plot(daylist, averagelist, '-o', label=course.name, picker=True, pickradius=5)

		def onclick(event):
			global user

			course = event.artist._label
			from matplotlib.dates import num2date
			date = num2date(event.mouseevent.xdata)

			assignments = user.getAssignments(course, date)

			print(f"\n\nAssignments for {course} on {date}:")
			for assignment in assignments:
				print(assignment)
			print("\n\n")

			# print(user.getAssignments(course, date))


		fig.canvas.mpl_connect('pick_event', onclick)

		plt.title("Grades over Semester")
		plt.xlabel('Date')
		plt.ylim(ymin-.03, 1.03)

		tickNums =  [.595,.625,.675,.695,.725,.775,.795,.825,.875,.895,.925,.975,1 ]
		tickNames = ['D-','D' ,'D+','C-','C' ,'C+','B-','B' ,'B+','A-','A' ,'A+','']
		plt.yticks(ticks=tickNums, labels=tickNames)
		plt.yticks(tickNums, tickNames)
		
		plt.hlines(tickNums, days[0], days[-1], '0')
		plt.ylabel('Grade')
		plt.legend(loc='lower left')
		# plt.show()


		"TODO: get agragate average"
			# totalAvgList = [0] * len(daylist)

			# for course in self.courses:
			# 	for ind, day in enumerate(averagelist):
			# 		try:
			# 			totalAvgList[ind] += day/len(self.courses)
			# 		except:
			# 			print(f"ind: <{ind}>, day: <{day}>")

			# plt.plot_date(daylist, totalAvgList, '-o', label='Average')
		
		import base64
		from io import BytesIO

		buf = BytesIO()
		fig.set_figheight(8)
		fig.set_figwidth(15)

		fig.savefig(buf, format="png")
		# Embed the result in the html output.
		data = base64.b64encode(buf.getbuffer()).decode("ascii")

		import os

		os.rename('plot.png', f'oldPlots/plot{ len(os.listdir("oldPlots")) }.png.bak')

		with open('plot.png', 'w') as f:
			f.write(data)


		return f"<img style='display: block; margin-left: auto; margin-right: auto' src='data:image/png;base64,{data}'/>"

	def printGrades(self):
		print('\n')
		for x in self.courses:
			# print(f'{x.className:<25}: {x.grades.letter} {(x.grades.average*100):.2f}%')
			print(f'{x.name:<25}: {Data.pctToLetter(x.average)} {(x.average*100):.2f}%')
			
		print('\n')

class Data:
	def pctToLetter(numeric: float):
			numeric = float(numeric)
			if (numeric < 0):
				raise ValueError()
			numeric = round(numeric, 2)

			# Max rounded numeric that is still that grade
			grades = {
				'F ': .59,
				'D-': 0.62,
				'D ': 0.66,
				'D+': 0.69,
				'C-': 0.72,
				'C ': 0.76,
				'C+': 0.79,
				'B-': 0.82,
				'B ': 0.86,
				'B+': 0.89,
				'A-': 0.92,
				'A ': 0.96,
				'A+': 1000,
			}
			
			prvValue = -1
			for key, value in grades.items():
				if numeric <= value:
					return key
			return 'A+'


if __name__ == "__main__":
	import sys
	from cred import Creds
	if len(sys.argv) == 3:
		user = User(Creds(sys.argv[1], sys.argv[2]))
	else:
		try: # for running locally
			import credentials
			user = User(credentials.users['jon'])
		except ImportError:	
			try:
				# EX: 
				# user_credentials = Creds("username", "password")
				# user = User(user_credentials)

				user_credentials = Creds("username", "password")
				user = User(user_credentials)


			except:
				raise ValueError("You probably forgot to add your credentials. Look at the instructions in README.md")
	


	user.printGrades()
	user.showPlot(daysBeforeToday=60)