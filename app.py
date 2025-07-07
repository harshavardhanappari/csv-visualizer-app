import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CSV Visualizer", layout="wide")
st.title("📊 CSV Data Visualizer and Comparator")

uploaded_file = st.file_uploader("📁 Upload Your Main CSV File", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.markdown("### 👀 Data Preview:")
    st.dataframe(df)

    st.markdown("### 📈 Summary Statistics:")
    st.write(df.describe())

    cols = df.columns.tolist()
    if len(cols) >= 2:
        x_col = cols[0]
        y_col = cols[1]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Bar Chart (Main Dataset)")
            fig1, ax1 = plt.subplots()
            ax1.bar(df[x_col], df[y_col])
            st.pyplot(fig1)

        with col2:
            st.markdown("#### 🥧 Pie Chart (Main Dataset)")
            fig2, ax2 = plt.subplots()
            ax2.pie(df[y_col], labels=df[x_col], autopct="%1.1f%%")
            ax2.axis("equal")
            st.pyplot(fig2)

    # 🧮 Analysis for Main Dataset
    st.markdown("### 🧮 Data Analysis Tools for Main Dataset")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if numeric_cols:
        selected_col = st.selectbox(
            f"Select numeric column (Main Dataset)",
            numeric_cols,
            key="main_analysis"
        )

        b1, b2, b3 = st.columns(3)

        with b1:
            if st.button("🔼 Sort Asc (Main)"):
                st.dataframe(df.sort_values(by=selected_col))

        with b2:
            if st.button("🔽 Sort Desc (Main)"):
                st.dataframe(df.sort_values(by=selected_col, ascending=False))

        with b3:
            if st.button("🧮 Max & Min (Main)"):
                st.write(f"*Max in {selected_col}:* {df[selected_col].max()}")
                st.write(f"*Min in {selected_col}:* {df[selected_col].min()}")

        threshold = st.number_input(
            f"Main Dataset: Show rows where {selected_col} >", value=0.0, key="main_gt_input"
        )
        if st.button(f"🔍 Filter > {threshold} (Main)"):
            filtered = df[df[selected_col] > threshold]
            st.dataframe(filtered)
    else:
        st.info("⚠ No numeric columns found in main dataset.")

    st.markdown("### 📥 Download Processed Data")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name='processed_data.csv',
        mime='text/csv'
    )

    st.divider()

    # ✅ THEN comes comparison section
    compare_mode = st.checkbox("🔁 Compare with more datasets?")

    if compare_mode:
        st.markdown("### 📂 Upload One or More CSVs to Compare")
        additional_files = st.file_uploader(
            "Upload additional CSV files", type="csv", accept_multiple_files=True
        )

        if additional_files:
            all_datasets = [("Main Dataset", df)]
            for idx, file in enumerate(additional_files):
                df_extra = pd.read_csv(file)
                all_datasets.append((file.name, df_extra))

            st.markdown("## 📊 Side-by-Side Graph + Analysis")

            for name, data in all_datasets:
                if name == "Main Dataset":
                    continue  # Skip, already shown above

                st.markdown(f"## 📄 {name}")
                cols = data.columns.tolist()

                if len(cols) < 2:
                    st.warning(f"⚠ {name} does not have enough columns to plot.")
                    continue

                x_col = cols[0]
                y_col = cols[1]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📊 Bar Chart")
                    fig1, ax1 = plt.subplots()
                    ax1.bar(data[x_col], data[y_col])
                    st.pyplot(fig1)

                with col2:
                    st.markdown("#### 🥧 Pie Chart")
                    fig2, ax2 = plt.subplots()
                    ax2.pie(data[y_col], labels=data[x_col], autopct="%1.1f%%")
                    ax2.axis("equal")
                    st.pyplot(fig2)

                # 🧮 Analysis for additional datasets
                st.markdown("### 🧮 Data Analysis Tools")

                numeric_cols = data.select_dtypes(include=["number"]).columns.tolist()

                if numeric_cols:
                    selected_col = st.selectbox(
                        f"Select numeric column in {name}",
                        numeric_cols,
                        key=f"num_col_{name}"
                    )

                    b1, b2, b3 = st.columns(3)

                    with b1:
                        if st.button(f"🔼 Sort Asc ({name})", key=f"sort_asc_{name}"):
                            st.dataframe(data.sort_values(by=selected_col))

                    with b2:
                        if st.button(f"🔽 Sort Desc ({name})", key=f"sort_desc_{name}"):
                            st.dataframe(data.sort_values(by=selected_col, ascending=False))

                    with b3:
                        if st.button(f"🧮 Max & Min ({name})", key=f"maxmin_{name}"):
                            st.write(f"*Max in {selected_col}:* {data[selected_col].max()}")
                            st.write(f"*Min in {selected_col}:* {data[selected_col].min()}")

                    threshold = st.number_input(
                        f"{name}: Show rows where {selected_col} >", value=0.0, key=f"gt_input_{name}"
                    )
                    if st.button(f"🔍 Filter > {threshold} ({name})", key=f"gt_btn_{name}"):
                        filtered = data[data[selected_col] > threshold]
                        st.dataframe(filtered)
                else:
                    st.info(f"⚠ No numeric columns found in {name}.")

                if data.shape == df.shape:
                    try:
                        st.markdown(f"#### 🔍 Differences vs Main Dataset: {name}")
                        diff = df.compare(data)
                        st.dataframe(diff)
                    except:
                        st.info("⚠ Columns mismatch — cannot compare.")