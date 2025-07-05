from datetime import datetime, timedelta


def format_date(date):
	return date.strftime('%Y-%m-%d')


def get_this_week_dates():
	today = datetime.now().date()
	days_since_monday = today.weekday()
	monday_this_week = today - timedelta(days=days_since_monday)
	
	# Calculate the last day of the week (Sunday)
	sunday_this_week = monday_this_week + timedelta(days=6)
	
	monday_this_week_formatted = format_date(monday_this_week)
	sunday_this_week_formatted = format_date(sunday_this_week)
	
	return monday_this_week_formatted, sunday_this_week_formatted


def get_this_month_dates():
	today = datetime.now().date()
	first_day_of_month = today.replace(day=1)
	last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

	first_day_formatted = format_date(first_day_of_month)
	last_day_formatted = format_date(last_day_of_month)

	return first_day_formatted, last_day_formatted

