import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- Page Setup ----------------
st.set_page_config(page_title="Dubai Real Estate Dashboard", layout="wide")
st.title("🏢 Dubai Real Estate Market Dashboard (Investor + Map Edition)")

# ---------------- Upload CSV/Excel ----------------
uploaded_file = st.file_uploader("Upload your Dubai property CSV or Excel file", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---------------- Check Required Columns ----------------
    required_cols = ["Area", "Project", "Size (Sqft)", "Total Price", "Year", "Latitude", "Longitude"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV/Excel must contain columns: {', '.join(required_cols)}")
    else:
        # ---------------- Calculations ----------------
        df["Price per Sqft"] = df["Total Price"] / df["Size (Sqft)"]

        # ---------------- Filters ----------------
        st.sidebar.header("Filters")
        selected_areas = st.sidebar.multiselect("Select Areas", options=df["Area"].unique(), default=df["Area"].unique())
        selected_years = st.sidebar.multiselect("Select Years", options=df["Year"].unique(), default=df["Year"].unique())
        df_filtered = df[df["Area"].isin(selected_areas) & df["Year"].isin(selected_years)]

        # ---------------- KPI CARDS ----------------
        st.subheader("🔹 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Average Price per Sqft", f"{df_filtered['Price per Sqft'].mean():,.0f} AED")
        col2.metric("Highest Area Price", f"{df_filtered.groupby('Area')['Price per Sqft'].mean().max():,.0f} AED")
        col3.metric("Lowest Area Price", f"{df_filtered.groupby('Area')['Price per Sqft'].mean().min():,.0f} AED")
        col4.metric("Total Projects", df_filtered['Project'].nunique())

        # ---------------- Bar Chart: Avg Price per Area ----------------
        st.subheader("📊 Average Price per Sqft by Area")
        area_bar = df_filtered.groupby("Area")["Price per Sqft"].mean().reset_index()
        fig_bar = px.bar(
            area_bar, x="Area", y="Price per Sqft",
            color="Price per Sqft", text="Price per Sqft",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ---------------- Top 5 Expensive & Affordable Areas ----------------
        st.subheader("🏆 Top 5 Expensive Areas")
        st.dataframe(area_bar.sort_values(by="Price per Sqft", ascending=False).head(5).reset_index(drop=True))
        st.subheader("💰 Top 5 Affordable Areas")
        st.dataframe(area_bar.sort_values(by="Price per Sqft", ascending=True).head(5).reset_index(drop=True))

        # ---------------- Project Table ----------------
        st.subheader("🏗 Project Details Table")
        df_table = df_filtered.copy()
        df_table["Price per Sqft Range"] = pd.cut(df_table["Price per Sqft"], bins=[0,1000,2000,3000,5000], labels=["Low","Medium","High","Premium"])
        st.dataframe(df_table[['Area', 'Project', 'Size (Sqft)', 'Total Price', 'Price per Sqft', 'Price per Sqft Range', 'Year']])

        # ---------------- Scatter Plot: Size vs Total Price ----------------
        st.subheader("📈 Scatter Plot: Size vs Total Price")
        fig_scatter = px.scatter(
            df_filtered, x="Size (Sqft)", y="Total Price", color="Price per Sqft Range",
            hover_data=["Area", "Project", "Price per Sqft"], size="Price per Sqft",
            color_discrete_map={"Low":"green","Medium":"orange","High":"blue","Premium":"purple"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # ---------------- Map View ----------------
        st.subheader("🗺 Dubai Projects Map")
        fig_map = px.scatter_mapbox(
            df_filtered, lat="Latitude", lon="Longitude", hover_name="Project",
            hover_data=["Area", "Price per Sqft", "Total Price"], color="Price per Sqft Range",
            size="Price per Sqft", zoom=10, height=600,
            color_discrete_map={"Low":"green","Medium":"orange","High":"blue","Premium":"purple"}
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)