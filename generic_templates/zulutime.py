from dateutil.parser import isoparse
import datetime
import pytz
import os

class ZuluTime:
    def __init__(self, isodate: str = None):
        """
        Returns the time in Zulu standard for the given input string.   If no input string is given
        then if the ZULUTIME environment variable exists that time will be returned.   If neither is 
        found then the current time is returned.
        """
        if not isodate is None:
            isodate = str(isodate)
            if ' ' in isodate:
                isodate = isodate.replace(' ','T')
            if '+00:00' in isodate:
                isodate = isodate.replace('+00:00', '')
            #print(f"isodate is '{isodate}'")
            d = isoparse(isodate)
            if ZuluTime.isnaive(d):
                d = pytz.utc.localize(d)
            self._datetime = d
        else:
            if 'ZULUTIME' in os.environ:
                d = isoparse(os.environ['ZULUTIME'])
                if ZuluTime.isnaive(d): d = pytz.utc.localize(d)
                self._datetime = d

            else:
                now = datetime.datetime.utcnow()
                self._datetime = pytz.utc.localize(now)

    @classmethod
    def now(self):
        """
        Returns the current time in Zulu standard
        """
        return ZuluTime(datetime.datetime.utcnow())

    @staticmethod
    def isnaive(dt : datetime.datetime):
        return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None

    def __sub__(self, ts):
        return self._datetime - ts._datetime

    def __eq__(self, ts):
        return self._datetime == ts._datetime

    def __lt__(self, ts):
        return self._datetime < ts._datetime

    def __le__(self, ts):
        return self._datetime <= ts._datetime

    def __gt__(self, ts):
        return self._datetime > ts._datetime

    def __ge__(self, ts):
        return self._datetime >= ts._datetime

    def __add__(self, offset_sec):
        return self._datetime + datetime.timedelta(seconds=offset_sec)

    def __repr__(self):
        return self._datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    def date(self):
        return self._datetime.strftime("%Y-%m-%d")

    def time(self):
        return self._datetime.strftime("%H:%M:%SZ")

    def met_ts(self):
        return self._datetime.strftime("%Y%m%d_%H%M%S")

    def expo_ts(self):
        return self._datetime.strftime("%Y%m%d")

    def timestamptz(self):
        """format compatible with Redshift TIMESTAMPTZ"""
        return self._datetime.strftime("%Y-%m-%d %H:%M:%S+00")


if __name__ == "__main__":
    print("Zulutime is ", ZuluTime())
