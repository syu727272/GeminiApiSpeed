# Gemini API 実行時間測定アプリ

このアプリケーションは、Gemini APIの入力から出力までの時間を測定するStreamlitアプリです。

## 機能

- Gemini APIへの入力テキストを設定できるフォーム
- 複数のモデル選択（gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-pro, gemini-2.0-flash-lite）
- 生成パラメータのカスタマイズ（Temperature, Top P, Top K, 最大出力トークン数）
- プリセットプロンプトの選択機能
- 実行時間の測定と表示
- 実行履歴の記録

## セットアップ

1. 必要なパッケージをインストール:
```
pip install -r requirements.txt
```

2. Gemini APIキーを取得:
   - [Google AI Studio](https://makersuite.google.com/app/apikey) からAPIキーを取得してください

3. アプリケーションの実行:
```
streamlit run app.py
```

## 使用方法

1. サイドバーにGemini APIキーを入力
2. 使用するモデルと生成パラメータを設定
3. プロンプトを入力するか、プリセットプロンプトを選択
4. 「実行」ボタンをクリックして結果を取得

## 注意事項

- APIキーは環境変数として一時的に保存されます
- 実行履歴はセッション中のみ保持されます（ブラウザを更新すると消去されます）
