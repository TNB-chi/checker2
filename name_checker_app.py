import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# PDFから全文テキストを抽出
def extract_text_from_pdf(pdf_file):
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

# 生徒名ごとの出現回数をカウント
def count_name_occurrences(text, name_list):
    name_counts = {}
    for name in name_list:
        name_counts[name] = text.count(name)
    return name_counts

st.title("📄 出席回数カウント（PDF内の名前出現回数）")

# ファイルアップロード
pdf_file = st.file_uploader("📎 生徒名が書かれたPDF（スケジュール表など）", type="pdf")
name_file = st.file_uploader("📋 名簿ファイル（Excel、1列目：名前、2列目：予定回数）", type=["xlsx"])

if pdf_file and name_file:
    try:
        # 名簿読み込み
        df = pd.read_excel(name_file)
        df = df.iloc[:, :2]
        df.columns = ["名前", "予定回数"]
        df["予定回数"] = df["予定回数"].astype(int)
    except Exception as e:
        st.error(f"名簿ファイルの読み込みに失敗しました：{e}")
        st.stop()

    # PDFテキスト抽出
    text = extract_text_from_pdf(pdf_file)

    # 生徒名の出現回数カウント
    name_list = df["名前"].astype(str).tolist()
    actual_counts = count_name_occurrences(text, name_list)

    # 結果比較
    results = []
    for _, row in df.iterrows():
        name = row["名前"]
        planned = row["予定回数"]
        actual = actual_counts.get(name, 0)
        status = "✅ 一致" if planned == actual else f"❌ 不一致（実際: {actual}回）"
        results.append({
            "名前": name,
            "予定回数": planned,
            "実際の出席回数": actual,
            "判定": status
        })

    result_df = pd.DataFrame(results)

    st.subheader("📊 照合結果")
    st.dataframe(result_df)

    csv = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 結果をCSVでダウンロード", csv, "attendance_result.csv", "text/csv")
