import base64
import os
import time
import json
import requests
import streamlit as st
import google.generativeai as genai

def generate_content_with_library(input_text, model_name, temperature, top_p, top_k, max_tokens):
    """Gemini APIを使用してコンテンツを生成し、実行時間を計測する関数"""
    # APIキーを設定
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    # モデルを取得
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_tokens,
        }
    )

    # 開始時間を記録
    start_time = time.time()
    
    # 応答を格納するための変数
    full_response = ""
    
    # ストリーミングレスポンスを取得
    response = model.generate_content(
        input_text,
        stream=True,
    )
    
    for chunk in response:
        if hasattr(chunk, 'text'):
            full_response += chunk.text
    
    # 終了時間を記録
    end_time = time.time()
    
    # 実行時間を計算（ミリ秒単位）
    execution_time = (end_time - start_time) * 1000
    
    return full_response, execution_time

def generate_content_with_rest_api(input_text, model_name, temperature, top_p, top_k, max_tokens, api_key):
    """REST APIを直接使用してGemini APIを呼び出す関数"""
    # APIのエンドポイントURL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # リクエストヘッダー
    headers = {
        "Content-Type": "application/json"
    }
    
    # リクエストボディ
    data = {
        "contents": [{
            "parts": [{"text": input_text}]
        }],
        "generationConfig": {
            "temperature": temperature,
            "topP": top_p,
            "topK": top_k,
            "maxOutputTokens": max_tokens
        }
    }
    
    # 開始時間を記録
    start_time = time.time()
    
    # APIリクエストを送信
    response = requests.post(url, headers=headers, json=data)
    
    # 終了時間を記録
    end_time = time.time()
    
    # 実行時間を計算（ミリ秒単位）
    execution_time = (end_time - start_time) * 1000
    
    # レスポンスを処理
    if response.status_code == 200:
        response_json = response.json()
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            if 'content' in response_json['candidates'][0] and 'parts' in response_json['candidates'][0]['content']:
                parts = response_json['candidates'][0]['content']['parts']
                full_response = ''.join([part.get('text', '') for part in parts if 'text' in part])
                return full_response, execution_time
    
    # エラーの場合
    return f"Error: {response.status_code} - {response.text}", execution_time

def generate_content(input_text, model_name, temperature, top_p, top_k, max_tokens, api_method="library", api_key=None):
    """選択されたメソッドに基づいてコンテンツを生成する関数"""
    if api_method == "library":
        return generate_content_with_library(input_text, model_name, temperature, top_p, top_k, max_tokens)
    else:  # api_method == "rest_api"
        return generate_content_with_rest_api(input_text, model_name, temperature, top_p, top_k, max_tokens, api_key)

def load_config():
    """設定ファイルを読み込む関数"""
    config_path = ".windsurf/gemini_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"設定ファイルの読み込みに失敗しました: {str(e)}")
        return {
            "api_settings": {
                "gemini_api_key": "",
                "default_model": "gemini-2.0-flash-lite"
            },
            "generation_params": {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048
            },
            "preset_prompts": {
                "short_question": "東京の天気はどうですか？",
                "medium_question": "人工知能の歴史と現在の発展状況について500文字程度で説明してください。",
                "long_question": "気候変動の原因、影響、および対策について詳細に説明し、各国の取り組みと今後の展望についても言及してください。1000文字以上で回答してください。"
            },
            "app_config": {
                "measure_execution_time": True,
                "save_history": True,
                "max_history_items": 50
            }
        }

