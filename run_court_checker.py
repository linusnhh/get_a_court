import datetime

from court import TennisChecker


def check_courts():
    start_date = datetime.date(2025, 7, 7)
    end_date = datetime.date(2025, 7, 7)
    start_time = 20
    end_time = 21
    minimum_booking_time = 60  # NOTE: By default it's one hour
    venues = ['Burgess Park']

    date_range = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    time_range = list(range(start_time, end_time + 1))
    court_checker = TennisChecker(target_date_range=date_range, target_time_range=time_range, venue_filter=venues, minimum_booking_time=minimum_booking_time)
    available_courts = court_checker.create_venue_coverage()
    user_output = court_checker.availability_filter(available_courts)
    for target_date, court_details in user_output.items():
        print(target_date)
        for venue_name, court_df in court_details.items():
            print(venue_name)
            print(court_df)


if __name__ == '__main__':
    check_courts()


