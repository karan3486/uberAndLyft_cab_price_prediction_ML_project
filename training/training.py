from sklearn.preprocessing import LabelEncoder
import pandas as pd
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score

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

class SurgeChargeTraining:
    def __init__(self, data_surge,model_path,encoder_path):
        self.model_path = model_path
        self.encoder_path = encoder_path
        self.data_surge = data_surge
        self.features = ['temp', 'clouds', 'pressure', 'rain', 'humidity', 'wind']
        self.target = 'surge_multiplier'
        self.data_surge[self.target] = data_surge[self.target].astype('category')
        label_encoder = LabelEncoder()
        self.data_surge[self.target] = label_encoder.fit_transform(data_surge[self.target])

        # Convert 'surge_multiplier' to a categorical type before applying label encoding
        
        joblib.dump(label_encoder,encoder_path)
    
    def train_model(self):
        # Split the data into train+validation and test sets
        X = self.data_surge[self.features]
        y = self.data_surge[self.target]

        X_train_val, self.X_test, y_train_val, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Further split train+validation into train and validation sets
        X_train, self.X_val, y_train, self.y_val = train_test_split(X_train_val, y_train_val, test_size=0.25, random_state=42, stratify=y_train_val)

        # Step 2: Define preprocessing and pipeline
        # Scaling numerical features
        preprocessor = ColumnTransformer(
            transformers=[
                ('scale', StandardScaler(), self.features)
            ]
        )

        # Create a pipeline with preprocessor and XGBoost classifier
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42))
        ])

        # Step 3: Define parameter grid for GridSearchCV
        param_grid = {
            'classifier__n_estimators': [50, 100],
            'classifier__max_depth': [3, 5, 7],
            'classifier__learning_rate': [0.01, 0.1],
            'classifier__subsample': [0.8, 1.0]
        }

        # Grid search with cross-validation
        grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='accuracy', verbose=2, n_jobs=-1)
        grid_search.fit(X_train, y_train)

        best_model_surge = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        joblib.dump(best_model_surge, self.model_path)

    def evaluate_model(self):
        best_model_surge_loaded = joblib.load(self.model_path)
        label_encoder_load = joblib.load('label_encoder.pkl')

        y_val_pred = best_model_surge_loaded.predict(self.X_val)
        val_accuracy = accuracy_score(self.y_val, y_val_pred)

        # Test accuracy
        y_test_pred = best_model_surge_loaded.predict(self.X_test)
        test_accuracy = accuracy_score(self.y_test, y_test_pred)

        # Classification report on the test set
        test_report = classification_report(self.y_test, y_test_pred, target_names=label_encoder_load.classes_.astype(str))

        test_precision = precision_score(self.y_test, y_test_pred, average='weighted')  # Precision
        test_recall = recall_score(self.y_test, y_test_pred, average='weighted')  # Recall
        test_f1 = f1_score(self.y_test, y_test_pred, average='weighted') 

        # Step 5: Display results
        print("*******************************Surge Charge Model Evaluation****************************")
        print("Best Parameters:", self.best_params)
        print("Validation Accuracy:", val_accuracy)
        print("Test Accuracy:", test_accuracy)
        print("Test Precision:", test_precision)
        print("Test Recall:", test_recall)
        print("Test F1-Score:", test_f1)
        print("\nClassification Report on Test Set:\n", test_report)


class LyftTraining:
    def __init__(self, dataset,model_path):
        self.data_lyft = dataset
        self.model_path = model_path
        self.data_lyft['surge_multiplier'] = self.data_lyft['surge_multiplier'].astype('category')

        # Features and target
        # X = data_lyft[['distance', 'surge_multiplier', 'name', 'temp', 'clouds', 
        #                'pressure', 'rain', 'humidity', 'wind', 'month', 'day_of_week', 'hour', 'minute']]
        self.X = self.data_lyft[['distance', 'surge_multiplier', 'name', 'day_of_week', 'hour', 'minute']]

        self.y = self.data_lyft['price']

    def train_model(self):
        # Initial split: Train-Test split
        X_train_lyft, self.X_test_lyft, y_train_lyft, self.y_test_lyft = train_test_split(self.X, self.y, test_size=0.2, random_state=42)

        # Further split Train into Train_Train and Train_Val
        X_train_train_lyft, self.X_train_val_lyft, y_train_train_lyft, self.y_train_val_lyft = train_test_split(X_train_lyft, y_train_lyft, test_size=0.25, random_state=42)  # 25% of 80% = 20%

        # Confirming the splits
        print(f"Train_Train: {X_train_train_lyft.shape}, Train_Val: {self.X_train_val_lyft.shape}, Test: {self.X_test_lyft.shape}")

        # Preprocessing pipeline
        preprocessor_lyft = ColumnTransformer(
            transformers=[
                ('label', LabelEncoderPipeline(), 'surge_multiplier'),  # Label encode 'surge_multiplier'
                ('onehot', OneHotEncoder(handle_unknown='ignore'), ['name'])    # One-hot encode 'name'
            ],
            remainder='passthrough'  # Keep other columns as-is
        )

        # Ensure X_train_train is properly formatted as a DataFrame
        X_train_train_lyft = X_train_train_lyft.reset_index(drop=True)
        self.X_train_val_lyft = self.X_train_val_lyft.reset_index(drop=True)
        self.X_test_lyft = self.X_test_lyft.reset_index(drop=True)

        # Define the full pipeline
        pipeline_lyft = Pipeline(steps=[
            ('preprocessor', preprocessor_lyft),
            ('regressor', XGBRegressor(objective='reg:squarederror', random_state=42))
        ])

        # Perform GridSearchCV on Train_Train and validate on Train_Val
        param_grid_lyft = {
            'regressor__n_estimators': [100, 200],
            'regressor__max_depth': [3, 5, 7],
            'regressor__learning_rate': [0.01, 0.1],
            'regressor__subsample': [0.8, 1.0]
        }
        grid_search_lyft = GridSearchCV(pipeline_lyft, param_grid_lyft, cv=3, scoring='neg_mean_squared_error', verbose=2, n_jobs=-1)
        grid_search_lyft.fit(X_train_train_lyft, y_train_train_lyft)
        self.best_params_lyft = grid_search_lyft.best_params_
        self.best_score_lyft = grid_search_lyft.best_score_

        best_model_lyft_pred = grid_search_lyft.best_estimator_
        joblib.dump(best_model_lyft_pred, self.model_path)
    
    def evaluate_model(self):
        best_model_lyft_loaded = joblib.load(self.model_path)

        # Validate on Train_Val
        y_val_pred_lyft = best_model_lyft_loaded.predict(self.X_train_val_lyft)
        val_mse = mean_squared_error(self.y_train_val_lyft, y_val_pred_lyft)

        # Evaluate on Test set
        y_test_pred_lyft = best_model_lyft_loaded.predict(self.X_test_lyft)
        test_mse = mean_squared_error(self.y_test_lyft, y_test_pred_lyft)

        val_r2 = r2_score(self.y_train_val_lyft, y_val_pred_lyft)
        test_r2 = r2_score(self.y_test_lyft, y_test_pred_lyft)
        
        print("*******************************Lyft Model Evaluation****************************")
        print("Best Parameters:", self.best_params_lyft)
        print("Best Cross-Validated Score (MSE):", -self.best_score_lyft)
        print("Validation MSE:", val_mse)
        print("Test MSE:", test_mse)

        print("Validation R²:", val_r2)
        print("Test R²:", test_r2)

