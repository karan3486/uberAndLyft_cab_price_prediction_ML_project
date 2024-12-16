import pandas as pd
class PreprocessingPipeline:
    def __init__(self,cab_data,weather_data):
        self.cab_data = cab_data
        self.weather_data = weather_data
    
    def preprocess(self):
        # Preprocess the data
        self.weather_data.rename(columns={'location': 'source'},inplace=True)
        self.weather_data.fillna(0,inplace=True) 
        self.cab_data.dropna(inplace= True)
        self.cab_data['datetime'] = pd.to_datetime(self.cab_data['time_stamp'], unit='ms')
        self.weather_data['datetime'] = pd.to_datetime(self.weather_data['time_stamp'], unit='s')

        self.ride_data_combined = pd.merge_asof(
                                    self.cab_data.sort_values('datetime'),
                                    self.weather_data.sort_values('datetime'),
                                    on='datetime',
                                    by='source',
                                    direction='backward'
                                )
        drop_columns = ['id','product_id','time_stamp_x','time_stamp_y','destination','source']
        self.final_data = self.ride_data_combined.drop(drop_columns,axis=1)

        self.final_data['month'] = self.final_data['datetime'].dt.month         # Extract month
        self.final_data['day_of_week'] = self.final_data['datetime'].dt.dayofweek + 1  # Extract day of week (0=Monday, 6=Sunday)
        self.final_data['hour'] = self.final_data['datetime'].dt.hour           # Extract hour
        self.final_data['minute'] = self.final_data['datetime'].dt.minute 
        self.final_data.drop(['datetime'],axis=1,inplace=True)

        self.data_uber = self.final_data.loc[self.final_data['cab_type']=='Uber'].drop(['cab_type'],axis=1)
        self.data_lyft = self.final_data.loc[self.final_data['cab_type']=='Lyft'].drop(['cab_type'],axis=1)
        self.data_surge = self.data_lyft[['temp', 'clouds','pressure', 'rain', 'humidity', 'wind','surge_multiplier']]
