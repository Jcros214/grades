from Sycamore import User
try:
	from credentials import users, Creds
except ModuleNotFoundError:
	pass

# credentials = Creds('USERNAME', 'PASSWORD')

try:
	# credentials = Creds('USERNAME', 'PASSWORD')
	credentials = users['jon']
except:
	raise ValueError("You probably forgot to add your credentials. Look at the instructions in README.md")


user = User(credentials)
user.printGrades()
user.showPlot(daysBeforeToday=60)
