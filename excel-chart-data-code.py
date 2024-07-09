import streamlit as st
import pandas as pd

# ファイルアップロード
uploaded_file = st.file_uploader("売上仕入データのExcelファイルをアップロードしてください", type=["xlsx"])

if uploaded_file is not None:
    try:
        sales_df = pd.read_excel(uploaded_file, sheet_name="売上")
        purchase_df = pd.read_excel(uploaded_file, sheet_name="仕入")
    except Exception as e:
        st.error(f"Excelファイルの読み込み中にエラーが発生しました: {e}")
        st.stop()  # エラー発生時は処理を停止

    # "判定" 列をブール型に変換 (ExcelのTRUE/FALSEをPythonのTrue/Falseに変換)
    sales_df["判定"] = sales_df["判定"].astype(bool)
    purchase_df["判定"] = purchase_df["判定"].astype(bool)

    # FALSE判定の行を抽出
    false_sales = sales_df[sales_df["判定"] == False]
    false_purchase = purchase_df[purchase_df["判定"] == False]

    # Streamlitアプリ
    st.title("売上仕入データ分析")

    st.header('FALSE判定の売上データ')
    if not false_sales.empty:
        st.dataframe(false_sales)
    else:
        st.info("FALSE判定の売上データはありません。")

    st.header('FALSE判定の仕入データ')
    if not false_purchase.empty:
        st.dataframe(false_purchase)
    else:
        st.info("FALSE判定の仕入データはありません。")

    # --------------------
    # 分析とグラフの追加 (必要に応じて修正)
    # --------------------
    st.header("分析結果")

    # 1. FALSE判定件数と割合
    st.subheader("FALSE判定の件数と割合")
    total_sales = len(sales_df)
    total_purchase = len(purchase_df)
    num_false_sales = len(false_sales)
    num_false_purchase = len(false_purchase)

    st.write(f"売上データ:  FALSE判定 {num_false_sales} 件 ({num_false_sales/total_sales:.2%})")
    st.write(f"仕入データ:  FALSE判定 {num_false_purchase} 件 ({num_false_purchase/total_purchase:.2%})")

    # 2. FALSE判定の売上・仕入合計
    st.subheader("FALSE判定の売上・仕入合計")
    total_sales_false = false_sales["売上本体金額"].sum()
    total_purchase_false = false_purchase["仕入本体金額"].sum()

    st.write(f"FALSE判定の売上合計: {total_sales_false:,} 円")
    st.write(f"FALSE判定の仕入合計: {total_purchase_false:,} 円")

    # 3. 仕入先別FALSE判定件数 
    st.subheader("仕入先別FALSE判定件数")
    supplier_false_counts = false_purchase["仕入先名"].value_counts()
    st.dataframe(supplier_false_counts)
    st.bar_chart(supplier_false_counts)

    # 4. 売上単価と仕入単価の散布図 (FALSE判定のみ)
    st.subheader("売上単価と仕入単価の散布図 (FALSE判定)")
    st.scatter_chart(false_sales.rename(columns={"売上単価": "単価"}).append(false_purchase.rename(columns={"仕入単価": "単価"}))[["単価", "判定"]])

    # 5. 月別のFALSE判定件数推移（棒グラフ）
    st.subheader("月別のFALSE判定件数推移")
    sales_df["伝票日付"] = pd.to_datetime(sales_df["伝票日付"], format='%Y%m%d')
    purchase_df["伝票日付"] = pd.to_datetime(purchase_df["伝票日付"], format='%Y%m%d')

    false_sales_monthly = false_sales.groupby(false_sales["伝票日付"].dt.strftime('%Y-%m'))["判定"].count()
    false_purchase_monthly = false_purchase.groupby(false_purchase["伝票日付"].dt.strftime('%Y-%m'))["判定"].count()

    st.bar_chart(false_sales_monthly.rename("売上").to_frame().join(false_purchase_monthly.rename("仕入").to_frame()))