import logging
import datetime
import requests

import pandas as pd
from config import clubs_info


class TennisChecker:
    def __init__(self, target_date_range, target_time_range, venue_filter=[]):
        self.target_date_range = target_date_range
        self.target_time_range = target_time_range
        self.venue_filter = venue_filter

    def create_venue_coverage(self):
        current_time = datetime.datetime.now()
        start_date_str = self.target_date_range[0].strftime("%Y-%m-%d")
        end_date_str = self.target_date_range[-1].strftime("%Y-%m-%d")
        available_courts = {}
        for club, club_details in clubs_info.items():
            print(club)
            court_url = club_details["court_url"]
            base_url = club_details["base_url"]
            role_id = club_details["role_id"]

            response = requests.get(
                f"https://{court_url}.{base_url}/v0/VenueBooking/{court_url}_{base_url.replace('.', '_')}/GetVenueSessions?resourceID=&startDate={start_date_str}&endDate={end_date_str}&roleId={role_id}",
                verify=False,
            )

            booking_data = response.json()
            timezone = booking_data['TimeZone']
            earliest_start = int(booking_data['EarliestStartTime'] / 60)
            latest_end = int((booking_data['LatestEndTime'] - 60) / 60)

            for booking_date in self.target_date_range:
                time_index = pd.date_range(start=f"{booking_date} {earliest_start}:00",
                                           end=f"{booking_date} {latest_end}:00",
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
