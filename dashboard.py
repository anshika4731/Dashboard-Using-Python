import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# Load dataset
df = pd.read_csv("Dashboard data.csv")  

# Check for missing values
df.fillna({"Sale": 0, "Cost": 0}, inplace=True)  

# Ensure 'Order Date' exists
if 'Order Date' not in df.columns:
    raise KeyError("The 'Order Date' column is missing from the dataset.")

# Convert 'Order Date' to datetime format, handling errors
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

# Drop rows where 'Order Date' couldn't be converted
df = df.dropna(subset=['Order Date'])

# Extract Year, Month, and Week only if conversion is successful
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.to_period('M')  # YYYY-MM format
df['Week'] = df['Order Date'].dt.to_period('W')  # Week number

# Remove duplicates
df = df.drop_duplicates()

# Add Profit column if Revenue and Cost exist
if "Sales" in df.columns and "Cost" in df.columns:
    df["Profit"] = df["Sales"] - df["Cost"]

# Convert date column to datetime 
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])

# Check for and remove negative values
df = df[df["Sales"] >= 0]

# Save cleaned dataset
df.to_csv("Dashboard data.csv", index=False)

# Display first few rows
print(df.head())

# --- Time-based Insights ---
fig, ax = plt.subplots(3, 1, figsize=(12, 12))

timeframes = ['Year', 'Month', 'Week']
titles = ['Yearly Sales and Profit', 'Monthly Sales and Profit', 'Weekly Sales and Profit']

for i, timeframe in enumerate(timeframes):
    grouped = df.groupby(timeframe).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    grouped.plot(x=timeframe, y=['Sales', 'Profit'], kind='line', ax=ax[i], marker='o')
    ax[i].set_title(titles[i])
    ax[i].set_ylabel('Amount')
    ax[i].grid()

plt.tight_layout()
plt.show()

# --- Product Performance ---
top_products = df.groupby('Product Name')['Sales'].sum().nlargest(5).reset_index()
plt.figure(figsize=(10, 5))
sns.barplot(data=top_products, x='Sales', y='Product Name', palette='viridis')
plt.title("Top 5 Best-Selling Products by Revenue")
plt.xlabel("Total Sales")
plt.ylabel("Product Name")
plt.show()

# Profit Margins per Product
product_profit_margin = df.groupby('Product Name')['Profit'].sum().nlargest(5).reset_index()
plt.figure(figsize=(10, 5))
sns.barplot(data=product_profit_margin, x='Profit', y='Product Name', palette='coolwarm')
plt.title("Top 5 Products by Profit Margin")
plt.xlabel("Total Profit")
plt.ylabel("Product Name")
plt.show()

# --- Regional Insights ---
region_sales = df.groupby('Region')['Sales'].sum().reset_index()
plt.figure(figsize=(10, 5))
sns.barplot(data=region_sales, x='Region', y='Sales', palette='Blues')
plt.title("Sales Performance Across Regions")
plt.xlabel("Region")
plt.ylabel("Total Sales")
plt.show()

# --- Product vs. Region Analysis ---
product_region = df.groupby(['Region', 'Product Name'])['Sales'].sum().reset_index()
plt.figure(figsize=(12, 6))
sns.barplot(data=product_region, x='Region', y='Sales', hue='Product Name', dodge=True)
plt.title("Product Sales Across Regions")
plt.xlabel("Region")
plt.ylabel("Total Sales")
plt.legend(title='Product', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()

# --- Streamlit Dashboard ---

st.set_page_config(page_title="Dashboard!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Dashboard Data")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"/Users/anshikasaini/Desktop/AnshikaSaini")
    df = pd.read_csv("Dashboard data.csv", encoding = "ISO-8859-1")

column1, column2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the Minimum and Maximum Date
startdate = pd.to_datetime(df["Order Date"]).min()
enddate = pd.to_datetime(df["Order Date"]).max()

with column1:
    date1 = pd.to_datetime(st.date_input("Start Date", startdate))

with column2:
    date2 = pd.to_datetime(st.date_input("End Date", enddate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
# Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for State

state = st.sidebar.multiselect("Pick your State", df["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df["State"].isin(state)]

# Create for City
city = st.sidebar.multiselect("Pick the City",df3["City"].unique())

# Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with column1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]], template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with column2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

column1, column2 = st.columns((2))
with column1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Purples"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv", help = 'Click here to download the data as a CSV file')

with column2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Greens"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
        
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')


# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")