import io
import os
import json
import numpy as np
import base64
import tensorflow as tf
from flask import Flask, request, jsonify
from PIL import Image
from youtube_api.service_yt import youtubevd

app = Flask(__name__)

MODEL_PATH = 'Mobilenetv3large_Plant_disease_detection.keras'
LABELS_PATH = 'labels.json'

model = tf.keras.models.load_model(MODEL_PATH)

with open(LABELS_PATH, 'r') as f:
    labels_with_descriptions = json.load(f)

# Preprocess gambar untuk prediksi
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))

    if img.mode != "RGB":
        img = img.convert("RGB")

    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = tf.keras.applications.mobilenet_v3.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# Prediksi penyakit
def predict_disease(proses_gambar):
    THRESHOLD = 0.5

    hasil_prediksi = model.predict(proses_gambar)
    indeks_kelas = np.argmax(hasil_prediksi[0])
    tingkat_prediksi = float(hasil_prediksi[0][indeks_kelas])

    if tingkat_prediksi < THRESHOLD:
        return None, tingkat_prediksi
    
    nama_penyakit = list(labels_with_descriptions.keys())[indeks_kelas]
    return nama_penyakit, tingkat_prediksi

# Proses respons prediksi
def process_prediction(nama_penyakit, tingkat_prediksi):
    if not nama_penyakit:
        return jsonify({
            'status': 'error',
            'message': 'Gambar tidak dikenali. Silakan coba dengan gambar yang berbeda.'
        }), 400
    
    videos = youtubevd(nama_penyakit)
    
    return jsonify({
        'status': 'success',
        'prediction': {
            'nama_penyakit': nama_penyakit,
            'tingkat_prediksi': tingkat_prediksi,
            'keterangan': labels_with_descriptions.get(nama_penyakit, 'Tidak ada deskripsi tersedia')
             
        },
        'videos': videos
    }), 200


@app.route('/', methods=['GET']) 
def index():
    #cek status api
    return jsonify({
        "message": "API sukses",
        "labels": list(labels_with_descriptions.keys())
    }), 200

@app.route('/predict/upload', methods=['POST']) #prediksi jika upload image
def predict_upload():
    try:
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Tidak ada file gambar ditemukan'
            }), 400
        
        image_file = request.files['image']
        image_bytes = image_file.read()
        proses_gambar = preprocess_image(image_bytes)
        nama_penyakit, tingkat_prediksi = predict_disease(proses_gambar)

        return process_prediction(nama_penyakit, tingkat_prediksi)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Kesalahan dalam memproses permintaan: {str(e)}'
        }), 500

@app.route('/predict/base64', methods=['POST']) #prediksi jika scan image/dari kamera
def predict_base64():
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Tidak ada data gambar base64 ditemukan'
            }), 400
        
        # Hapus header base64 jika ada
        base64_image = data['image']
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]

        image_bytes = base64.b64decode(base64_image)
        proses_gambar = preprocess_image(image_bytes)
        nama_penyakit, tingkat_prediksi = predict_disease(proses_gambar)

        return process_prediction(nama_penyakit, tingkat_prediksi)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Kesalahan dalam memproses permintaan: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))
