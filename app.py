from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Load model Random Forest terbaik Anda
model = joblib.load('best_rf_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Ekstrak 10 fitur yang dibutuhkan model (tanpa Nama dan Jenis Kelamin)
        features = {
            "Age": data["Age"],
            "Salt_Intake": data["Salt_Intake"],
            "Stress_Score": data["Stress_Score"],
            "BP_History": data["BP_History"],
            "Sleep_Duration": data["Sleep_Duration"],
            "BMI": data["BMI"],
            "Medication": data["Medication"],
            "Family_History": data["Family_History"],
            "Exercise_Level": data["Exercise_Level"],
            "Smoking_Status": data["Smoking_Status"]
        }
        
        # Ubah ke DataFrame dan Prediksi
        input_df = pd.DataFrame([features])
        prediction = model.predict(input_df)[0]
        
        # Interpretasi hasil (1 = Berisiko, 0 = Normal)
        result = "Beresiko Hipertensi" if prediction == 1 else "Normal"
        
        return jsonify({'status': 'success', 'prediction': result})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)