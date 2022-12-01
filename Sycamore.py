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


days = pd.date_range(datetime.date(2022, 8, 15), end=datetime.date.today()).to_pydatetime().tolist()
days: list[datetime.date]


rootURL = 'https://app.sycamoreschool.com'

class Day:
	def __init__(self, date: datetime.date) -> None:
		self.date = date
		self.earned = 0
		self.possible = 0
		self.runningScore = 0

class Assignment:
	def __init__(self, name, earned, possible, date):
		self.name = name
		self.date = datetime.datetime.strptime(date, r'%m/%d/%y')
		self.earned = earned
		self.possible = possible
		self.score = self.earned/self.possible

class Section:
	def __init__(self, data: list[Assignment], weight, name) -> None:
		self.data = data
		self.name = name
		self.earned = 0
		self.possible = 0

		self.weight = weight
		self.adjWeight = weight

		self.value = self.sectionAverage()

		self.timeline = {}
		for day in days:
			self.timeline[day] = Day(day)

		for assignment in self.data:
			self.timeline[assignment.date].earned += assignment.earned
			self.timeline[assignment.date].possible += assignment.possible

			

	def sectionAverage(self):
		earned, possible = 0,0
		for assignment in self.data:
			self.earned += assignment.earned
			self.possible += assignment.possible
			score = self.earned/self.possible
			pass
		return score*self.weight

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
		



		for section in self.sections:
			section: Section
			section.timeline

			runningEarned = 0
			runningPossible = 0

			for day in days:
				for assignment in section.data:
					if assignment.date == day:
						runningEarned += assignment.earned
						runningPossible += assignment.possible
						try:
							section.timeline[day].runningScore = runningEarned/runningPossible
						except: pass
					else:
						try:
							section.timeline[day].runningScore = runningEarned/runningPossible
						except: pass

			


			tmpDF = pd.DataFrame({'earned': [section.timeline[day].earned for day in section.timeline], 'possible': [section.timeline[day].possible for day in section.timeline], 'average':[section.timeline[day].runningScore*section.weight for day in section.timeline]}, days)
			self.sectionDFs += [tmpDF]
		
		for dfnum, frame in enumerate(self.sectionDFs):
			frame: pd.DataFrame
			self.df = self.df.join(frame, rsuffix=f"-{dfnum}")


		# get total average by row
		for index, row in self.df.iterrows():
			self.averageByDay.append(sum([row.iloc[ind] for ind in range(2, len(row), 3)])/(self.earnedWeight))
			# if self.averageByDay[-1] > 1:
			# 	raise ValueError("What's Wrong??")

		# self.average = sum([sect.value for sect in self.sections]) + (1- sum([sect.weight for sect in self.sections]))

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
		pass
		for section in self.sections:
			self.average += ((section.earned/section.possible))*(section.weight)
		self.average = (self.average/self.earnedWeight)


class User:
	def __init__(self, creds, sheets=False, debug = False):
		self.debug = debug
		self.useSheets = sheets


		# if (type(picker) is int):
		# 	if (picker < len(credintalList)):
		# 		username = credintalList[picker][0]
		# 		password = credintalList[picker][1]
		# 	else:
		# 		raise ValueError("picker is too large (out of range)")
		# elif (type(picker) is list and len(picker) == 2):
		# 	username = picker[0]
		# 	password = picker[1]
		# else:
		# 	raise ValueError("picker is not valid")

		username = creds.username
		password = creds.password

		self.username = username
		self.password = password
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

		
		if(self.useSheets):
			for userClass in self.classes:
				self.googleSheet(userClass)

	# get classIDs and classNames, and store as Class in self.classes
	def getClasses(self, r: str):
		if self.debug:
			print('Finding classes....')

		# ex: 
		# <a onclick="doclass(389179)">Bible 9/10: Boys A</a>

		pattern = r'<a onclick=[\'\"]doclass\(([\d]{6})\)[\"\']>([A-Za-z0-9: \/]+)<\/a>'

		matches = re.finditer(pattern, r)

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

	def showPlot(self, daysBeforeToday = 0):
		course: Course	
		for course in self.courses:
			if daysBeforeToday != 0:
				daylist = days[len(days)-1-daysBeforeToday:]
				averagelist = course.averageByDay[len(course.averageByDay)-1-daysBeforeToday:]
			else:
				daylist = days
				averagelist = course.averageByDay

			plt.plot_date(daylist, averagelist, '-o', label=course.name)

		"TODO: get agragate average"
			# totalAvgList = [0] * len(daylist)

			# for course in self.courses:
			# 	for ind, day in enumerate(averagelist):
			# 		try:
			# 			totalAvgList[ind] += day/len(self.courses)
			# 		except:
			# 			print(f"ind: <{ind}>, day: <{day}>")

			# plt.plot_date(daylist, totalAvgList, '-o', label='Average')
		
		plt.title("Grades over Semester")
		plt.xlabel('Date')
		# plt.ylim(.8, 1)

		tickNums = [.795,.825,.875,.895,.925,.975]
		tickNames = ['B-','B','B+','A-','A','A+']
		# plt.yticks(ticks=tickNums, labels=tickNames)
		plt.hlines(tickNums, daylist[0], daylist[-1], '0')
		plt.ylabel('Grade')
		plt.legend(loc='lower left')
		plt.show()

		import base64
		from io import BytesIO

		buf = BytesIO()
		plt.gcf().set_figheight(8)
		plt.gcf().set_figwidth(15)

		plt.savefig(buf, format="png")
		# Embed the result in the html output.
		data = base64.b64encode(buf.getbuffer()).decode("ascii")
		return f"<img style='display: block; margin-left: auto; margin-right: auto' src='data:image/png;base64,{data}'/>"




	# Depreciated
	# def googleSheet(self, Class):
	# 	# define the scope
	# 	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

	# 	# add credentials to the account
	# 	creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)

	# 	self.sheetName = f'22-23: cro'

	# 	# authorize the clientsheet 
	# 	client = gspread.authorize(creds)
	# 	self.Wbook = client.open(self.sheetName)
	# 	outputTable = Class.grades.df.fillna("")

	# 	outputTable['Class.grades.average'] = Class.grades.average

	# 	sheetName = Class.className.replace(":", "")
	# 	try:
	# 		worksheet = self.Wbook.worksheet(sheetName)
	# 	except:
	# 		self.Wbook.add_worksheet(sheetName, len(outputTable), len(outputTable.columns))
	# 		print(f'Sheet Not found. Creating new sheet: {sheetName}')
	# 		worksheet = self.Wbook.worksheet(sheetName)

	# 		# add_worksheet(title=classIds[x][1].replace(":", " "), rows=70, cols=12)
	# 		# worksheet.clear()

	# 		worksheet.update(outputTable.values.tolist())

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
	try:
		from credentials import Creds, users
	except:
		raise ValueError("You probably forgot to add your credentials. Look at the instructions in README.md")
	user = User(users['jon'], sheets = False)

	user.printGrades()
	user.showPlot(daysBeforeToday=50)