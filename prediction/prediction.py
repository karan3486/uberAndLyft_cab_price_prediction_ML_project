import joblib
from sklearn.preprocessing import LabelEncoder

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

class LyftPrediction:
    
    def __init__(self,surge_path,encoder_path,lyft_path):
            try:
                self.best_model_surge_loaded = joblib.load(surge_path)
                self.label_encoder_load = joblib.load(encoder_path)
                self.best_model_lyft_loaded = joblib.load(lyft_path)
    
            except Exception as e:
                    print(f"Error during initialization: {e}")
                    raise Exception("Initialization failed in TrainingLyft.")

     
    def predict_price(self,data):
            try:
                # Load the model and the encoder
                surge_predicted = self.best_model_surge_loaded.predict(data)
                surge_decoded =  float(self.label_encoder_load.inverse_transform(surge_predicted))
                data['surge_multiplier'] = surge_decoded
                price_lyft = self.best_model_lyft_loaded.predict(data)
                # Return the predictions and the labels
                return price_lyft
        
            except Exception as e:
                    print(f"Error during prediction: {e}")
                    raise Exception("Prediction process failed in TrainingLyft.")
    
    def save_predictions(self, predictions, filename):
            try:
                with open(filename, 'w') as f:
                    for item in predictions:
                        f.write("%s\n" % item)

            except Exception as e:
                print(f"Error during saving predictions: {e}")

class UberPrediction:
    
    def __init__(self,uber_path):
            try:
                self.best_model_uber_loaded = joblib.load(uber_path)
    
            except Exception as e:
                    print(f"Error during initialization: {e}")
                    raise Exception("Initialization failed in UberPrediction.")

     
    def predict_price(self,data):
            try:
                # Load the model and the encoder
                price_uber = self.best_model_uber_loaded.predict(data)
                # Return the predictions and the labels
                return price_uber
        
            except Exception as e:
                    print(f"Error during prediction: {e}")
                    raise Exception("Prediction process failed in Uber.")