import os
from flask import Flask, request, jsonify
import base64
import requests
import csv
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Google Cloud Vision APIキー
api_key = 'API_KEY'

# アップロードされた画像を保存するフォルダを設定
UPLOAD_FOLDER = 'C:/python_portfolio/mooooosic'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# CSVファイルからランダムな行を選択する関数
def get_random_elements(csv_file, num_elements):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)
        random_elements = random.sample(data, num_elements)
        return random_elements
    
# 各感情の判定文字列を数値に変換
def convert_emotion_likelihood(emotion_likelihood):
    if emotion_likelihood == 'UNKNOWN':
        return 0.0
    elif emotion_likelihood == 'VERY_UNLIKELY':
        return 0.2
    elif emotion_likelihood == 'UNLIKELY':
        return 0.4
    elif emotion_likelihood == 'POSSIBLE':
        return 0.6
    elif emotion_likelihood == 'LIKELY':
        return 0.8
    elif emotion_likelihood == 'VERY_LIKELY':
        return 1.0
    else:
        return 0.0  # 未知の場合は0.0として扱う

@app.route('/detect-emo', methods=['POST'])
def detect_emo():
    
        data = request.get_json()
        newdata=data.get('capturedImage')
        base64_data = newdata.split(",")[1]
        image_data = base64.b64decode(base64_data)
        print(base64_data)
        #captured_image = data.get('capturedImage')

        # ここでcapturedImageを使用して感情を判定する処理を実行
        #encoded_image = base64.b64encode(captured_image).decode('utf-8')
        #captured_image_binary = base64.b64decode(image_data)
        #print(captured_image_binary)
        request_data = {
                "requests": [
                    {
                        "image": {
                            "content": base64_data
                        },
                        "features": [
                            {
                                "type": "FACE_DETECTION",
                                "maxResults": 1
                            }
                        ]
                    }
                ]
            }        
            # Google Cloud Vision APIにリクエストを送信
        url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
        response = requests.post(url, json=request_data)

        # レスポンスのJSONデータを取得
        response_json = response.json()

        # レスポンスデータから感情情報を抽出
        emotion_data = response_json['responses'][0]['faceAnnotations'][0]
        joy_likelihood = emotion_data['joyLikelihood']
        sorrow_likelihood = emotion_data['sorrowLikelihood']
        anger_likelihood = emotion_data['angerLikelihood']
        surprise_likelihood = emotion_data['surpriseLikelihood']
        detection_confidence = emotion_data['detectionConfidence']

        joy_likelihood_numeric = convert_emotion_likelihood(joy_likelihood)
        sorrow_likelihood_numeric = convert_emotion_likelihood(sorrow_likelihood)
        anger_likelihood_numeric = convert_emotion_likelihood(anger_likelihood)
        surprise_likelihood_numeric = convert_emotion_likelihood(surprise_likelihood)

        # 最も高い値を選ぶ
        highest_likelihood = max(joy_likelihood_numeric, sorrow_likelihood_numeric, anger_likelihood_numeric, surprise_likelihood_numeric)
        print(highest_likelihood)

        # 最も高い感情を判定
        if highest_likelihood == joy_likelihood_numeric:
            highest_emotion = 'happy'
        elif highest_likelihood == sorrow_likelihood_numeric:
            highest_emotion = 'sad'
        elif highest_likelihood == anger_likelihood_numeric:
            highest_emotion = 'anger'
        else:
            highest_emotion = 'surprise'

        # 結果をJSONとして返す
        result = {
            "emotion": highest_emotion,
        }

        return jsonify(result)


@app.route('/api/random', methods=['POST'])
def get_random_data():
    print(request)
    request_data = request.get_json()
    emotion = request_data.get('emotion_type')
    #emotion = request.args.get('emotion_type')  # リクエストパラメータからCSVファイルのパスを取得
    num_elements = 10  # 取得したいランダムな要素の数
    random_elements = get_random_elements(f"mooooosic/{emotion}.csv", num_elements)
    return jsonify(random_elements)

@app.route('/api/happy', methods=['POST'])
def get_happy_data():
    usedata = request.get_json()
    cdata = usedata.get('capturedImage')
    return "happy"


if __name__ == '__main__':
    # アップロードフォルダを作成
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(port=5000)
