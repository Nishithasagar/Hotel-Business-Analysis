import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hotel Business Analysis",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM THEME
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF9F2;
        color: #263238;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .hotel-hero {
        width: 100%;
        box-sizing: border-box;
        background: linear-gradient(135deg, #7B4B2A, #A66A3F);
        border-radius: 18px;
        padding: 42px 35px;
        margin: 20px 0 28px 0;
        text-align: center;
        box-shadow: 0 8px 20px rgba(30, 55, 80, 0.18);
    }

    .hotel-hero-title {
        color: white !important;
        font-size: 36px !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        margin: 0 !important;
    }

    .hotel-hero-subtitle {
        color: white !important;
        font-size: 21px !important;
        font-weight: 600 !important;
        margin: 18px 0 0 0 !important;
    }

    .hotel-hero-description {
        color: #EAF3F8 !important;
        font-size: 15px !important;
        margin: 12px 0 0 0 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #F5EDE2;
        border-right: 1px solid #E2D5C5;
    }

    .sidebar-project-title {
        color: #26384A;
        font-size: 24px;
        font-weight: 700;
        margin: 10px 0 18px 0;
    }

    .sidebar-section-title {
        color: #26384A;
        font-size: 18px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .sidebar-item {
        color: #374957;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 10px;
    }

    .sidebar-label {
        font-weight: 700;
        color: #26384A;
    }

    .sidebar-divider {
        border-top: 1px solid #D2D9DF;
        margin: 20px 0;
    }

    h2 {
        color: #294F6F !important;
        font-weight: 700 !important;
    }

    h3 {
        color: #315F7D !important;
        font-weight: 650 !important;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E0E5EA;
        border-radius: 10px;
        padding: 15px 17px;
        box-shadow: 0 2px 7px rgba(30, 50, 70, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: #637482 !important;
        font-size: 13px;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #294F6F !important;
        font-size: 27px;
        font-weight: 700;
    }

    .question {
        background-color: white;
        border-left: 4px solid #315F9A;
        border-radius: 7px;
        padding: 13px 16px;
        margin: 18px 0 10px 0;
        color: #294F6F;
        font-size: 18px;
        font-weight: 650;
    }

    .caption-box {
        background-color: #EEF2F6;
        border-radius: 7px;
        padding: 10px 14px;
        margin: 6px 0 10px 0;
        color: #586A76;
        font-size: 14px;
        line-height: 1.5;
    }

    .insight-box {
        background-color: #EAF2F8;
        border-left: 4px solid #315F9A;
        border-radius: 7px;
        padding: 12px 15px;
        margin: 6px 0 18px 0;
        color: #304A5B;
        font-size: 14.5px;
        line-height: 1.55;
    }

    .recommendation-box {
        background-color: white;
        border: 1px solid #E0E5EA;
        border-left: 4px solid #315F9A;
        border-radius: 8px;
        padding: 14px 17px;
        margin: 10px 0;
        box-shadow: 0 2px 6px rgba(30, 50, 70, 0.04);
    }

    .recommendation-box b {
        color: #294F6F;
        font-size: 16px;
    }

    .recommendation-box p {
        color: #586A76;
        margin-top: 6px;
    }

    div[data-testid="stPlotlyChart"] {
        background-color: white;
        border-radius: 8px;
        padding: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING AND CLEANING
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv("hotel_bookings_data.csv")

    # Handle missing values
    df["children"] = df["children"].fillna(0)
    df["agent"] = df["agent"].fillna(0)
    df["company"] = df["company"].fillna(0)
    df["city"] = df["city"].fillna("Unknown")

    # Remove duplicate rows
    df = df.drop_duplicates().copy()

    # Replace undefined meal values
    df["meal"] = df["meal"].replace("Undefined", "No Meal")

    # Remove negative ADR
    df = df[df["adr"] >= 0].copy()

    # Remove extreme ADR values using the same IQR rule as the EDA
    q1 = df["adr"].quantile(0.25)
    q3 = df["adr"].quantile(0.75)
    iqr = q3 - q1
    upper_limit = q3 + 1.5 * iqr
    df = df[df["adr"] <= upper_limit].copy()

    # Remove bookings with no guests
    df["total_guests"] = (
        df["adults"] + df["children"] + df["babies"]
    )

    df = df[df["total_guests"] > 0].copy()

    # Total stay
    df["total_stay"] = (
        df["stays_in_weekend_nights"]
        + df["stays_in_weekdays_nights"]
    )

    return df


df = load_data()


# ============================================================
month_order = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]


# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    """
    <div class="hotel-hero">
        <div class="hotel-hero-title">
            🏨 Hotel Business Analysis
        </div>
        <div class="hotel-hero-subtitle">
            Investigating Bookings and Cancellation Rates
        </div>
        <div class="hotel-hero-description">
            📊 Hotel Booking & Cancellation Analysis
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SHARED HELPERS
# ============================================================

def show_caption(text):
    st.markdown(
        f'<div class="caption-box"><b>Caption:</b> {text}</div>',
        unsafe_allow_html=True
    )


def show_insight(text):
    st.markdown(
        f'<div class="insight-box"><b>Insight:</b> {text}</div>',
        unsafe_allow_html=True
    )


# ============================================================
# PAGE: OVERVIEW
# ============================================================

def overview_page():
    st.header("📌 Project Overview")

    # ========================================================
    # KPI SUMMARY — RESPONDS TO DASHBOARD FILTERS
    # ========================================================
    st.markdown("### 📊 Dashboard KPIs")

    if filtered_df.empty:
        st.warning("No bookings match the selected filters.")
        return

    total_bookings = len(filtered_df)
    cancellation_rate = filtered_df["is_canceled"].mean() * 100
    avg_lead_time = filtered_df["lead_time"].mean()
    avg_adr = filtered_df["adr"].mean()
    city_share = (filtered_df["hotel"].eq("City Hotel").mean()) * 100

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    kpi1.metric(
        "Total Bookings",
        f"{total_bookings:,}"
    )

    kpi2.metric(
        "Cancellation Rate",
        f"{cancellation_rate:.1f}%"
    )

    kpi3.metric(
        "Average Lead Time",
        f"{avg_lead_time:.0f} days"
    )

    kpi4.metric(
        "Average ADR",
        f"{avg_adr:.2f}"
    )

    kpi5.metric(
        "City Hotel Share",
        f"{city_share:.1f}%"
    )

    if selected_hotel == "All" and selected_year == "All":
        st.caption("KPIs are calculated for all cleaned bookings.")
    else:
        hotel_label = selected_hotel
        year_label = selected_year
        st.caption(
            f"Current selection: Hotel Type = {hotel_label} | "
            f"Arrival Year = {year_label}"
        )

    st.markdown("### Business Problem")
    st.write(
        "The objective of this project is to analyze hotel booking "
        "behaviour and identify patterns that can help hotel management "
        "improve booking performance and reduce cancellation-related "
        "revenue loss."
    )

    st.markdown("### 🎯 Project Objectives")
    st.markdown(
        """
        - Analyze hotel booking patterns and booking volume.
        - Compare booking behaviour between City Hotel and Resort Hotel.
        - Identify factors associated with booking cancellations.
        - Analyze the relationship between lead time, stay duration and cancellations.
        - Identify seasonal booking patterns.
        - Provide practical recommendations to improve booking performance
          and reduce cancellation-related losses.
        """
    )

    st.markdown("### Business Questions")
    st.markdown(
        """
        1. Which hotel type is booked most frequently?
        2. Does the length of stay affect the cancellation rate?
        3. Does the time between booking and arrival affect the cancellation rate?
        """
    )

    st.markdown("### 📊 Dataset Overview")
    st.write(
        "The hotel booking dataset contains reservation-level information "
        "for City Hotel and Resort Hotel. It includes booking status, "
        "arrival details, stay duration, guest information, lead time, "
        "meal type, room information and pricing-related variables."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Records", f"{len(df):,}")
    col2.metric("Variables", f"{df.shape[1]}")
    col3.metric("Hotel Types", f"{df['hotel'].nunique()}")

    st.markdown("### Tools Used")
    st.write(
        "Python • Pandas • NumPy • Matplotlib • Seaborn • Plotly • Streamlit"
    )

    st.markdown("### EDA Process")
    st.info(
        "Data Loading → Data Cleaning → Exploratory Data Analysis "
        "→ Business Questions → Insights → Recommendations"
    )


# ============================================================
# PAGE: DATA PREPARATION
# ============================================================

def data_preparation_page():
    st.header("🧹 Data Preparation")

    st.write(
        "The dataset was cleaned before the EDA so that the analysis "
        "uses consistent and validated records."
    )

    st.subheader("Cleaning Steps")

    cleaning_steps = [
        ("Missing values", "Filled children, agent and company with 0; city with 'Unknown'."),
        ("Duplicate records", "Removed duplicate rows."),
        ("Meal values", "Replaced 'Undefined' with 'No Meal'."),
        ("Negative ADR", "Removed records with negative ADR."),
        ("Extreme ADR", "Removed ADR values above the IQR upper limit."),
        ("No-guest bookings", "Removed bookings where adults, children and babies were all zero."),
    ]

    for step, description in cleaning_steps:
        st.markdown(
            f'<div class="recommendation-box"><b>{step}</b>'
            f'<p>{description}</p></div>',
            unsafe_allow_html=True
        )

    st.subheader("Final Data Quality Validation")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows After Cleaning", f"{len(df):,}")
    col2.metric("Columns", f"{df.shape[1]:,}")
    col3.metric("Missing Values", f"{int(df.isnull().sum().sum()):,}")
    col4.metric("Duplicate Rows", f"{int(df.duplicated().sum()):,}")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Negative ADR",
        f"{int((df['adr'] < 0).sum()):,}"
    )

    col2.metric(
        "No-Guest Bookings",
        f"{int((df['total_guests'] == 0).sum()):,}"
    )

    col3.metric(
        "Maximum ADR",
        f"{df['adr'].max():.2f}"
    )

    st.subheader("Final Dataset")
    st.write(
        f"**Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns**"
    )

    st.caption(
        "The final cleaned dataset is the same dataset used for the "
        "dashboard EDA."
    )


# ============================================================
# PAGE: EDA
# ============================================================

def eda_page():
    st.header("🔍 Exploratory Data Analysis")
    st.caption(
        "The dashboard presents the same six charts used in the Python EDA."
    )

    # --------------------------------------------------------
    # 1. Booking Distribution by Hotel Type
    # --------------------------------------------------------

    st.markdown(
        '<div class="question">1. Booking Distribution by Hotel Type</div>',
        unsafe_allow_html=True
    )

    hotel_counts = (
        filtered_df["hotel"]
        .value_counts()
        .reset_index()
    )
    hotel_counts.columns = ["Hotel Type", "Bookings"]

    fig = px.bar(
        hotel_counts,
        x="Hotel Type",
        y="Bookings",
        text="Bookings",
        title="Booking Distribution by Hotel Type"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Hotel Type",
        yaxis_title="Number of Bookings"
    )

    st.plotly_chart(fig, use_container_width=True)

    show_caption(
        "The chart compares booking volume between City Hotel and Resort Hotel."
    )

    if not hotel_counts.empty:
        top_hotel = hotel_counts.iloc[0]
        show_insight(
            f"{top_hotel['Hotel Type']} has the highest booking volume "
            f"with {top_hotel['Bookings']:,} bookings."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # 2. Share of Bookings by Hotel Type
    # --------------------------------------------------------

    st.markdown(
        '<div class="question">2. Share of Bookings by Hotel Type</div>',
        unsafe_allow_html=True
    )

    booking_share = (
        filtered_df["hotel"]
        .value_counts(normalize=True)
        .mul(100)
        .reset_index()
    )
    booking_share.columns = ["Hotel Type", "Share"]

    fig = px.pie(
        booking_share,
        names="Hotel Type",
        values="Share",
        title="Share of Bookings by Hotel Type"
    )

    fig.update_traces(
        texttemplate="%{label}<br>%{percent}"
    )

    st.plotly_chart(fig, use_container_width=True)

    show_caption(
        "The chart shows the percentage contribution of each hotel type "
        "to the total bookings."
    )

    if not booking_share.empty:
        highest_share = booking_share.iloc[0]
        show_insight(
            f"{highest_share['Hotel Type']} contributes "
            f"{highest_share['Share']:.2f}% of the bookings."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # 3. Monthly Bookings by Hotel Type
    # --------------------------------------------------------

    st.markdown(
        '<div class="question">3. Monthly Bookings by Hotel Type</div>',
        unsafe_allow_html=True
    )

    monthly_bookings = (
        filtered_df
        .groupby(["hotel", "arrival_date_month"])
        .size()
        .reset_index(name="bookings")
    )

    monthly_bookings["arrival_date_month"] = pd.Categorical(
        monthly_bookings["arrival_date_month"],
        categories=month_order,
        ordered=True
    )

    monthly_bookings = monthly_bookings.sort_values(
        "arrival_date_month"
    )

    fig = px.line(
        monthly_bookings,
        x="arrival_date_month",
        y="bookings",
        color="hotel",
        markers=True,
        title="Monthly Bookings by Hotel Type"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Bookings"
    )

    st.plotly_chart(fig, use_container_width=True)

    show_caption(
        "The chart shows how booking volume changes across arrival months "
        "for each hotel type."
    )

    monthly_total = (
        filtered_df["arrival_date_month"]
        .value_counts()
        .reindex(month_order)
        .fillna(0)
    )

    if monthly_total.sum() > 0:
        busiest_month = monthly_total.idxmax()
        quietest_month = monthly_total.idxmin()

        show_insight(
            f"{busiest_month} has the highest booking volume, while "
            f"{quietest_month} has the lowest."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # 4. Cancellation Rate by Hotel Type
    # --------------------------------------------------------

    st.markdown(
        '<div class="question">4. Cancellation Rate by Hotel Type</div>',
        unsafe_allow_html=True
    )

    cancellation_by_hotel = (
        filtered_df
        .groupby("hotel")["is_canceled"]
        .mean()
        .mul(100)
        .reset_index(name="Cancellation Rate")
    )

    fig = px.bar(
        cancellation_by_hotel,
        x="hotel",
        y="Cancellation Rate",
        text="Cancellation Rate",
        title="Cancellation Rate by Hotel Type"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Hotel Type",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

    show_caption(
        "The chart compares the percentage of bookings cancelled "
        "between City Hotel and Resort Hotel."
    )

    if not cancellation_by_hotel.empty:
        highest_cancel = cancellation_by_hotel.loc[
            cancellation_by_hotel["Cancellation Rate"].idxmax()
        ]

        show_insight(
            f"{highest_cancel['hotel']} has the higher cancellation rate "
            f"at {highest_cancel['Cancellation Rate']:.2f}%."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # 5. Impact of Stay Duration on Cancellation Rate
    # --------------------------------------------------------

    st.markdown(
        '<div class="question">5. Impact of Stay Duration on Cancellation Rate</div>',
        unsafe_allow_html=True
    )

    stay_bins = [-1, 2, 4, 7, 14, float("inf")]
    stay_labels = [
        "0-2 nights",
        "3-4 nights",
        "5-7 nights",
        "8-14 nights",
        "15+ nights"
    ]

    stay_df = filtered_df.copy()

    stay_df["stay_duration_group"] = pd.cut(
        stay_df["total_stay"],
        bins=stay_bins,
        labels=stay_labels
    )

    stay_cancel = (
        stay_df
        .groupby(
            ["hotel", "stay_duration_group"],
            observed=True
        )["is_canceled"]
        .mean()
        .mul(100)
        .reset_index(name="Cancellation Rate")
    )

    fig = px.bar(
        stay_cancel,
        x="stay_duration_group",
        y="Cancellation Rate",
        color="hotel",
        barmode="group",
        text="Cancellation Rate",
        title="Impact of Stay Duration on Cancellation Rate"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Stay Duration",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

    show_caption(
        "The chart compares cancellation rates across different stay "
        "duration groups for each hotel type."
    )

    if not stay_cancel.empty:
        highest_stay = stay_cancel.loc[
            stay_cancel["Cancellation Rate"].idxmax()
        ]

        show_insight(
            f"The highest observed cancellation rate is "
            f"{highest_stay['Cancellation Rate']:.2f}% for the "
            f"{highest_stay['stay_duration_group']} stay group at "
            f"{highest_stay['hotel']}."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # 6. Impact of Lead Time on Cancellation Rate
    # --------------------------------------------------------

    st.markdown(
        '<div class="question">6. Impact of Lead Time on Cancellation Rate</div>',
        unsafe_allow_html=True
    )

    lead_bins = [-1, 30, 60, 90, 180, 365, float("inf")]
    lead_labels = [
        "0-30",
        "31-60",
        "61-90",
        "91-180",
        "181-365",
        "366+"
    ]

    lead_df = filtered_df.copy()

    lead_df["lead_time_group"] = pd.cut(
        lead_df["lead_time"],
        bins=lead_bins,
        labels=lead_labels
    )

    lead_cancel = (
        lead_df
        .groupby(
            ["hotel", "lead_time_group"],
            observed=True
        )["is_canceled"]
        .mean()
        .mul(100)
        .reset_index(name="Cancellation Rate")
    )

    fig = px.bar(
        lead_cancel,
        x="lead_time_group",
        y="Cancellation Rate",
        color="hotel",
        barmode="group",
        text="Cancellation Rate",
        title="Impact of Lead Time on Cancellation Rate"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Lead Time Group (Days)",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

    show_caption(
        "The chart compares cancellation rates across different booking "
        "lead-time groups for each hotel type."
    )

    if not lead_cancel.empty:
        highest_lead = lead_cancel.loc[
            lead_cancel["Cancellation Rate"].idxmax()
        ]

        show_insight(
            f"The highest observed cancellation rate is "
            f"{highest_lead['Cancellation Rate']:.2f}% for the "
            f"{highest_lead['lead_time_group']} lead-time group at "
            f"{highest_lead['hotel']}."
        )


# ============================================================
# PAGE: KEY FINDINGS
# ============================================================

def findings_page():
    st.header("💡 Key Findings")

    st.write(
        "The following findings summarize the main patterns identified "
        "through the six EDA charts."
    )

    st.subheader("📊 Booking Patterns")

    hotel_counts = filtered_df["hotel"].value_counts()
    total = len(filtered_df)

    if total > 0:
        top_hotel = hotel_counts.idxmax()
        top_count = hotel_counts.max()
        top_share = top_count / total * 100
    else:
        top_hotel = "N/A"
        top_count = 0
        top_share = 0

    st.markdown(
        f"""
        - **{top_hotel}** has the highest booking volume with
          **{top_count:,} bookings ({top_share:.2f}%)**.
        """
    )

    monthly_total = (
        filtered_df["arrival_date_month"]
        .value_counts()
        .reindex(month_order)
        .fillna(0)
    )

    if monthly_total.sum() > 0:
        busiest = monthly_total.idxmax()
        quietest = monthly_total.idxmin()
        st.markdown(
            f"- **{busiest}** has the highest booking volume, while "
            f"**{quietest}** has the lowest."
        )

    st.subheader("❌ Cancellation Patterns")

    cancellation_by_hotel = (
        filtered_df
        .groupby("hotel")["is_canceled"]
        .mean()
        .mul(100)
    )

    if not cancellation_by_hotel.empty:
        highest_cancel_hotel = cancellation_by_hotel.idxmax()
        highest_cancel_rate = cancellation_by_hotel.max()

        st.markdown(
            f"- **{highest_cancel_hotel}** has the higher cancellation "
            f"rate at approximately **{highest_cancel_rate:.2f}%**."
        )

    st.markdown(
        """
        - Cancellation behaviour varies across different stay-duration groups.
        - Cancellation rates vary across different booking lead-time groups.
        """
    )

    st.subheader("📌 Overall Takeaway")

    st.info(
        "The EDA indicates that hotel type, seasonal booking patterns, "
        "stay duration and booking lead time are useful dimensions for "
        "understanding booking and cancellation behaviour."
    )


# ============================================================
# PAGE: BUSINESS RECOMMENDATIONS
# ============================================================

def recommendations_page():
    st.header("💼 Business Recommendations")

    st.write(
        "The recommendations below translate the main EDA findings into "
        "practical actions for hotel management."
    )

    recommendations = [
        (
            "1. 📅 Prepare for Seasonal Demand",
            "Booking activity varies across arrival months. Management "
            "can use high-demand periods to plan room availability, "
            "staffing and operational resources in advance."
        ),
        (
            "2. 🏨 Improve Performance of the Less-Booked Hotel Type",
            "The hotel type with the smaller booking share can be supported "
            "with targeted promotions, seasonal packages and suitable offers "
            "during lower-demand periods."
        ),
        (
            "3. ❌ Manage Cancellation Risk",
            "Cancellation rates differ between hotel types. Management "
            "can monitor higher-risk booking segments when planning "
            "expected occupancy."
        ),
        (
            "4. ⏳ Monitor Long Lead-Time Bookings",
            "Cancellation rates vary across lead-time groups. Far-ahead "
            "reservations can receive closer monitoring and timely "
            "confirmation reminders."
        ),
        (
            "5. 📊 Use Booking Patterns for Planning",
            "Booking volume, cancellation behaviour, stay duration and "
            "lead time can be considered together when planning room "
            "inventory and operational resources."
        ),
    ]

    for title, description in recommendations:
        st.markdown(
            f"""
            <div class="recommendation-box">
                <b>{title}</b>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.subheader("⭐ Priority Action")

    st.success(
        "Prioritize cancellation-risk monitoring for bookings made "
        "well in advance. This can help management plan expected "
        "occupancy more realistically and prepare for potential "
        "cancellations."
    )

    st.caption(
        "These recommendations are based on patterns identified through "
        "the EDA and should be treated as business actions to consider, "
        "not as proof of causal relationships."
    )


# ============================================================
# SIDEBAR — PROJECT INFORMATION, NAVIGATION & FILTERS
# ============================================================

st.sidebar.markdown(
    """
    <div class="sidebar-project-title">
        🏨 Hotel Business Analysis
    </div>

    <div class="sidebar-item">
        <span class="sidebar-label">Dataset:</span><br>
        Hotel Booking Dataset
    </div>

    <div class="sidebar-item">
        <span class="sidebar-label">Analysis:</span><br>
        Booking & Cancellation Analysis
    </div>

    <div class="sidebar-divider"></div>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# PAGE OBJECTS
# ------------------------------------------------------------

overview_pg = st.Page(
    overview_page,
    title="Overview",
    icon="📌",
    url_path="overview"
)

data_prep_pg = st.Page(
    data_preparation_page,
    title="Data Preparation",
    icon="🧹",
    url_path="data-preparation"
)

eda_pg = st.Page(
    eda_page,
    title="EDA",
    icon="🔍",
    url_path="eda"
)

findings_pg = st.Page(
    findings_page,
    title="Key Findings",
    icon="💡",
    url_path="key-findings"
)

recommendations_pg = st.Page(
    recommendations_page,
    title="Business Recommendations",
    icon="💼",
    url_path="business-recommendations"
)

pages = {
    "Project": [overview_pg, data_prep_pg],
    "Analysis": [eda_pg, findings_pg, recommendations_pg],
}

# Hide Streamlit's automatic navigation.
selected_page = st.navigation(pages, position="hidden")

# ------------------------------------------------------------
# CUSTOM SIDEBAR NAVIGATION
# ------------------------------------------------------------

st.sidebar.markdown(
    '<div class="sidebar-section-title">📍 Project</div>',
    unsafe_allow_html=True
)

st.sidebar.page_link(
    overview_pg,
    label="Overview",
    icon="📌"
)

st.sidebar.page_link(
    data_prep_pg,
    label="Data Preparation",
    icon="🧹"
)

st.sidebar.markdown(
    '<div class="sidebar-section-title">📊 Analysis</div>',
    unsafe_allow_html=True
)

st.sidebar.page_link(
    eda_pg,
    label="EDA",
    icon="🔍"
)

st.sidebar.page_link(
    findings_pg,
    label="Key Findings",
    icon="💡"
)

st.sidebar.page_link(
    recommendations_pg,
    label="Business Recommendations",
    icon="💼"
)

# ------------------------------------------------------------
# DASHBOARD FILTERS
# ------------------------------------------------------------

st.sidebar.markdown(
    '<div class="sidebar-divider"></div>',
    unsafe_allow_html=True
)

st.sidebar.markdown(
    '<div class="sidebar-section-title">🔎 Dashboard Filters</div>',
    unsafe_allow_html=True
)

hotel_options = ["All"] + sorted(
    df["hotel"].dropna().unique().tolist()
)

selected_hotel = st.sidebar.selectbox(
    "🏨 Hotel Type",
    hotel_options
)

year_options = ["All"] + sorted(
    df["arrival_date_year"].unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "📅 Arrival Year",
    year_options
)

filtered_df = df.copy()

if selected_hotel != "All":
    filtered_df = filtered_df[
        filtered_df["hotel"] == selected_hotel
    ]

if selected_year != "All":
    filtered_df = filtered_df[
        filtered_df["arrival_date_year"] == selected_year
    ]

# Run the selected page only after filters have been prepared.
selected_page.run()

