import streamlit as st
import json
import requests
import time

def input_apikey() -> str:
    """APIkeyを取得する
    """
    key = st.sidebar.text_input("自動要約生成APIキーを入力")
    st.sidebar.write("APIキーが無い場合は発行してください\n \
            https://cl.asahi.com/api_data/longsum.html")
    if key:
        if len(key) != 40:
            st.warning("APIキーの文字数が不正です")
        else:
            return key

def select_task():
    """タスクを設定
    """
    length = 0
    rate = 0

    task = st.sidebar.selectbox(
        "何をしますか？",
        (
        "指定した長さごとに生成型要約",
        "すべての文の長さを揃える",
        # "すべての文を圧縮する",
        "重要な文を抽出する",
        "重要な文を抽出後圧縮して、指定した長さにする",
        )
    )
    if task == "指定した長さごとに生成型要約":
        num_setting = st.sidebar.number_input("本文を何文字ずつ区切って要約しますか？（200～2000字）", 200, 2000, step=10)
        url = "https://clapi.asahi.com/abstract"

    if task == "すべての文の長さを揃える":
        num_setting = st.sidebar.number_input("一文の文字数は何文字にしますか？（10～50字）", 10, 50, 25, step=5)
        url = "https://clapi.asahi.com/align"

    # if task == "すべての文を圧縮する":
    #     rate = st.sidebar.number_input("本文を何文字ずつ区切って要約しますか？（200～2000字）", 200, 2000, step=10)
    #     url = # 朝日のリファレンス側がURL記載ミス

    if task == "重要な文を抽出する":
        num_setting = st.sidebar.number_input("全体の何割から文を抽出しますか？（0.1～0.9）", 0.1, 0.9, step=0.1)
        url = "https://clapi.asahi.com/extract"

    if task == "重要な文を抽出後圧縮して、指定した長さにする":
        num_setting = st.sidebar.number_input("一文の文字数は何文字にしますか？（10～2000字）", 10, 2000, 500, step=10)
        url = "https://clapi.asahi.com/control-len"

    if task:
        auto_paragraph = st.sidebar.checkbox("パラグラフ分割：要約後の文章から自動的に段落を判断し段落ごとに分割して返却します。", True)
        st.sidebar.write(auto_paragraph)
        st.markdown(f"## {task}")

    return task, url, num_setting, auto_paragraph

def input_text() -> str:
    """要約するテキストを取得
    """
    text = st.text_input("要約する文章を入力（100～2000字）", max_chars=2000)
    return text

def sample_text_1() -> str:
    """動作確認用にサンプルテキストを取得
    """
    with open('sample1.txt', 'r') as f:
        text = f.read()
    return text

def sample_text_2() -> str:
    """動作確認用にサンプルテキストを取得
    """
    with open('sample2.txt', 'r') as f:
        text = f.read()
    return text

def set_page_layout() -> None:
    """画面の横幅等のレイアウト設定
    """
    color = "rgb(16,16,16)"
    background_color = "#fff"
    max_width = 1200
    padding_top = 5
    padding_right = 1
    padding_left = 1
    padding_bottom = 10

    st.markdown(
        f"""
        <style>
            .reportview-container .main .block-container{{
                max-width: {max_width}px;
                padding-top: {padding_top}rem;
                padding-right: {padding_right}rem;
                padding-left: {padding_left}rem;
                padding-bottom: {padding_bottom}rem;
            }}
            .reportview-container .main {{
                color: {color};
                background-color: {background_color};
            }}
        </style>
        """,
                unsafe_allow_html=True,
    )

def main():
    """main処理
    """

    key = input_apikey()
    
    if key:
        set_page_layout()
        task, url, num_setting, auto_paragraph = select_task()

        input_type = st.radio(
            "要約する文章を選択してください",
            ("サンプル1", "サンプル2", "手入力")
        )
        if input_type == "サンプル1":
            text = sample_text_1()
        elif input_type == "サンプル2":
            text = sample_text_2()
        else:
            text = input_text()

        if text:
            st.write(text)
        
        if task in ["指定した長さごとに生成型要約", "すべての文の長さを揃える", "重要な文を抽出後圧縮して、指定した長さにする"]:
            input_json = json.dumps({"text": text, "length": num_setting, "auto_paragraph":auto_paragraph})

        if task in ["重要な文を抽出する"]:
            input_json = json.dumps({"text": text, "rate": num_setting, "auto_paragraph":auto_paragraph})     
        
        headers = {"accept":"application/json", "Content-Type":"application/json", "x-api-key":key}
        
        run = st.button("要約実行")
        if run:
            st.write("要約中...")
            # リクエスト送信
            response = requests.post(url, input_json, headers=headers)

            # 負荷軽減のために5秒スリープ
            time.sleep(5)

            # エンドポイントからレスポンスあったら結果を表示
            if response.status_code == 200:
                result = response.json()["result"]
                num_sentence = len(result)
                for i in range(num_sentence):
                    st.write(f"・{result[i]}")

            elif response.status_code == 403:
                st.warning("<403>APIキーが不正")

            elif response.status_code == 500:
                st.warning("<500>サーバ処理で異常発生")

            elif response.status_code == 503:
                st.warning("<503>サーバ処理で異常発生")

            elif response.status_code == 429:
                st.warning("<429>アクセス数の制限を超過（1日20アクセス）")
            else:
                st.warning(response)
        
            st.write("★★★要約終了★★★")

main()