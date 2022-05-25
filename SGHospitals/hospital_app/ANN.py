#Rede Neural
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn import linear_model
from math import sqrt
import pandas as pd
import numpy as np
import pickle
import os

def predict(dataframe):  

      csv= 'resultados_completo.csv'
      dataframe_control = pd.read_csv(csv)
      X = dataframe_control.loc[:, ['Rooftransmittance', 'Walltransmittance', 'Parede Interna', 'RoofAbsortance','WallAbsortance',  'SGH', 'DPI', 'CDH']].copy()
      z = dataframe_control.loc[:, ['Consumo']].copy()

      X_encoded = pd.get_dummies(X, columns = ['Parede Interna'])
      print(X_encoded)
      df_predict = dataframe.loc[:,['Rooftransmittance','Walltransmittance','RoofAbsortance','WallAbsortance','SGH','DPI','CDH','InternalWall1', 'InternalWall2','InternalWall3']]

      y = np.ravel(z)
      X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size = 0.2, train_size = 0.8, random_state = 2101)


      scaler = preprocessing.StandardScaler().fit(X_train)
      X_train_scaled = scaler.transform(X_train)
      X_test_scaled = scaler.transform(X_test)

      df_encoded_scaled= scaler.transform(df_predict)
      ANN = MLPRegressor(random_state = 2101, alpha = 0.0001, hidden_layer_sizes = (40), learning_rate_init = 0.01)
      ANN.fit(X_train_scaled, y_train)
      y_pred = ANN.predict(X_test_scaled)

      #Predict consumption with ANN model

      filename = 'modelo_ANN_hospital.sav'
      ANN_model = pickle.load(open(filename, 'rb'))
      ann_extras = ANN_model.predict(df_encoded_scaled)
      df_ann = pd.DataFrame(ann_extras,  columns= ['Consumo'])

      return df_ann
