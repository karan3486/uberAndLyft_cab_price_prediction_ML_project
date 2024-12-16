from flask import Flask, request, jsonify,render_template
import joblib
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from utility.utils import TimeAndWeather,PricePrediction,ModelTraining
import plotly.graph_objs as go
import plotly.io as pio
class LabelEncoderPipeline(LabelEncoder):
    def fit(self, X, y=None):
        super().fit(X)
        return self

    def transform(self, X):
        # Ensure the output is 2D
        return super().transform(X).reshape(-1, 1)

    def fit_transform(self, X, y=None):
        # Ensure the output is 2D
        return super().fit_transform(X).reshape(-1, 1)
from prediction.prediction import LyftPrediction,UberPrediction
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))

# model_path = "xgboost_ride_price_model.pkl"
surge_path = os.path.join(os.getcwd(),'models\\best_model_surge.pkl')
encoder_path = os.path.join(os.getcwd(),'models\\label_encoder.pkl')
lyft_model_path = os.path.join(os.getcwd(),'models\\best_model_lyft.pkl')
uber_model_path = os.path.join(os.getcwd(),'models\\best_model_uber.pkl')
long_lati = '37.48730837087998, -121.92509100041184'

cabData = os.path.join(os.getcwd(),'data/cab_rides.csv')
weatherData = os.path.join(os.getcwd(),'data/weather.csv')

try:
    lyft_model = LyftPrediction(surge_path,encoder_path,lyft_model_path)
    uber_model = UberPrediction(uber_model_path)
except FileNotFoundError:
        raise FileNotFoundError("The model file was not saved due to the earlier issue with XGBoost.")


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/train", methods=['GET'])
def train():
    #load the data
    train_model = ModelTraining(cabData=cabData,weatherData=weatherData,surge_path=surge_path,encoder_path=encoder_path,lyft_model_path=lyft_model_path,uber_model_path=uber_model)
    train_model.train()
    return render_template("about.html")

@app.route("/book")
def book():
    return render_template("book.html")

@app.route('/predict', methods=['POST'])
def predict_price():
    try:
        input_data = request.get_json()
        if not input_data:
            return jsonify({"error": "Invalid input, JSON data is required"}), 400
        
        distance = input_data.get('distance')
        lon_lat =  long_lati if input_data.get('lon_lat') == '' else input_data.get('lon_lat')
        price_predictions = PricePrediction(lyft_model,uber_model)
        temp, clouds, pressure, rain, humidity, wind = TimeAndWeather.getWeatherData(lon_lat)
        day_of_week, hour, minute = TimeAndWeather.getTime()
        data = {'distance':distance,'day_of_week':day_of_week,'hour':hour,'minute':minute, 'temp': temp, 'clouds': clouds, 'pressure': pressure,'rain': rain,'humidity':humidity,'wind': wind}

        predict_price = []
        # temp, clouds, pressure, rain, humidity, wind = getWeatherData(input_data.get('lon_lat'))
        # day_of_week, hour, minute = getTime()
        # distance = input_data.get('distance')
        # data = {'distance':distance,'day_of_week':day_of_week,'hour':hour,'minute':minute, 'temp': temp, 'clouds': clouds, 'pressure': pressure,'rain': rain,'humidity':humidity,'wind': wind}
        # lyft_price_dict = getlyft_price(data)
        # uber_price_dict = getUber_price(data)
        predict_price.append(price_predictions.getlyft_price(data))
        predict_price.append(price_predictions.getUber_price(data))
        return jsonify(predict_price), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/metricReport')
def metric_report():
    # Convert Plotly figures to JSON for embedding in HTML
    roc_auc_plot = pio.read_json("static/plots_metrics/roc_auc_plot.json")
    conf_matrix_plot = pio.read_json("static/plots_metrics/conf_matrix_plot.json")
    metrics_plot = pio.read_json("static/plots_metrics/metrics_plot.json")
    fig_imp = pio.read_json("static/plots_metrics/fig_imp.json")
    
    # Pass data to template as JSON strings
    return render_template('visualization.html', 
                           roc_auc_plot=roc_auc_plot.to_json(),
                           conf_matrix_plot=conf_matrix_plot.to_json(),
                           metrics_plot=metrics_plot.to_json(),
                           fig_imp=fig_imp.to_json())



if __name__ == "__main__":
    app.run(debug=True)