def main():
    st.set_page_config(page_title="Gemini API 実行時間測定", page_icon="⏱️", layout="wide")
    
    # 設定ファイルを読み込む
    config = load_config()
    
    st.title("Gemini API 実行時間測定アプリ")
    st.markdown("Gemini APIの入力から出力までの時間を測定するアプリケーションです。")
    
    # サイドバーにAPI設定を配置
    st.sidebar.header("API設定")
    
    # APIキー入力（パスワードとして表示）
    api_key = st.sidebar.text_input("GEMINI_API_KEY", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        
    # API呼び出し方法の選択
    api_method = st.sidebar.radio(
        "API呼び出し方法",
        ["Python ライブラリ", "REST API (直接呼び出し)"],
        index=0,
        help="Gemini APIの呼び出し方法を選択します。Python ライブラリは使いやすく、REST APIは低レベルの制御が可能です。"
    )
    
    # 内部処理用に変換
    api_method_internal = "library" if api_method == "Python ライブラリ" else "rest_api"
    
    # モデル選択
    model_options = [
        "gemini-1.5-pro", 
        "gemini-1.5-flash", 
        "gemini-2.0-pro-exp-02-05", 
        "gemini-2.0-flash-lite"
    ]
    model_name = st.sidebar.selectbox(
        "モデル", 
        model_options, 
        index=model_options.index(config["api_settings"]["default_model"]) if config["api_settings"]["default_model"] in model_options else 3
    )
    
    # パラメータ設定
    st.sidebar.header("生成パラメータ")
    temperature = st.sidebar.slider(
        "Temperature", 
        0.0, 1.0, 
        config["generation_params"]["temperature"], 
        0.1
    )
    top_p = st.sidebar.slider(
        "Top P", 
        0.0, 1.0, 
        config["generation_params"]["top_p"], 
        0.05
    )
    top_k = st.sidebar.slider(
        "Top K", 
        1, 100, 
        config["generation_params"]["top_k"], 
        1
    )
    max_tokens = st.sidebar.slider(
        "最大出力トークン数", 
        100, 8192, 
        config["generation_params"]["max_output_tokens"], 
        100
    )
    
    # 入力テキストエリア
    st.header("入力テキスト")
    input_text = st.text_area("プロンプトを入力してください", height=200)
    
    # プリセットプロンプト
    st.header("プリセットプロンプト")
    preset_prompts = {
        "短い質問": config["preset_prompts"]["short_question"],
        "中程度の質問": config["preset_prompts"]["medium_question"],
        "長い質問": config["preset_prompts"]["long_question"]
    }
    
    preset_cols = st.columns(len(preset_prompts))
    for i, (name, prompt) in enumerate(preset_prompts.items()):
        if preset_cols[i].button(name):
            input_text = prompt
            st.session_state.input_text = prompt
            st.experimental_rerun()
    
    # 実行ボタン
    if st.button("実行", type="primary", disabled=not (api_key and input_text)):
        with st.spinner("Gemini APIからの応答を待っています..."):
            try:
                # 進捗バーを表示
                progress_bar = st.progress(0)
                
                # APIを呼び出して結果と実行時間を取得
                response, execution_time = generate_content(
                    input_text, 
                    model_name, 
                    temperature, 
                    top_p, 
                    top_k, 
                    max_tokens,
                    api_method_internal,
                    api_key
                )
                
                progress_bar.progress(100)
                
                # 結果表示エリア
                st.header("結果")
                
                # 実行時間の表示
                st.metric("実行時間", f"{execution_time:.2f} ミリ秒")
                
                # 出力テキストの表示
                st.subheader("出力テキスト")
                st.text_area("応答", response, height=400)
                
                # 実行情報の表示
                st.subheader("実行情報")
                execution_info = {
                    "API呼び出し方法": api_method,
                    "モデル": model_name,
                    "Temperature": temperature,
                    "Top P": top_p,
                    "Top K": top_k,
                    "最大出力トークン数": max_tokens,
                    "入力テキスト文字数": len(input_text),
                    "出力テキスト文字数": len(response),
                    "実行時間(ms)": f"{execution_time:.2f}"
                }
                
                # 実行情報をテーブルとして表示
                st.table(execution_info)
                
                # 履歴に追加（セッション状態を使用）
                if 'history' not in st.session_state:
                    st.session_state.history = []
                
                st.session_state.history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "api_method": api_method,
                    "model": model_name,
                    "input_length": len(input_text),
                    "output_length": len(response),
                    "execution_time": execution_time
                })
                
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
    
    # 履歴表示
    if 'history' in st.session_state and st.session_state.history:
        st.header("実行履歴")
        # 設定ファイルから最大履歴数を取得
        max_history = config["app_config"]["max_history_items"]
        # 履歴が最大数を超えた場合、古いものから削除
        if len(st.session_state.history) > max_history:
            st.session_state.history = st.session_state.history[-max_history:]
        history_df = st.dataframe(st.session_state.history)

if __name__ == "__main__":
    main()
