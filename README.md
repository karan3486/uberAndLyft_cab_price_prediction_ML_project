
---

# Ride Price Prediction System

This project is a **Flask-based web application** that predicts ride prices for Lyft and Uber based on input data such as distance, weather conditions, and time. It integrates machine learning models for price prediction and provides interactive visualizations for metric reports.
![image](https://github.com/user-attachments/assets/d9ab910e-ebcb-4a37-a3b6-ba695c44f77d)

![image](https://github.com/user-attachments/assets/24c4eff9-d067-462c-ac62-3bcb311512c3)


---

## Features

- **Price Prediction**: Predicts ride prices for Lyft and Uber.
- **Machine Learning Training**: Trains models using cab ride and weather data.
- **Interactive Visualizations**: Displays metrics like ROC-AUC, confusion matrix, and feature importance.
- **Customizable Templates**: Includes pre-built HTML templates for various routes.
- **REST API Support**: Accepts JSON input for predictions.

---


---

## Prerequisites

1. **Python 3.7+**
2. **Virtual Environment** (optional but recommended)
3. Installed dependencies (see below).

---

## Model:
XGBoost Regressor and 
XGBoost Classifier

##Prediction Pipeline:
![predictgraph](https://github.com/user-attachments/assets/543ea36a-5f07-4b9c-b1ec-c026351d553e)

## Installation


1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/ride-price-prediction.git
   cd ride-price-prediction
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Prepare the Project
- Ensure your pre-trained models (`best_model_surge.pkl`, `label_encoder.pkl`, etc.) and data files (`cab_rides.csv`, `weather.csv`) are in the appropriate directories (`models/` and `data/`).

### 2. Run the Application
Start the Flask server:

```bash
python app.py
```

The application will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## API Endpoints

### **1. Home Page**
- **Route**: `/`
- **Method**: GET
- **Description**: Displays the home page.

### **2. About Page**
- **Route**: `/about`
- **Method**: GET
- **Description**: Provides details about the project.

### **3. Train Models**
- **Route**: `/train`
- **Method**: GET
- **Description**: Trains the models using the provided data.

### **4. Predict Price**
- **Route**: `/predict`
- **Method**: POST
- **Description**: Predicts ride prices for Lyft and Uber.

 

### **5. Metric Report**
- **Route**: `/metricReport`
- **Method**: GET
- **Description**: Displays visualizations of model metrics.

---

## Files and Models

- **Data**: 
  - `cab_rides.csv` (Ride data)
  - `weather.csv` (Weather data)
  
- **Models**:
  - `best_model_surge.pkl` (Lyft surge prediction model)
  - `label_encoder.pkl` (Label encoder for categorical data)
  - `best_model_lyft.pkl` (Lyft price prediction model)
  - `best_model_uber.pkl` (Uber price prediction model)

---

## Dependencies

Add the following to your `requirements.txt`:

```
Flask==2.2.2
pandas==1.5.3
plotly==5.6.0
joblib==1.2.0
scikit-learn==1.2.1
```

Install them using:

```bash
pip install -r requirements.txt
```

---

## Customization

1. Modify templates in the `templates/` directory to customize the UI.
2. Update the data in the `data/` folder for training new models.
3. Extend functionality by adding routes in `app.py`.

---

## Future Enhancements

- Add user authentication.
- Implement additional ride services (e.g., Ola, Grab).
- Enhance UI/UX with more interactive features.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---
