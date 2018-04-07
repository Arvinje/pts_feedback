import time

def startDateIsBeforeToday(date):
  dayToday = int(time.strftime('%d'))
  monthToday = int(time.strftime('%m'))
  yearToday = int(time.strftime('%Y'))

  if (yearToday < date.year):
    return True
  if ((yearToday == date.year) & (monthToday < date.month)):
    return True
  if ((monthToday == date.month) & (dayToday < date.day)):
    return True
  return False