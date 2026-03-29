import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import urllib.request
import os

# --- Helper Functions ---
DATA_URL = "https://raw.githubusercontent.com/shricharan-ks/Retail-datasets/master/Online%20Retail.csv"

@st.cache_data
def load_and_clean_data():
    if not os.path.exists("RetailData.csv"):
        st.info("Downloading data...")
        try:
            urllib.request.urlretrieve(DATA_URL, "RetailData.csv")
            # Fix encoding
            with open("RetailData.csv", "r", encoding="ISO-8859-1") as f:
                content = f.read()
            with open("RetailData.csv", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            st.error(f"Error downloading data: {e}")
            return pd.DataFrame()

    try:
        df = pd.read_csv('RetailData.csv', encoding='utf-8', parse_dates=['InvoiceDate'], dtype={'InvoiceNo': str})
    except UnicodeDecodeError:
        df = pd.read_csv('RetailData.csv', encoding='ISO-8859-1', parse_dates=['InvoiceDate'], dtype={'InvoiceNo': str})

    df.dropna(subset=['Description', 'InvoiceNo'], inplace=True)
    df['Description'] = df['Description'].str.strip()
    df = df[~df['InvoiceNo'].str.contains('C')] # Remove cancellations
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    # Feature Engineering for Time Analysis
    df['Hour'] = df['InvoiceDate'].dt.hour
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    df['Month'] = df['InvoiceDate'].dt.month_name()
    
    # --- MEMORY SAFETY ---
    # Sample if dataset is too large
    if len(df) > 50000:
        df = df.sample(n=50000, random_state=42)
    
    return df

def encode_units(x):
    if x <= 0: return 0
    if x >= 1: return 1

@st.cache_data
def perform_mba(df_country, min_support, min_threshold):
    # 1. Filter Items Hard (Top 150) to prevent combinatorial explosion
    top_items = df_country['Description'].value_counts().head(150).index
    df_filtered = df_country[df_country['Description'].isin(top_items)]

    basket = (df_filtered.groupby(['InvoiceNo', 'Description'])['Quantity']
              .sum().unstack().reset_index().fillna(0)
              .set_index('InvoiceNo'))
    
    # Optimization: Convert to boolean immediately
    basket_encoded = basket.apply(lambda x: x > 0)
    
    basket_filtered = basket_encoded[(basket_encoded > 0).sum(axis=1) >= 2]
    
    if basket_filtered.empty:
        return pd.DataFrame()

    # 2. Cap max itemset length to 2 (Pairwise only)
    # 3. Use low_memory=True
    frequent_itemsets = apriori(basket_filtered, min_support=min_support, use_colnames=True, low_memory=True, max_len=2)
    
    if frequent_itemsets.empty:
        return pd.DataFrame()
        
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_threshold)
    rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x))
    rules['consequents'] = rules['consequents'].apply(lambda x: list(x))
    
    return rules

# --- Streamlit App ---
st.set_page_config(page_title="SegmentIQ: Retail Analytics", layout="wide", page_icon="🛒")

# Custom CSS for "Premium" look
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6; 
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    [data-testid="stMetricValue"] {
        font-weight: bold;
        color: #0068c9;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛒 SegmentIQ: Retail Analytics & Market Basket")
st.markdown("Unlock insights from your retail data with advanced association rules and interactive dashboards.")

with st.spinner("Processing Data..."):
    df = load_and_clean_data()

if df.empty:
    st.stop()

# --- Sidebar ---
st.sidebar.header("🔧 Configuration")
countries = sorted(df['Country'].unique())
default_country = 'United Kingdom' if 'United Kingdom' in countries else countries[0]
selected_country = st.sidebar.selectbox("Select Country", countries, index=countries.index(default_country))

df_country = df[df['Country'] == selected_country]

# --- Dashboard: Key Metrics ---
st.subheader(f"📊 Dashboard: {selected_country}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transactions", f"{df_country['InvoiceNo'].nunique():,}")
col2.metric("Total Products Sold", f"{df_country['StockCode'].nunique():,}")
col3.metric("Total Items Sold", f"{df_country['Quantity'].sum():,}")
col4.metric("Total Revenue", f"£{df_country['TotalPrice'].sum():,.2f}")

# --- Dashboard: Charts ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("##### 🏆 Top 10 Best Selling Products")
    top_products = df_country['Description'].value_counts().head(10).reset_index()
    top_products.columns = ['Product', 'Sales Count']
    fig_top = px.bar(top_products, x='Sales Count', y='Product', orientation='h', color='Sales Count', color_continuous_scale='Viridis')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_top, use_container_width=True)