class UberTraining:
    def __init__(self, dataset,model_path):
        self.data_uber = dataset
        self.model_path = model_path
        self.X = self.data_uber[['distance', 'name', 'day_of_week', 'hour', 'minute','temp','clouds','pressure','rain',	'humidity',	'wind']]
        self.y = self.data_uber['price']

    def train_model(self):
        # Initial split: Train-Test split
        X_train_uber, self.X_test_uber, y_train_uber, self.y_test_uber = train_test_split(X, y, test_size=0.2, random_state=42)

        # Further split Train into Train_Train and Train_Val
        X_train_train_uber, self.X_train_val_uber, y_train_train_uber, self.y_train_val_uber = train_test_split(X_train_uber, y_train_uber, test_size=0.25, random_state=42)  # 25% of 80% = 20%

        # Confirming the splits
        print(f"Train_Train: {X_train_train_uber.shape}, Train_Val: {self.X_train_val_uber.shape}, Test: {self.X_test_uber.shape}")

        # Preprocessing pipeline
        preprocessor_uber = ColumnTransformer(
            transformers=[
                ('onehot', OneHotEncoder(handle_unknown='ignore'), ['name'])    # One-hot encode 'name'
            ],
            remainder='passthrough'  # Keep other columns as-is
        )

        # Ensure X_train_train is properly formatted as a DataFrame
        X_train_train_uber = X_train_train_uber.reset_index(drop=True)
        self.X_train_val_uber = self.X_train_val_uber.reset_index(drop=True)
        self.X_test_uber = self.X_test_uber.reset_index(drop=True)

        # Define the full pipeline
        pipeline_uber = Pipeline(steps=[
            ('preprocessor', preprocessor_uber),
            ('regressor', XGBRegressor(objective='reg:squarederror', random_state=42))
        ])

        # Perform GridSearchCV on Train_Train and validate on Train_Val
        param_grid_uber = {
            'regressor__n_estimators': [100, 200],
            'regressor__max_depth': [3, 5, 7],
            'regressor__learning_rate': [0.01, 0.1],
            'regressor__subsample': [0.8, 1.0]
        }
        grid_search_uber = GridSearchCV(pipeline_uber, param_grid_uber, cv=5, scoring='neg_mean_squared_error', verbose=2, n_jobs=-1)
        grid_search_uber.fit(X_train_train_uber, y_train_train_uber)
        best_model_uber_pred = grid_search_uber.best_estimator_
        joblib.dump(best_model_uber_pred, self.model_path)
        self.best_params_uber = grid_search_uber.best_params_
        self.best_score_uber = grid_search_uber.best_score_
    
    def evaluate_model(self):
        best_model_lyft_loaded = joblib.load(self.model_path)

        # Validate on Train_Val
        y_val_pred_lyft = best_model_lyft_loaded.predict(self.X_train_val_uber)
        val_mse = mean_squared_error(self.y_train_val_uber, y_val_pred_lyft)

        # Evaluate on Test set
        y_test_pred_lyft = best_model_lyft_loaded.predict(self.X_test_uber)
        test_mse = mean_squared_error(self.y_test_uber, y_test_pred_lyft)

        val_r2 = r2_score(self.y_train_val_uber, y_val_pred_lyft)
        test_r2 = r2_score(self.y_test_uber, y_test_pred_lyft)
        
        print("*******************************Uber Model Evaluation****************************")
        print("Best Parameters:", self.best_params_uber)
        print("Best Cross-Validated Score (MSE):", -self.best_score_uber)
        print("Validation MSE:", val_mse)
        print("Test MSE:", test_mse)

        print("Validation R²:", val_r2)
        print("Test R²:", test_r2)
