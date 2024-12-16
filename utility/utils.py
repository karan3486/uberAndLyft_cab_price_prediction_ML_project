import requests
import pandas as pd
from training.training import SurgeChargeTraining, LyftTraining, UberTraining
from preprocessing.preprocessing import PreprocessingPipeline

cab_types = ['Uber','Lyft']
lyft_types = {'Share':'Shared','Lyft':'Lyft','LyftXL':'Lyft XL','BlackSUV':'Lux Black XL',}
uber_types = {'Share':'UberPool','UberX':'UberX','UberXL':'UberXL','BlackSUV':'Black SUV'}

class TimeAndWeather:
    @staticmethod
    def getTime():
        current_datetime = pd.Timestamp.now()

        # Extract day_of_week, hour, and minute
        day_of_week = current_datetime.dayofweek+1  # Monday=0, Sunday=6
        hour = current_datetime.hour
        minute = current_datetime.minute

        return (day_of_week, hour, minute)
    
    @staticmethod
    def getWeatherData(lon_lat):
        api_key = '6f7bd8748a1943759e555019241612'
        url = f"https://api.weatherapi.com/v1/current.json?q={lon_lat}&key={api_key}"

        response = requests.get(url)
        weather_data = response.json()
        print(response.json())
        temp = weather_data["current"]["temp_f"]
        clouds = weather_data["current"]["cloud"]
        pressure = weather_data["current"]["pressure_mb"]
        rain = weather_data["current"]["precip_in"]
        humidity = weather_data["current"]["humidity"]
        wind = weather_data["current"]["wind_mph"]

        # Display the extracted values
        return temp, clouds, pressure, rain, humidity, wind

class PricePrediction:
    def __init__(self, lyft_model,uber_model):
          self.lyft_model = lyft_model
          self.uber_model = uber_model

    def getlyft_price(self,data):
        try:
            input_df = pd.DataFrame([data])
            price_dict = {}
            for ltype,type in lyft_types.items():
                input_df['name']= type
                # Make a prediction
                prediction = self.lyft_model.predict_price(input_df)
                predicted_price = prediction[0]
                price_dict[ltype] = float(predicted_price)

            price_dict['cab_type']= 'Lyft'
            return price_dict
        except Exception as e:
            print(f"Error: {e}")
            raise Exception("Error parsing price prediction data from file: {}".format( repr(e) ))
    
    def getUber_price(self,data):
        try:
            input_df = pd.DataFrame([data])
            price_dict = {}
            for ltype,type in uber_types.items():
                input_df['name']= type
                # Make a prediction
                prediction = self.uber_model.predict_price(input_df)
                predicted_price = prediction[0]
                price_dict[ltype] = float(predicted_price)

            price_dict['cab_type']= 'Uber'
            return price_dict
        except Exception as e:
            print(f"Error: {e}")
            raise Exception("Error parsing price prediction data from file: {}".format( repr(e) ))

class ModelTraining:
    def __init__(self, **kwargs):
        self.cabData = kwargs.pop('cabData', None)
        self.weatherData = kwargs.pop('weatherData', None)
        self.surge_path = kwargs.pop('surge_path', None)
        self.encoder_path = kwargs.pop('encoder_path', None)
        self.lyft_model_path = kwargs.pop('lyft_model_path', None)
        self.uber_model_path = kwargs.pop('uber_model_path', None)

    def train(self):
        ride_data = pd.read_csv(self.cabData)
        weather_data = pd.read_csv(self.weatherData)
        preprocessPipe = PreprocessingPipeline(ride_data, weather_data)
        preprocessPipe.preprocess()
        
        surge_trainer = SurgeChargeTraining(preprocessPipe.data_surge,self.surge_path,self.encoder_path)
        surge_trainer.train_model()
        surge_trainer.evaluate_model()

        lyft_trainer = LyftTraining(preprocessPipe.data_lyft,self.lyft_model_path)
        lyft_trainer.train_model()
        lyft_trainer.evaluate_model()

        uber_trainer = UberTraining(preprocessPipe.data_uber,self.uber_model_path)
        uber_trainer.train_model()
        uber_trainer.evaluate_model()