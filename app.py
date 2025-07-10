import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 CSV Visualizer & Comparator")

st.markdown("### Upload the Main Dataset")
main_file = st.file_uploader("Choose the main CSV file", type="csv")

compare_more = st.checkbox("Compare more datasets")
other_files = []
if compare_more:
    other_files = st.file_uploader("Upload other CSV files", type="csv", accept_multiple_files=True)

# ✅ Efficient large CSV reader
@st.cache_data
def read_large_csv(f):
    chunks = []
    try:
        for chunk in pd.read_csv(f, chunksize=100_000, dtype_backend="pyarrow"):
            chunks.append(chunk)
        return pd.concat(chunks, ignore_index=True)
    except Exception as e:
        return f"Error: {e}"

def show_dataset_ui(file, label):
    st.markdown(f"## {label}")

    df = read_large_csv(file)
    if isinstance(df, str):  # Error handling
        st.error(f"Failed to read {label}: {df}")
        return

    st.write("### Dataset Preview", df.head())

    cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(cols) < 1:
        st.warning("No numeric columns to visualize.")
        return

    col1, col2 = st.columns(2)
    with col1:
        x_col = st.selectbox(f"Select X-axis (categorical)", df.columns, key=label + "_x")
    with col2:
        y_col = st.selectbox(f"Select Y-axis (numeric)", cols, key=label + "_y")

    if x_col and y_col:
        col1, col2 = st.columns(2)

        with col1:
            if df[x_col].nunique() <= 30:
                fig1, ax1 = plt.subplots()
                ax1.bar(df[x_col], df[y_col])
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig1)
            else:
                st.info(f"⚠ Too many unique values in '{x_col}' to display a clean bar chart.")

        with col2:
            if df[x_col].nunique() <= 30:
                try:
                    fig2, ax2 = plt.subplots()
                    ax2.pie(df[y_col], labels=df[x_col], autopct="%1.1f%%")
                    ax2.axis("equal")
                    st.pyplot(fig2)
                except Exception as e:
                    st.warning(f"⚠ Pie chart error: {e}")
            else:
                st.info(f"⚠ Too many unique values in '{x_col}' for a meaningful pie chart.")

    st.markdown("### 📌 Data Analysis Tools")
    st.write(f"🔢 Number of rows: {df.shape[0]}")
    st.write(f"📐 Number of columns: {df.shape[1]}")
    st.write("📊 Basic statistics:")
    st.write(df.describe())

    st.markdown("### 🔽 Sorting & Filtering")
    sort_col = st.selectbox("Sort by column", df.columns, key=label + "_sort")
    if sort_col:
        sort_order = st.radio("Order", ["Ascending", "Descending"], key=label + "_order")
        st.write(df.sort_values(by=sort_col, ascending=(sort_order == "Ascending")))

    st.markdown("### 🔍 Find values above a threshold")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    num_col = st.selectbox("Choose numeric column", numeric_cols, key=label + "_numfilter")
    if num_col:
        threshold = st.number_input("Enter threshold value", key=label + "_threshold")
        filtered = df[df[num_col] > threshold]
        st.write(filtered)

    st.markdown("### 📈 Min & Max Finder")
    min_col = st.selectbox("Column for Min/Max", numeric_cols, key=label + "_minmax")
    if min_col:
        st.write("🔽 Minimum Value:")
        st.write(df[df[min_col] == df[min_col].min()])
        st.write("🔼 Maximum Value:")
        st.write(df[df[min_col] == df[min_col].max()])

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(f"⬇ Download {label}", csv, file_name=f"{label}.csv", mime="text/csv")

# Show main dataset
if main_file:
    show_dataset_ui(main_file, "Main Dataset")

# Show comparison datasets
if other_files:
    for i, file in enumerate(other_files):
        show_dataset_ui(file, f"Dataset{i+1}")
