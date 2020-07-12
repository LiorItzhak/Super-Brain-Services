from datetime import datetime
from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
from datetime import datetime, timedelta
import dateutil.parser
import pandas as pd
import numpy as np
import math


from pandas.api.indexers import BaseIndexer
# TODO create separate micro-service
# baseurl = 'http://127.0.0.1:5000/activity'
baseurl = 'http://34.71.217.0:5000/event'
# baseurl = 'http://crud:5000/event'


class TimelineApi(Resource):

    def get(self, user_id):
        date = request.args.get('date', None)
        if date is None:
            from_timestamp = datetime.now().date()
        else:
            from_timestamp = dateutil.parser.parse(date).date()
        to_timestamp = (from_timestamp + timedelta(days=1))

        location_df = self.get_location_events(user_id, from_timestamp, to_timestamp)
        if location_df is None:
            return []
        person_df = self.get_person_activities(user_id, from_timestamp, to_timestamp)

        location_df.loc[:, 'person_list'] = location_df.apply(
            lambda x: self.get_person_id_vector(person_df, x['from_timestamp'], x['to_timestamp']), axis=1)

        df = location_df

        # marshaling data
        df.update(df.select_dtypes('datetime').stack().dt.strftime("%Y-%m-%dT%H:%M:%S.%f").unstack())
        return json.loads(df.reset_index().to_json(orient='records'))

    def get_person_id_vector(self, person_df, from_timestamp, to_timestamp):
        person_df = person_df[(person_df.timestamp >= from_timestamp) & (person_df.timestamp < to_timestamp)]
        person_df.person_id.unique()
        return person_df.person_id.unique()


    def get_person_activities(self, user_id, from_timestamp, to_timestamp):
        response = requests.get(f'{baseurl}', {'page': 0, 'size': 9999999, 'type': 'Person', 'user_id': user_id,
                                               'from_timestamp': from_timestamp.isoformat(),
                                               'to_timestamp': to_timestamp.isoformat()}).json()

        person_activities = [r for r in response if {'person_id'} <= r['data'].keys()]
        person_activities = [ [a["user_id"], dateutil.parser.parse(a["timestamp"]), a["data"].get("person_id")] for a in person_activities]

        df = pd.DataFrame(person_activities, columns=['user_id', 'timestamp', "person_id"])
        return df

    def get_person_events(self, user_id, from_timestamp, to_timestamp):
        # TODO - intervals
        df = self.get_person_activities(user_id, from_timestamp, to_timestamp)
        dff = df.groupby('person_id').agg({
            'user_id': ['first', 'count'],
            'timestamp': ['min', 'max'],
        })
        dff.columns = dff.columns.map('_'.join)
        dff = dff.rename(columns={
            'user_id_first': 'user_id',
            'user_id_count': 'count',
            'timestamp_max': 'to_timestamp',
            'timestamp_min': 'from_timestamp'
        })
        return dff

    def get_location_events(self, user_id, from_timestamp, to_timestamp):
        geolocator = Nominatim(user_agent=__name__)

        # fetching and unmarshaling data
        response = requests.get(f'{baseurl}', {'page': 0, 'size': 9999999, 'type': 'Location',
                                               'user_id': user_id,
                                               'from_timestamp': from_timestamp.isoformat(),
                                               'to_timestamp': to_timestamp.isoformat()
                                               }).json()

        activities = [r for r in response if {'lat', 'lng'} <= r['data'].keys()]
        activities = [[a["user_id"], dateutil.parser.parse(a["timestamp"]), a["data"]["lat"], a["data"]["lng"]]
                      for a in activities]
        if len(activities) < 3: return None

        # create a dataframe
        df = pd.DataFrame(activities, columns=['user_id', 'timestamp', "lat", "lng"])
        df = df.sort_values('timestamp')
        df['index'] = df['timestamp']
        df = df.set_index('index')

        window = '20 min'
        df.loc[:, 'mean_lat'] = df.lat.rolling(window=window).mean()
        df.loc[:, 'mean_lng'] = df.lng.rolling(window=window).mean()

        df.loc[:, 'prv_timestamp'] = df.timestamp.shift()
        df.loc[:, 'prv_lat'] = df.lat.shift()
        df.loc[:, 'prv_lng'] = df.lng.shift()
        df.loc[:, 'prv_mean_lat'] = df.mean_lat.shift()
        df.loc[:, 'prv_mean_lng'] = df.mean_lng.shift()
        df = df[1:]

        df.loc[:, 'distance_prv_mean_m'] = df.apply(
            lambda x: geodesic((x['lat'], x['lng']), (x['prv_mean_lat'], x['prv_mean_lng'])).m, axis=1)
        df.loc[:, 'deltatime_s'] = (
                (df.loc[:, 'timestamp'] - df.loc[:, 'prv_timestamp']) / np.timedelta64(1, 's')).abs()
        df.loc[:, 'distance_m'] = df.apply(lambda x: geodesic((x['lat'], x['lng']), (x['prv_lat'], x['prv_lng'])).m,
                                           axis=1)

        df.loc[:, 'is_standing'] = df.distance_prv_mean_m < 200
        df.loc[:, 'change_status'] = df['is_standing'] - df['is_standing'].shift()
        df = df[1:]
        df.loc[:, 'id'] = (df.change_status != 0).groupby(level=0, sort=False).sum().cumsum()

        dff = df.groupby('id', sort=False)[
            ['user_id', 'timestamp', 'lat', 'lng', 'is_standing', 'distance_m', 'deltatime_s', 'prv_timestamp']].agg({
            'timestamp': ['count', 'max'],
            'prv_timestamp': 'min',
            'is_standing': 'last',
            'lat': ['first', 'last', 'mean'],
            'lng': ['mean', 'first', 'last'],
            'distance_m': 'sum',
            'deltatime_s': 'sum',
            'user_id': 'first'
        })
        dff.columns = dff.columns.map('_'.join)
        dff = dff.reset_index()
        dff = dff.rename(columns={
            "is_standing_last": "is_standing", 'user_id_first': 'user_id',
            "prv_timestamp_min": "from_timestamp",
            "timestamp_max": "to_timestamp",
            "lat_first": "from_lat",
            "lat_last": "to_lat",
            "lng_first": "from_lng",
            "lng_last": "to_lng",
            "deltatime_s_sum": "duration_sec",
            "timestamp_count": "count"
        })
        dff.loc[:, 'speed_mps'] = dff.distance_m_sum / dff.duration_sec
        dff.loc[:, 'distance_from_to'] = dff.apply(
            lambda x: geodesic((x['from_lat'], x['from_lng']), (x['to_lat'], x['to_lng'])).m, axis=1)

        # remove moving records less then 150 meter and not enough data (count less then 3 or less then 10 min)
        dff = dff.loc[(dff.distance_from_to > 150) | ((dff.loc[:, 'count'] >= 3) & (dff.duration_sec > 10 * 60)) | (
            dff.is_standing)]

        # merge 2 consecutive standing records that close enough
        dff.loc[:, 'prv_lat_mean'] = dff.lat_mean.shift()
        dff.loc[:, 'prv_lng_mean'] = dff.lng_mean.shift()
        dff.loc[0, 'prv_lat_mean'] = dff.loc[0, 'lat_mean']
        dff.loc[0, 'prv_lng_mean'] = dff.loc[0, 'lng_mean']
        dff.loc[:, 'distance_from_prv_mean'] = dff.apply(
            lambda x: geodesic((x['lat_mean'], x['lng_mean']), (x['prv_lat_mean'], x['prv_lng_mean'])).m, axis=1)
        dff.loc[:, 'change_status'] = (dff['is_standing'] - dff['is_standing'].shift()).abs()
        dff.loc[0, 'change_status'] = 0
        dff.loc[(dff.is_standing == True) & (dff.distance_from_prv_mean > 200), 'change_status'] = 1
        dff.loc[:, 'id'] = (dff.change_status != 0).groupby(level=0, sort=False).sum().cumsum()

        dff = dff.groupby('id', sort=False)[[
            'count', 'is_standing', 'user_id',
            'from_timestamp', 'to_timestamp',
            'lat_mean', 'lng_mean',
            'from_lat', 'from_lng',
            'to_lat', 'to_lng',
            'distance_m_sum', 'duration_sec']].agg({
            'count': 'sum', 'is_standing': 'first', 'user_id': 'first',
            'from_timestamp': "min", 'to_timestamp': "max",
            'lat_mean': 'mean', 'lng_mean': 'mean',
            'from_lat': 'first', 'from_lng': 'first',
            'to_lat': 'last', 'to_lng': 'last',
            'distance_m_sum': 'sum', 'duration_sec': 'sum'

        })
        # calculate address for standing records (using reverse geocoder)
        dff.loc[:, 'address'] = dff.apply(
            lambda x: geolocator.reverse((x['lat_mean'], x['lng_mean'])).address if x['is_standing'] is True else None,
            axis=1)
        return dff