with col_chart2:
    st.markdown("##### 📈 Revenue Trend (Daily)")
    daily_sales = df_country.groupby(df_country['InvoiceDate'].dt.date)['TotalPrice'].sum().reset_index()
    daily_sales.columns = ['Date', 'Revenue']
    fig_trend = px.line(daily_sales, x='Date', y='Revenue', markers=True, line_shape='spline')
    fig_trend.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_trend, use_container_width=True)

# --- Operational Insights ---
with st.expander("🕰️ Operational Insights (Heatmap)"):
    st.markdown("##### Sales Heatmap: Day of Week vs Hour")
    heatmap_data = df_country.groupby(['DayOfWeek', 'Hour'])['InvoiceNo'].nunique().reset_index()
    heatmap_data.columns = ['Day', 'Hour', 'Transactions']
    
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig_heat = px.density_heatmap(heatmap_data, x='Hour', y='Day', z='Transactions', 
                                  category_orders={'Day': days_order}, color_continuous_scale='Plasma')
    st.plotly_chart(fig_heat, use_container_width=True)


# --- Market Basket Analysis ---
st.divider()
st.subheader("🛍️ Product Recommender System (Market Basket Analysis)")

min_support = st.sidebar.slider("MBA: Min Support", 0.01, 0.1, 0.05, 0.01)
min_threshold = st.sidebar.slider("MBA: Min Lift Threshold", 0.5, 5.0, 1.0, 0.1)

with st.spinner(f"Running Apriori Algorithm for {selected_country}..."):
    rules = perform_mba(df_country, min_support, min_threshold)

if rules.empty:
    st.warning("No association rules found with the current parameters. Try lowering the support or lift threshold.")
else:
    # FIX 3: REMOVE SYMMETRIC / USELESS RULES
    rules = rules[rules['antecedents'] != rules['consequents']]
    
    # --- Recommender Interface ---
    st.info("Based on historical transaction data, customers who purchased X also purchased the following products with high confidence and lift.")

    # Get unique antecedents for selection
    all_antecedents = set()
    for item_list in rules['antecedents']:
        for item in item_list:
            all_antecedents.add(item)
    
    selected_product = st.selectbox("I am interested in buying...", sorted(list(all_antecedents)))
    
    # Filter rules where selected product is in antecedents
    recommendations = rules[rules['antecedents'].apply(lambda x: selected_product in x)].copy()
    
    if not recommendations.empty:
        # Sort by Lift to show best matches first
        recommendations.sort_values(by=['confidence', 'lift'], ascending=False, inplace=True)
        
        # FIX 2: SHOW ONLY TOP-3 RECOMMENDATIONS
        top_recommendations = recommendations.head(3)
        
        st.markdown(f"### 💡 Top Recommendations for **{selected_product}**")
        
        # FIX 5: ADD A SIMPLE RANKING STATEMENT (Top 1)
        top_rec = top_recommendations.iloc[0]
        rec_item = ', '.join(list(top_rec['consequents']))
        lift_val = top_rec['lift']
        st.success(f"Customers buying **{selected_product}** are **{lift_val:.1f}x** more likely to also buy **{rec_item}**.")
        
        # Display as cards
        for index, row in top_recommendations.iterrows():
            rec_text = ', '.join(list(row['consequents']))
            conf_text = f"{row['confidence']:.1%}"
            lift_text = f"{row['lift']:.2f}x"
            
            with st.container():
                st.markdown(f"""
                **{rec_text}**  
                Likelihood: `{conf_text}` | Market Strength: `{lift_text}`
                """)
                st.divider()

        # FIX 4: EXPLAIN CONFIDENCE & LIFT
        with st.expander("ℹ️ How to interpret these numbers?"):
            st.markdown("""
            **Likelihood (Confidence)**  
            → "Out of all purchases containing *X*, this % also contained *Y*"
            
            **Market Strength (Lift)**  
            → "How much more likely this pairing is compared to random chance"
            """)

    else:
        st.write("No strong recommendations found for this specific item based on current rules.")

    # --- Full Rules (Advanced) ---
    with st.expander("View All Association Rules (Advanced)"):
        st.dataframe(rules)
        csv = rules.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Rules as CSV",
            data=csv,
            file_name=f'market_basket_rules_{selected_country}.csv',
            mime='text/csv',
        )

# --- Footer ---
st.markdown("---")
st.caption("Powered by SegmentIQ Analytics Engine")
