import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import psycopg2
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ================ SETTINGS ================
st.set_page_config(
    page_title="📊 Real-Time Analytics", 
    layout="wide",
    page_icon="📊"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(145deg, #f0f2f6, #ffffff);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .header-text {
        color: #2c3e50;
        font-weight: 700 !important;
    }
    .stDataFrame {
        border-radius: 10px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 25px;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Auto-refresh every 10 seconds
st_autorefresh(interval=10 * 1000, key="dashboard_refresh")

# ================ DATA ================
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="postgres",
        user="postgres",
        password="pass1234"
    )

conn = get_connection()

# ================ HEADER ================
st.title("📊 Real-Time User Interaction Analytics Dashboard")
st.markdown("""
<div style="background:#f0f8ff;padding:15px;border-radius:10px;margin-bottom:20px">
    <p style="font-size:16px;color:#2c3e50;margin:0">Live dashboard showing real-time user behavior patterns and product interactions</p>
</div>
""", unsafe_allow_html=True)

# ================ TABS ================
tab1, tab2, tab3, tab4 = st.tabs([
    "🧭 Funnel Summary", 
    "🔁 Event Trends", 
    "📦 Purchases + Heatmap", 
    "💀 Churn Prediction"
])
# =======================
# 🔁 TAB 1: Event KPIs
# =======================
with tab1:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<h3 class="header-text">🔁 Event Funnel Metrics</h3>', unsafe_allow_html=True)
        
        try:
            query_event_counts = """
                SELECT event_type, SUM(event_count) AS total_count
                FROM event_trends
                GROUP BY event_type
                ORDER BY total_count DESC;
            """
            funnel_df = pd.read_sql(query_event_counts, conn)

            if not funnel_df.empty:
                cols = st.columns(len(funnel_df))
                for i, row in funnel_df.iterrows():
                    with cols[i]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="font-size:14px;color:#7f8c8d">{row['event_type'].capitalize()}</div>
                            <div style="font-size:24px;font-weight:700;color:#2c3e50">{int(row['total_count']):,}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No event data yet.")
        except Exception as e:
            st.error(f"Error loading metrics: {e}")

    with col2:
        st.markdown('<h3 class="header-text">👥 User & Product Stats</h3>', unsafe_allow_html=True)
        
        try:
            user_count = pd.read_sql("SELECT COUNT(DISTINCT user_id) FROM user_events_raw;", conn).iloc[0, 0]
            product_count = pd.read_sql("SELECT COUNT(DISTINCT product_id) FROM user_events_raw;", conn).iloc[0, 0]
            
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px">
                <div class="metric-card">
                    <div style="font-size:14px;color:#7f8c8d">Unique Users</div>
                    <div style="font-size:24px;font-weight:700;color:#3498db">{user_count:,}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size:14px;color:#7f8c8d">Unique Products</div>
                    <div style="font-size:24px;font-weight:700;color:#e74c3c">{product_count:,}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading users/products: {e}")

    st.divider()

    # Top Performers Section
    st.markdown('<h3 class="header-text">🏆 Top Performers</h3>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<h4 style="color:#2c3e50">👤 Top 5 Active Users</h4>', unsafe_allow_html=True)
        try:
            query_top_users = """
                SELECT user_id, COUNT(*) AS total_events
                FROM user_events_raw
                GROUP BY user_id
                ORDER BY total_events DESC
                LIMIT 5;
            """
            top_users = pd.read_sql(query_top_users, conn)
            st.dataframe(
                top_users.style
                .background_gradient(cmap='Blues', subset=['total_events'])
                .format({'total_events': '{:,}'}),
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error loading top users: {e}")

    with col4:
        st.markdown('<h4 style="color:#2c3e50">🛍️ Top 5 Purchased Products</h4>', unsafe_allow_html=True)
        try:
            query_top_products = """
                SELECT product_id, COUNT(*) AS purchase_count
                FROM user_events_raw
                WHERE event_type = 'purchase'
                GROUP BY product_id
                ORDER BY purchase_count DESC
                LIMIT 5;
            """
            top_products = pd.read_sql(query_top_products, conn)
            st.dataframe(
                top_products.style
                .background_gradient(cmap='Oranges', subset=['purchase_count'])
                .format({'purchase_count': '{:,}'}),
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error loading top products: {e}")
    
            

# =======================
# 📈 TAB 2: Event Trends
# =======================
with tab2:
    st.markdown('<h3 class="header-text">📈 Event Trends Over Time</h3>', unsafe_allow_html=True)
    
    try:
        query = """
            SELECT window_start, event_type, SUM(event_count) AS total_count
            FROM event_trends
            GROUP BY window_start, event_type
            ORDER BY window_start DESC
            LIMIT 100;
        """
        df = pd.read_sql(query, conn)

        if not df.empty:
            df['window_start'] = pd.to_datetime(df['window_start'])
            df = df.sort_values("window_start")
            
            # Interactive Plotly chart
            fig = px.area(
                df, 
                x="window_start", 
                y="total_count", 
                color="event_type",
                title="<b>Event Volume Over Time</b>",
                labels={"window_start": "Time", "total_count": "Event Count"},
                template="plotly_white"
            )
            fig.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available yet.")
    except Exception as e:
        st.error(f"Error loading trend chart: {e}")

        

# =======================
# 📦 TAB 3: Purchases + Heatmap
# =======================
with tab3:
    col5, col6 = st.columns([2, 3])
    
    with col5:
        st.markdown('<h3 class="header-text">📦 Recent Purchases</h3>', unsafe_allow_html=True)
        try:
            query = """
                SELECT user_id, product_id, timestamp
                FROM user_events_raw
                WHERE event_type = 'purchase'
                ORDER BY timestamp DESC
                LIMIT 10;
            """
            purchase_df = pd.read_sql(query, conn)
            if not purchase_df.empty:
                purchase_df['timestamp'] = pd.to_datetime(purchase_df['timestamp'])
                st.dataframe(
                    purchase_df.style.format({'timestamp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')}),
                    use_container_width=True
                )
            else:
                st.info("No purchases yet.")
        except Exception as e:
            st.error(f"Failed to load recent purchases: {e}")
    
    with col6:
        st.markdown('<h3 class="header-text">🔥 Interaction Heatmap</h3>', unsafe_allow_html=True)
        try:
            query = """
                SELECT 
                    EXTRACT(DOW FROM timestamp) AS day_of_week,
                    EXTRACT(HOUR FROM timestamp) AS hour_of_day,
                    COUNT(*) AS interaction_count
                FROM user_events_raw
                GROUP BY day_of_week, hour_of_day
                ORDER BY day_of_week, hour_of_day;
            """
            heatmap_df = pd.read_sql(query, conn)

            if not heatmap_df.empty:
                # Enhanced heatmap with day names
                days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                heatmap_df['day_name'] = heatmap_df['day_of_week'].map(lambda x: days[int(x)])
                
                pivot = heatmap_df.pivot_table(
                    index='day_name',
                    columns='hour_of_day',
                    values='interaction_count',
                    fill_value=0
                ).reindex(days)

                fig, ax = plt.subplots(figsize=(12, 4))
                sns.heatmap(pivot, cmap="YlOrRd", ax=ax, annot=True, fmt='g', linewidths=.5)
                ax.set_xlabel("Hour of Day", fontsize=10)
                ax.set_ylabel("Day of Week", fontsize=10)
                ax.set_title("User Activity Heatmap", pad=20)
                st.pyplot(fig)
            else:
                st.info("Not enough data for heatmap.")
        except Exception as e:
            st.error(f"Heatmap error: {e}")


# ===========================
# 🛑 TAB 4: At-Risk Users
# ===========================
tab4 = st.tabs(["🛑 At-Risk Users"])[0]

with tab4:
    st.subheader("🛑 Users Predicted to Churn (Live)")

    try:
        query_churned = """
            SELECT user_id, num_views, num_adds
            FROM churn_predictions
            WHERE churned = TRUE
            ORDER BY user_id
            LIMIT 10;
        """
        churn_df = pd.read_sql(query_churned, conn)

        if not churn_df.empty:
            st.dataframe(churn_df, hide_index=True)
        else:
            st.info("No churned users detected yet.")
    except Exception as e:
        st.error(f"Failed to load churned users: {e}")
