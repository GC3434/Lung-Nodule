
import matplotlib

# Use the Agg backend for Matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from roboflow import Roboflow
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, concatenate

app = Flask(__name__)

# Roboflow setup last commit
roboflow_api_key = "gJ5NmruB1DqLsgYxaPAl"   
rf = Roboflow(api_key=roboflow_api_key)
project = rf.workspace().project("lung-nodule-z4exc")
model3 = project.version(1).model

import os

# Get the directory path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
model_file = os.path.join(current_dir, 'concat_pref.h5')

concatenated_model = tf.keras.models.load_model(model_file)


#concatenated_model= tf.keras.models.load_model('concat_pref.h5')

class_names = ['Benign', 'Malignant', 'Normal']

def analyze_and_plot(img_path, class_label, accuracy):
    img = Image.open(img_path)
    img = img.convert("RGB")

    # Create a figure and axes for the uploaded image
    plt.figure(figsize=(4, 2))
    plt.imshow(img, cmap='gray')
    plt.title(f'Prediction: {class_label}')
    uploaded_plot_path = "static/images/uploaded_plot.jpg"
    plt.savefig(uploaded_plot_path)
    plt.close()

    return uploaded_plot_path

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def analyze_image():
    # Ensure there's at least one file uploaded
    if 'imagefile' not in request.files:
        return render_template('index.html', error='No file uploaded!')

    img = request.files['imagefile']

    # Save the uploaded image
    img_path = "static/images/uploaded_image.jpg"
    img.save(img_path)

    # Load and preprocess the imagex
    img = Image.open(img_path)
    img = img.convert("RGB")
    img = img.resize((256, 256))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Get the predicted class probabilities
    predictions = concatenated_model.predict([img_array, img_array])

    predicted_classes = [class_names[idx] for idx in np.argmax(predictions, axis=1)]
  
    # Get the predicted class index
    predicted_class_index = np.argmax(predictions[0])
 
     # Get the accuracy for the predicted class
    accuracy = predictions[0][predicted_class_index]   
    # Run prediction on the uploaded image using Roboflow model
    prediction = model3.predict(img_path, confidence=40, overlap=30)

    # # Visualize the prediction and save the image
    pred_path = "static/images/prediction.jpg"
    prediction.save(pred_path)

    # Use the analyze_and_plot function to handle Tkinter in a separate function
    uploaded_plot_path = analyze_and_plot(img_path, predicted_classes[0], accuracy)

    return render_template('index.html', img_path=img_path, result=predicted_classes[0], accuracy=accuracy, uploaded_plot=uploaded_plot_path)

@app.after_request
def cleanup(response):
    plt.close('all')
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=3000, debug=True)
