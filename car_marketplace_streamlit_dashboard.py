import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

st.set_page_config(page_title="Car Marketplace Dashboard", layout="wide")

# ----------------------
# Load Data
# ----------------------
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

st.sidebar.header("Upload Data")
upload_option = st.sidebar.radio("Data Source", ["Upload CSV", "Load from Local File"])

if upload_option == "Upload CSV":
    file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
    if file is not None:
        df = load_data(file)
    else:
        df = None
else:
    file_path = st.sidebar.text_input("Enter local file path", placeholder="e.g., C:/path/to/file.csv")
    if file_path and file_path.endswith('.csv'):
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            st.sidebar.error("File not found. Check the path.")
            df = None
    else:
        df = None

## read data from local file
file_path = "C:\\Users\\RodahNambuyaChepkori\\Documents\\Skillup\\PROJECT 101\\Notebooks\\car_listings_2.csv"
df = pd.read_csv(file_path)


if df is not None:

    # ----------------------
    # Data Cleaning
    # ----------------------
    df['asking_price'] = pd.to_numeric(df['asking_price'], errors='coerce')
    df['views_count'] = pd.to_numeric(df['views_count'], errors='coerce')
    df['clicks_count'] = pd.to_numeric(df['clicks_count'], errors='coerce')
    df['mileage'] = pd.to_numeric(df['mileage'], errors='coerce')

    df['CTR'] = df['clicks_count'] / df['views_count']

    # ----------------------
    # Sidebar Filters
    # ----------------------
    st.sidebar.header("Filters")

    make_filter = st.sidebar.multiselect("Select Make", df['make_name'].dropna().unique())
    fuel_filter = st.sidebar.multiselect("Fuel Type", df['fuel_type'].dropna().unique())
    location_filter = st.sidebar.multiselect("Location", df['location_name'].dropna().unique())

    price_min, price_max = st.sidebar.slider(
        "Price Range",
        int(df['asking_price'].min()),
        int(df['asking_price'].max()),
        (int(df['asking_price'].min()), int(df['asking_price'].max()))
    )

    filtered_df = df.copy()

    if make_filter:
        filtered_df = filtered_df[filtered_df['make_name'].isin(make_filter)]

    if fuel_filter:
        filtered_df = filtered_df[filtered_df['fuel_type'].isin(fuel_filter)]

    if location_filter:
        filtered_df = filtered_df[filtered_df['location_name'].isin(location_filter)]

    filtered_df = filtered_df[
        (filtered_df['asking_price'] >= price_min) &
        (filtered_df['asking_price'] <= price_max)
    ]

    # ----------------------
    # KPIs
    # ----------------------
    st.title("🚗 Car Marketplace Dashboard")

    st.title("📊 Overview")

    col1, col2, col3, col4 = st.columns(4)     

    col1.metric("Total Listings", len(filtered_df))
    col2.metric("Avg Price", f"{filtered_df['asking_price'].mean():,.0f}")
    col3.metric("Total Views", int(filtered_df['views_count'].sum()))
    col4.metric("Avg CTR", f"{filtered_df['CTR'].mean():.2%}")

    # ----------------------
    # Price Distribution
    # ----------------------
    st.title("🚘 Market Insights")
    st.subheader("Price Distribution")
    fig_price = px.histogram(filtered_df, x="asking_price", nbins=50)
    st.plotly_chart(fig_price, use_container_width=True)

    # ----------------------
    # Price vs Mileage
    # ----------------------
    st.subheader("Price vs Mileage")
    fig_scatter = px.scatter(filtered_df, x="mileage", y="asking_price", color="make_name")
    st.plotly_chart(fig_scatter, use_container_width=True)

    #----------------------
    # Make vs Price
    #----------------------
    st.subheader("Price by Make")
    fig1 = px.box(filtered_df, x='make_name', y='asking_price') # fig1 = px.box(filtered_df, x='model_name', y='asking_price')
    st.plotly_chart(fig1, use_container_width=True)
    

    # ----------------------
    # Top Makes
    # ----------------------
    st.subheader("Top Car Makes")
    make_counts = filtered_df['make_name'].value_counts().reset_index()
    make_counts.columns = ['make_name', 'count']
    fig_make = px.bar(make_counts.head(10), x='make_name', y='count')
    st.plotly_chart(fig_make, use_container_width=True)

    # ----------------------
    # Engagement Analysis
    # ----------------------

    st.title("👀 Engagement Analysis")

    # ctr_make = filtered_df.groupby('make_name')['CTR'].mean().reset_index()
    # fig = px.bar(ctr_make, x='make_name', y='CTR')
    # st.plotly_chart(fig, use_container_width=True)
    st.subheader("CTR by Make")
    ctr_model = filtered_df.groupby('model_name')['CTR'].mean().reset_index().sort_values(by='CTR', ascending=False).head(10)
    fig2 = px.bar(ctr_model, x='model_name', y='CTR')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Top Viewed Cars")
    top_views = filtered_df.sort_values(by='views_count', ascending=False).head(10)
    fig_views = px.bar(top_views, x='display_name', y='views_count')
    st.plotly_chart(fig_views, use_container_width=True)

    st.subheader("Top Clicked Cars")
    top_clicks = filtered_df.sort_values(by='clicks_count', ascending=False).head(10)
    fig_clicks = px.bar(top_clicks, x='display_name', y='clicks_count')
    st.plotly_chart(fig_clicks, use_container_width=True)

        # ----------------------
    # PAGE: DEALS
    # ----------------------

    st.title("💸 Deals & Best Cars")
    deals = filtered_df.copy()
    deals['deal_score'] = deals['discount_percentage'].fillna(0) * deals['CTR'].fillna(0)

    best_deals = deals.sort_values(by='deal_score', ascending=False).head(10)
    st.subheader("🔥 Best Deals")
    st.dataframe(best_deals[['display_name','asking_price','discount_percentage','CTR','deal_score']])

    fig = px.scatter(deals, x='discount_percentage', y='CTR')
    st.plotly_chart(fig, use_container_width=True)


    # ----------------------
    # Discount Analysis
    # ----------------------
    st.subheader("Discount Impact")
    discount_df = filtered_df.dropna(subset=['discount_percentage'])

    if not discount_df.empty:
        fig_discount = px.scatter(discount_df, x='discount_percentage', y='views_count')
        st.plotly_chart(fig_discount, use_container_width=True)
    else:
        st.info("No discount data available")

    # ----------------------
    # Location Analysis
    # ----------------------
    st.subheader("Listings by Location")
    location_counts = filtered_df['location_name'].value_counts().reset_index()
    location_counts.columns = ['location_name', 'count']
    fig_location = px.bar(location_counts.head(10), x='location_name', y='count')
    st.plotly_chart(fig_location, use_container_width=True)

    # ----------------------
    # Seller Analysis
    # ----------------------
    st.subheader("Seller Type Distribution")
    seller_counts = filtered_df['seller_type_display'].value_counts().reset_index()
    seller_counts.columns = ['seller_type', 'count']
    fig_seller = px.pie(seller_counts, names='seller_type', values='count')
    st.plotly_chart(fig_seller, use_container_width=True)

    # ----------------------
    # Price Prediction
    # ----------------------

    st.title("🤖 Price Prediction Model")

    model_df = filtered_df[['asking_price','mileage','engine_size','year']].dropna()
        

    if len(model_df) > 50:
            X = model_df[['mileage','engine_size','year']]
            y = model_df['asking_price']

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

            model = RandomForestRegressor()
            model.fit(X_train, y_train)

            preds = model.predict(X_test)
            error = mean_absolute_error(y_test, preds)

            st.metric("Model MAE", f"{error:,.0f}")

            st.subheader("Predict Price")
            mileage = st.number_input("Mileage", value=50000)
            engine = st.number_input("Engine Size", value=1500)
            year = st.number_input("Year", value=2018)

            if st.button("Predict"):
                input_df = pd.DataFrame([[mileage, engine, year]], columns=['mileage','engine_size','year'])
                pred = model.predict(input_df)
                st.success(f"Estimated Price: {pred[0]:,.0f}")

    else:
            st.warning("Not enough data for ML model")

    # ----------------------
    # Raw Data
    # ----------------------
    st.subheader("Raw Data Preview")
    st.dataframe(filtered_df.head(100))

else:
    st.info("Please upload a CSV file to begin.")
