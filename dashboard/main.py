import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency 
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value":"sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
        
    return daily_orders_df

def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({
        "payment_value":"sum"
    })
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
        "payment_value" : "sum"
    }, inplace=True)

    return sum_spend_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

    return sum_order_items_df

def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    most_common_score = review_scores.idxmax()

    return review_scores, most_common_score

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

    return bystate_df, most_common_state

def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    most_common_status = order_status_df.idxmax()

    return order_status_df, most_common_status

all_df = pd.read_csv("C:/Users/ACER/OneDrive/Documents/Dokumen Kuliah/Pemrograman di luar Pembelajaran/Dicoding/Analisis Data dengan Python/Real Project/submission/data/all_data.csv")

datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    st.image("C:/Users/ACER/OneDrive/Documents/Dokumen Kuliah/Pemrograman di luar Pembelajaran/Dicoding/Analisis Data dengan Python/Real Project/submission/dashboard/logo.png")

    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & (all_df["order_approved_at"] <= str(end_date))]


daily_orders_df = create_daily_orders_df(main_df)
sum_spend_df = create_sum_spend_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
score_df = review_score_df(main_df)
bystate_df = create_bystate_df(main_df)
order_status = create_order_status(main_df)

st.header('Project E-Commerce (Dean) :sparkles:')

# Penjualan Harian Perusahaan dan Revenue
st.subheader("Penjualan Harian Perusahaan dan Revenue")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color = "#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Membuat Visualisasi produk terlaris dan paling tidak laris 
st.header('Produk terlaris dan paling tidak laris')
col1, col2 = st.columns(2)

with col1:
    total_items  = sum_order_items_df['product_count'].sum()
    st.markdown(f"Total Items : **{total_items}**")
    
with col2: 
    avg_items = sum_order_items_df['product_count'].mean()
    st.markdown(f"Average Items : **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9","#D3D3D3","#D3D3D3","#D3D3D3","#D3D3D3"]

sns.barplot(x='product_count', y='product_category_name_english', data= sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel('Total Penjualan')
ax[0].set_title('Produk Terlaris', loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x='product_count', y='product_category_name_english', data= sum_order_items_df.sort_values(by='product_count', ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('Jumlah Penjualan', fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].set_title('Produk paling tidak laris', loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Membuat Visualisasi Kepuasan Pelanggan (Review)
st.subheader('Review Score')
col1, col2 = st.columns(2)

with col1:
    avg_review_score = score_df[0].mean()
    st.markdown(f'Average Review Score : **{avg_review_score}**')
    
with col2:
    most_common_review_score = score_df[1]
    st.markdown(f'Most Common Review Score : **{most_common_review_score}**')


fig, ax = plt.subplots(figsize=(12, 6))

# Fix: Use score_df[0].index for the 'order' parameter, not the function.
sns.barplot(
    x=score_df[0].index, 
    y=score_df[0].values, 
    order=score_df[0].index,  # Use the index of the review scores
    palette=["#068DA9" if score == most_common_review_score else "#D3D3D3" for score in score_df[0].index]
)

plt.title('Tingkat Kepuasan Pelanggan (Review)', fontsize=15)
plt.xlabel('Rating')
plt.ylabel('Count')
plt.xticks(fontsize=12)
st.pyplot(fig)

st.caption('Copyright (C) Dean G. P. 2024')