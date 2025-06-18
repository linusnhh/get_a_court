import requests
import pandas as pd

# from pandas_helper import pandas_show_all
import datetime

# pandas_show_all()
# available_courts = {}

# NOTE: This is
nh_name = 'Stratford'
print(f'The venue is {nh_name}.')
current_time = datetime.datetime.now()
# NOTE: logic dependent on whether you can book or not
end_date = current_time + datetime.timedelta(weeks=2)
# end_date = current_time + datetime.timedelta(days=2)  # for testing purpose
start_date_str = current_time.strftime('%Y-%m-%d')
current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%d')

# NOTE: available_courts
available_courts = {}
booking_date_range = [(current_time + datetime.timedelta(days=i)).date() for i in range((end_date - current_time).days
                                                                                        + 1)]

response = requests.get(
    f"https://stratford.newhamparkstennis.org.uk/v0/VenueBooking/stratford_newhamparkstennis_org_uk/GetVenueSessions?resourceID=&startDate={start_date_str}&endDate={end_date_str}&roleId=&_=1750070208037",
    verify=False)
booking_data = response.json()
timezone = booking_data['TimeZone']
earliest_start = int(booking_data['EarliestStartTime'] / 60)
latest_end = int((booking_data['LatestEndTime'] - 60) / 60)

for booking_date in booking_date_range:
    time_index = pd.date_range(start=f"{booking_date} {earliest_start}:00", end=f"{booking_date} {latest_end}:00",
                               freq='h')
    df = pd.DataFrame({'Time': time_index})
    df = df.set_index('Time')
    available_courts[booking_date.strftime('%Y-%m-%d')] = df


for court_details in booking_data['Resources']:
    court_name = court_details['Name']
    for booking_date_summary in court_details['Days']:
        booking_date = booking_date_summary['Date'][:10]
        for court_session in booking_date_summary['Sessions']:
            # print(court_session)  # NOTE: court session is an individual court booking session

            session_start = int(court_session['StartTime'] / 60)
            session_end = int(court_session['EndTime'] / 60)
            if court_session['Capacity'] == 1:
                df = available_courts[booking_date]
                for session_time in range(session_start, session_end):
                    if court_name not in df.columns:
                        df[court_name] = 0
                    df.loc[f"{booking_date} {session_time:02d}:00:00", court_name] += 1

for every_day, df in available_courts.items():
    print(every_day)
    print(df)

