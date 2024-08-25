import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model, load_model

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Flatten

from tensorflow.keras.layers import Input, Dense, LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import ModelCheckpoint
import Sharing_data
from Trading_main import Futures_bot

def prepare_Heikin_Ashi_data(df):
    # Label the data (1 if the next candle is green, 0 if red)
    df['Label'] = (df['HA_Close'].shift(-1) > df['HA_Open'].shift(-1)).astype(int)
    df = df.dropna()

    # Prepare the data for the transformer
    features = df[['HA_Open', 'HA_High', 'HA_Low', 'HA_Close']].values

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_features = scaler.fit_transform(features)
    return scaled_features, df

def train_Heikin_Ashi_model(df, sequence_length=3, model_file=None):
    # get data
    scaled_features, df = prepare_Heikin_Ashi_data(df=df)
    labels = df['Label'].values
    # Create the dataset for the transformer
    X, y = [], []
    
    for i in range(sequence_length, len(scaled_features)):
        X.append(scaled_features[i-sequence_length:i])
        y.append(labels[i])
    X, y = np.array(X), np.array(y)

    # Convert labels to categorical
    y = to_categorical(y, num_classes=2)

    # Check data shapes
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    # Transformer model definition
    """
    input_layer = Input(shape=(X.shape[1], X.shape[2]))
    attention = MultiHeadAttention(num_heads=1, key_dim=1)(input_layer, input_layer)
    attention = LayerNormalization(epsilon=1e-6)(attention)
    output = GlobalAveragePooling1D()(attention)
    output = Dense(units=2, activation='softmax')(output)

    model = Model(inputs=input_layer, outputs=output)
    """
    # Simplified model definition
    model = Sequential([
        Input(shape=(X.shape[1], X.shape[2])),
        Flatten(),
        Dense(50, activation='relu'),
        Dense(25, activation='relu'),
        Dense(2, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Define a callback to save the model
    checkpoint = ModelCheckpoint(model_file, save_best_only=True, monitor='val_loss', mode='min')

    model.summary()

    # Train the model
    model.fit(X_train, y_train, epochs=20, batch_size=4, verbose=1, validation_data=(X_test, y_test), callbacks=[checkpoint])

    # Evaluate the model
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    Sharing_data.append_to_file("Test Accuracy:", accuracy)

def predict_next_Heikin_Ashi_candle(df, sequence_length=3, model_file=None):
    # sequence_length shall be the same as the one used for training
    # Load the best model
    model = load_model(model_file)
    # get data
    scaled_features, df = prepare_Heikin_Ashi_data(df=df)
    # Predict the probability of the next Heikin-Ashi candle being green or red
    last_data = np.expand_dims(scaled_features[-sequence_length:], axis=0)
    predicted_probabilities = model.predict(last_data)

    # Print the probabilities
    probability_red, probability_green = predicted_probabilities[0]
    Sharing_data.append_to_file("Probability of next Heikin-Ashi candle being red:", probability_red)
    Sharing_data.append_to_file("Probability of next Heikin-Ashi candle being green:", probability_green)

if __name__ == "__main__":
	Bot = Futures_bot()
	Sharing_data.erase_folder_content(folder_path=Bot.crypto[0].folder_path)
	Sharing_data.append_to_file(f"Function Heikin Ashi price color change")

	Sharing_data.append_to_file(f"Get last klines")
	Bot.crypto[0].df = Bot.binance.fetch_klines(symbol=Bot.crypto[0].symbol_spot, timeframe=Bot.crypto[0].timeframe, since=None, limit=2000, market_type='spot')
	Bot.crypto[0].df = Trading_tools.calculate_heikin_ashi(Bot.crypto[0].df)
	Sharing_data.append_to_file(f"Train model")
	scaled_features, Bot.crypto[0].df = ml_prediction.prepare_Heikin_Ashi_data(df=Bot.crypto[0].df)

	X, y = [], []
	sequence_length = 3

	labels = Bot.crypto[0].df['Label'].values

	for i in range(sequence_length, len(scaled_features)):
		X.append(scaled_features[i-sequence_length:i])
		y.append(labels[i])
	X, y = np.array(X), np.array(y)

	#ml_prediction.train_Heikin_Ashi_model(Bot.crypto[0].df, sequence_length=3, model_file=Bot.crypto[0].model_file)

	#ml_prediction.predict_next_Heikin_Ashi_candle(Bot.crypto[0].df, sequence_length=3, model_file=Bot.crypto[0].model_file)
