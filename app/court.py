import logging
import datetime
import requests
import logging
import pandas as pd
import numpy as np
import urllib3

from app.config import clubs_info
from app.logger import setup_logger

logger = setup_logger(name="Get A Court", log_path=r"./logs/court_booking.log", level=logging.INFO)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger.warning(f"Insecure Warning Suppressed.")

class TennisChecker:
    def __init__(
            self, target_date_range, target_time_range, venue_filter, minimum_booking_time
    ):
        self.target_date_range = target_date_range
        self.target_time_range = target_time_range
        self.venue_filter = venue_filter
        self.court_availability = {}

    def queries_summary(self):
        print('The queries_summary')
        target_dates = '|'.join([td.strftime('%e %b') for td in self.target_date_range])
        target_courts = '|'.join(self.venue_filter)
        print(f'🗓️🎾📍️Gathering Court Data for {target_dates} from {self.target_time_range[0]} to '
              f'{self.target_time_range[-1]} at {target_courts}')

    def create_venue_coverage(self):
        current_time = datetime.datetime.now()
        start_date_str = self.target_date_range[0].strftime("%Y-%m-%d")
        end_date_str = self.target_date_range[-1].strftime("%Y-%m-%d")

        for club, club_details in clubs_info.items():
            for venue_name, venue_details in club_details.items():
                if venue_name in self.venue_filter:
                    court_url = venue_details["court_url"]
                    base_url = venue_details["base_url"]
                    role_id = venue_details["role_id"]

                    response = requests.get(
                        f"https://{court_url}.{base_url}/v0/VenueBooking/{court_url}_{base_url.replace('.', '_')}/GetVenueSessions?resourceID=&startDate={start_date_str}&endDate={end_date_str}&roleId={role_id}",
                        verify=False,
                    )

                    booking_data = response.json()
                    logger.info(f"Raw Booking data for {venue_name}: {booking_data}")

                    timezone = booking_data["TimeZone"]
                    earliest_start = int(booking_data["EarliestStartTime"] / 60)
                    minimum_interval = booking_data["MinimumInterval"]
                    latest_end = (booking_data["LatestEndTime"] - minimum_interval) / 60

                    for booking_date in self.target_date_range:
                        date_str = booking_date.strftime("%Y-%m-%d")
                        time_index = pd.date_range(
                            start=f"{date_str} {earliest_start}:00",
                            end=f"{date_str} {latest_end}:00",
                            freq=f"{str(minimum_interval)}min",
                        )
                        df = pd.DataFrame({"Time": time_index}).set_index("Time")

                        if date_str not in self.court_availability:
                            self.court_availability[date_str] = {}

                        self.court_availability[date_str][
                            venue_name
                        ] = df.copy()  # IMPORTANT: .copy() avoids mutating same df

                    # Fill in court availability
                    for court_details in booking_data["Resources"]:
                        court_no = court_details["Name"]
                        for booking_date_summary in court_details["Days"]:
                            booking_date_str = booking_date_summary["Date"][:10]
                            for court_session in booking_date_summary["Sessions"]:
                                session_start = court_session["StartTime"] / 60
                                session_end = court_session["EndTime"] / 60
                                if court_session["Capacity"] == 1:
                                    df = self.court_availability[booking_date_str][
                                        venue_name
                                    ]


                                    for session_time in np.arange(
                                            session_start,
                                            session_end,
                                            minimum_interval / 60,
                                    ):
                                        session_hh, session_mm = int(session_time), int(
                                            str(session_time).split(".")[1]
                                        )
                                        if session_mm == 5:
                                            session_mm = "30"
                                        else:
                                            session_mm = "00"
                                        if court_no not in df.columns:
                                            df[court_no] = 0
                                        df.loc[
                                            f"{booking_date_str} {session_hh:02d}:{session_mm}:00",
                                            court_no,
                                        ] += 1

        return self.court_availability

    def availability_filter(self, court_availability):
        requested_availability = {}

        for target_date in self.target_date_range:
            target_index_time_range = pd.to_datetime([
                f"{target_date} {target_time:02d}:00:00"
                for target_time in self.target_time_range
            ])
            all_courts = court_availability[target_date.strftime("%Y-%m-%d")]
            filtered_courts = {
                k: v[v.index.isin(target_index_time_range)]
                for k, v in all_courts.items()
                if k in self.venue_filter
            }
            filtered_courts = {
                k: v.loc[~(v == 0).all(axis=1), ~(v == 0).all(axis=0)]
                for k, v in filtered_courts.items()
            }
            filtered_courts = {k: v for k, v in filtered_courts.items() if not v.empty}
            requested_availability[target_date] = filtered_courts
        return requested_availability
