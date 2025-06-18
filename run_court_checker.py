import datetime

from court import TennisChecker


def check_courts():
    start_date = datetime.date(2025, 6, 26)
    end_date = datetime.date(2025, 6, 27)
    start_time = 17
    end_time = 21
    date_range = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    time_range = list(range(start_time, end_time + 1))
    court_checker = TennisChecker(target_date_range=date_range, target_time_range=time_range)
    court_checker.create_venue_coverage()


if __name__ == '__main__':
    check_courts()


