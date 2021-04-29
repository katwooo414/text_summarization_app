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
        num_setting = st.sidebar.number_input("出力する要約文のトータルの長さは？（10～2000字）", 10, 2000, 500, step=10)
        url = "https://clapi.asahi.com/control-len"

    if task:
        auto_paragraph = st.sidebar.checkbox("パラグラフ分割：段落単位に複数の要約文が結合されて返却されます", True)
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
    text = '九州電力玄海原発３、４号機（佐賀県玄海町）の運転差し止めを住民らが求めた仮処分申し立ての即時抗告審で、福岡高裁（山之内紀行裁判長）は１０日、住民側の抗告を棄却した。主な争点は、耐震設計の基になる基準地震動（想定される最大の揺れ）の合理性、原発周辺の火山の噴火リスク、配管の安全性の３点。 住民側は「基準地震動が過小評価されている」と主張。原子力規制委員会の安全審査の内規（火山影響評価ガイド）は、破局的噴火が予測できることを前提としている点は不合理と指摘。阿蘇カルデラ火山の噴火による火砕流が原発の敷地に到達する可能性も、十分小さいとは言えないと訴えていた。配管については「九電の検査方法では損傷が見逃されることがありうる」としていた。九電側は、基準地震動の評価について「各種調査で地域的な特性を把握した上、過小にならないようにしており合理的だ」と反論。「原発の運用期間中に破局的噴火が起きる可能性は極めて低い」と主張していた。配管については「健全性の確保に向け万全を期している」としていた。佐賀地裁は２０１７年６月、「安全性に欠けるところがあるとは認められない」などとして、仮処分の申し立てを却下。住民側が即時抗告していた。'
    return text

def sample_text_2() -> str:
    """動作確認用にサンプルテキストを取得
    """
    text = '文章の論旨や要点を短くまとめて表現する要約文。学生の頃、レポート作成などで書いた経験があるものの、それ以降はまったく書いていないという人は多いことでしょう。しかし、文章作成が苦手な人や、文章がわかりにくいと指摘される人、自分の考えが相手に伝わらないと悩む人は、改めて「要約」に注目してみるべきです。なぜならば、要約文を書く練習には、文章力と読解力を鍛える効果があるから。これらは、単に国語力を磨くだけでなく、日常生活やビジネスシーンにも良い影響をもたらします。今回は、要約の練習によって得られるメリットや、具体的な練習方法について詳しくご説明しましょう。要約文を作成するには、単語の意味を正しく理解しなければいけません。また、文字数調整のために、単語を別の言葉に言い換える必要も出てきますよね。こうしたトレーニングにより、自然と語彙力が高まり、結果的に文章力が向上していきます。『大人に必要な「読解力」がきちんと身につく 読みトレ』の著者・吉田裕子氏は、日常でただ会話したり、漫然と文章を読んだりしているだけでは、これらの能力はなかなか向上しないと述べます。漫然と文章を読んでいるだけでは、語彙力は少しずつしか伸びません。成長を速くするには、言葉を調べたりメモしたりすることを習慣化すべきです。読解力を高めるには「本を読めばいい」とよく言われますが、学習・教育アドバイザーの伊藤敏雄氏は、この考えに否定的です。伊藤氏によると、読みに関する記憶力（リーディングスパン）が弱いままで読書を繰り返しても、読解力はつかないのだとか。リーディングスパンが弱い人は、穴が開いたバケツから水がこぼれてしまうように、情報が穴からどんどん抜け出てしまうのです。一方、要約の練習を通して主語と述語を正しく理解できるようになると、バケツの穴から情報が抜け出ることはなくなり、読解力の向上にもつながると、伊藤氏は述べます。主語と述語を正しく読みとること、これが「バケツの穴をふさぐこと」、つまり読解力を上げることにつながるのです。また、都留文科大学特任教授の石田勝紀氏は、読解力の向上は次のような形で日常生活にもメリットをもたらすと述べます。意味を理解する力は、あらゆる場面で発揮されます。つまり、どのような科目でも、分野でも、さらに言えば、仕事でも、日常生活におけるさまざまな出来事でも発揮されます。つまり、要約の練習は、単に読み書きを鍛えるだけでなく、仕事などのスキルアップにも役立つのです。出典：https://studyhacker.net/inventory-training-3method'
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

            # # 負荷軽減のために5秒スリープ
            # time.sleep(5)

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