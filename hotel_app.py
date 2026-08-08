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
# CUSTOM THEME / STYLING
# ============================================================

st.markdown("""
<style>

/* ----------------------------------------------------------
   Main App Background
---------------------------------------------------------- */

.stApp {
    background-color: #F5F7FA;
}


/* ----------------------------------------------------------
   Main Content
---------------------------------------------------------- */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}


/* ----------------------------------------------------------
   Main Title
---------------------------------------------------------- */

.main-title {
    color: #163A5F;
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 18px;
}


/* ----------------------------------------------------------
   Section Headers
---------------------------------------------------------- */

h1 {
    color: #163A5F !important;
}

h2 {
    color: #1F4E79 !important;
}

h3 {
    color: #1F4E79 !important;
}


/* ----------------------------------------------------------
   Sidebar
---------------------------------------------------------- */

section[data-testid="stSidebar"] {
    background-color: #163A5F;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

section[data-testid="stSidebar"] h2 {
    color: white !important;
}


/* ----------------------------------------------------------
   KPI Cards
---------------------------------------------------------- */

div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #D9E2EC;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(22, 58, 95, 0.08);
}

div[data-testid="stMetricLabel"] {
    color: #526777 !important;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #163A5F !important;
    font-weight: 700;
}


/* ----------------------------------------------------------
   Tabs
---------------------------------------------------------- */

button[data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
    color: #526777;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #163A5F !important;
}


/* ----------------------------------------------------------
   Question Boxes
---------------------------------------------------------- */

.question {
    background-color: white;
    border-left: 5px solid #2F6690;
    padding: 13px 16px;
    border-radius: 8px;
    margin-top: 15px;
    margin-bottom: 12px;
    color: #163A5F;
    font-size: 19px;
    font-weight: 650;
}


/* ----------------------------------------------------------
   Caption Boxes
---------------------------------------------------------- */

.caption-box {
    background-color: #EAF1F7;
    border-radius: 8px;
    padding: 11px 15px;
    margin-top: 8px;
    margin-bottom: 12px;
    color: #40566A;
    font-size: 14px;
}


/* ----------------------------------------------------------
   Insight Boxes
---------------------------------------------------------- */

.insight-box {
    background-color: #E7F1F8;
    border-left: 5px solid #2F6690;
    border-radius: 8px;
    padding: 13px 16px;
    margin-bottom: 18px;
    color: #243B53;
    font-size: 15px;
}


/* ----------------------------------------------------------
   Recommendation Boxes
---------------------------------------------------------- */

.recommendation-box {
    background-color: white;
    border-left: 5px solid #163A5F;
    border-radius: 8px;
    padding: 15px 18px;
    margin-bottom: 14px;
    box-shadow: 0 2px 7px rgba(22, 58, 95, 0.07);
}


/* ----------------------------------------------------------
   Info Boxes
---------------------------------------------------------- */

div[data-testid="stAlert"] {
    border-radius: 8px;
}


/* ----------------------------------------------------------
   Horizontal Line
---------------------------------------------------------- */

hr {
    border-color: #D9E2EC;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD AND CLEAN DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("hotel_bookings_data.csv")

    # Missing value handling
    df["children"] = df["children"].fillna(0)
    df["agent"] = df["agent"].fillna(0)
    df["company"] = df["company"].fillna(0)
    df["city"] = df["city"].fillna("Unknown")

    # Remove duplicate records
    df = df.drop_duplicates()

    # Replace Undefined meal category
    df["meal"] = df["meal"].replace(
        "Undefined",
        "No Meal"
    )

    # Remove negative ADR values
    df = df[df["adr"] >= 0].copy()

    # Calculate total guests
    df["total_guests"] = (
        df["adults"]
        + df["children"]
        + df["babies"]
    )

    # Remove bookings with no guests
    df = df[df["total_guests"] > 0].copy()

    # Calculate total stay
    df["total_stay"] = (
        df["stays_in_weekend_nights"]
        + df["stays_in_weekdays_nights"]
    )

    return df


df = load_data()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🏨 Hotel Business Analysis – Investigating Bookings and Cancellation Rates'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.markdown("## Filters")

st.sidebar.markdown(
    "Use the filters below to explore the hotel booking data."
)

st.sidebar.markdown("---")


hotel_options = [
    "All"
] + sorted(
    df["hotel"].dropna().unique().tolist()
)

selected_hotel = st.sidebar.selectbox(
    "Hotel Type",
    hotel_options
)


year_options = [
    "All"
] + sorted(
    df["arrival_date_year"].unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Arrival Year",
    year_options
)


# Apply filters
filtered_df = df.copy()

if selected_hotel != "All":

    filtered_df = filtered_df[
        filtered_df["hotel"] == selected_hotel
    ]


if selected_year != "All":

    filtered_df = filtered_df[
        filtered_df["arrival_date_year"] == selected_year
    ]


# Month order
month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


# ============================================================
# TABS
# ============================================================

overview_tab, dashboard_tab, eda_tab, insights_tab = st.tabs(
    [
        "📌 Project Overview",
        "📊 Dashboard",
        "🔍 EDA",
        "💡 Insights & Recommendations"
    ]
)


# ============================================================
# TAB 1 — PROJECT OVERVIEW
# ============================================================

with overview_tab:

    st.header("Project Overview")

    st.markdown("""
    ### Business Problem

    The objective of this project is to analyze hotel booking
    behaviour and identify patterns that can help hotel management
    improve booking performance and reduce cancellation-related
    revenue loss.
    """)

    st.markdown("### Business Questions")

    st.markdown("""
    1. Which hotel type is booked most frequently?
    2. Does the length of stay affect the cancellation rate?
    3. Does the time between booking and arrival affect the
       cancellation rate?
    """)

    st.markdown("### Dataset")

    st.markdown("""
    The dataset contains hotel booking information including:

    - Hotel type
    - Booking status
    - Arrival date
    - Stay duration
    - Lead time
    - Number of guests
    - ADR
    - Meal type
    - Customer and booking information
    """)

    st.markdown("### Tools Used")

    st.markdown("""
    **Python • Pandas • NumPy • Matplotlib • Seaborn • Plotly • Streamlit**
    """)

    st.markdown("### EDA Process")

    st.info(
        "Data Loading → Data Cleaning → Exploratory Data Analysis "
        "→ Business Questions → Insights → Recommendations"
    )

    st.markdown("### Data Quality Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Rows After Cleaning",
        f"{len(df):,}"
    )

    col2.metric(
        "Columns",
        f"{df.shape[1]:,}"
    )

    col3.metric(
        "Duplicate Rows",
        f"{df.duplicated().sum():,}"
    )

    col4.metric(
        "Negative ADR",
        f"{(df['adr'] < 0).sum():,}"
    )


# ============================================================
# TAB 2 — DASHBOARD
# ============================================================

with dashboard_tab:

    st.header("Hotel Booking Dashboard")

    # KPI calculations
    total_bookings = len(filtered_df)

    cancelled_bookings = (
        filtered_df["is_canceled"].sum()
    )

    cancellation_rate = (
        filtered_df["is_canceled"].mean() * 100
        if total_bookings > 0
        else 0
    )

    average_lead_time = (
        filtered_df["lead_time"].mean()
        if total_bookings > 0
        else 0
    )

    average_stay = (
        filtered_df["total_stay"].mean()
        if total_bookings > 0
        else 0
    )


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Bookings",
        f"{total_bookings:,}"
    )

    col2.metric(
        "Cancelled Bookings",
        f"{cancelled_bookings:,}"
    )

    col3.metric(
        "Cancellation Rate",
        f"{cancellation_rate:.2f}%"
    )

    col4.metric(
        "Average Lead Time",
        f"{average_lead_time:.1f} days"
    )

    col5.metric(
        "Average Stay",
        f"{average_stay:.1f} nights"
    )


    st.markdown("---")

    # --------------------------------------------------------
    # BOOKING OVERVIEW
    # --------------------------------------------------------

    st.subheader("Booking Overview")

    col1, col2 = st.columns(2)


    # Hotel booking share
    with col1:

        hotel_counts = (
            filtered_df["hotel"]
            .value_counts()
            .reset_index()
        )

        hotel_counts.columns = [
            "Hotel Type",
            "Bookings"
        ]

        fig = px.pie(
            hotel_counts,
            names="Hotel Type",
            values="Bookings",
            hole=0.4,
            title="Share of Bookings by Hotel Type"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        fig.update_layout(
            font=dict(
                family="Arial"
            ),
            margin=dict(
                t=60,
                b=20,
                l=20,
                r=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Cancellation distribution
    with col2:

        cancellation_counts = (
            filtered_df["is_canceled"]
            .map({
                0: "Not Cancelled",
                1: "Cancelled"
            })
            .value_counts()
            .reset_index()
        )

        cancellation_counts.columns = [
            "Booking Status",
            "Bookings"
        ]

        fig = px.bar(
            cancellation_counts,
            x="Booking Status",
            y="Bookings",
            text="Bookings",
            title="Booking Cancellation Distribution"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Booking Status",
            yaxis_title="Number of Bookings",
            font=dict(
                family="Arial"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # MONTHLY BOOKING TREND
    # --------------------------------------------------------

    st.subheader("Monthly Booking Trend")

    monthly = (
        filtered_df
        .groupby(
            ["arrival_date_month", "hotel"]
        )
        .size()
        .reset_index(
            name="Bookings"
        )
    )

    monthly["arrival_date_month"] = pd.Categorical(
        monthly["arrival_date_month"],
        categories=month_order,
        ordered=True
    )

    monthly = monthly.sort_values(
        "arrival_date_month"
    )

    fig = px.line(
        monthly,
        x="arrival_date_month",
        y="Bookings",
        color="hotel",
        markers=True,
        title="Monthly Bookings by Hotel Type"
    )

    fig.update_layout(
        xaxis_title="Arrival Month",
        yaxis_title="Number of Bookings",
        font=dict(
            family="Arial"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB 3 — EDA
# ============================================================

with eda_tab:

    st.header("Exploratory Data Analysis")

    st.caption(
        "Each analysis below follows the structure: "
        "Business Question → Visualization → Caption → Insight."
    )


    # ========================================================
    # QUESTION 1
    # ========================================================

    st.markdown(
        '<div class="question">'
        'Q1. Which hotel type is booked most frequently?'
        '</div>',
        unsafe_allow_html=True
    )


    hotel_counts = (
        filtered_df["hotel"]
        .value_counts()
        .reset_index()
    )

    hotel_counts.columns = [
        "Hotel Type",
        "Bookings"
    ]


    fig = px.bar(
        hotel_counts,
        x="Hotel Type",
        y="Bookings",
        text="Bookings",
        title="Bookings by Hotel Type"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Hotel Type",
        yaxis_title="Number of Bookings",
        font=dict(
            family="Arial"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.markdown(
        '<div class="caption-box">'
        '<b>Caption:</b> The chart compares the booking volume '
        'between City Hotel and Resort Hotel.'
        '</div>',
        unsafe_allow_html=True
    )


    if not hotel_counts.empty:

        top_hotel = hotel_counts.iloc[0]

        st.markdown(
            f'<div class="insight-box">'
            f'<b>Insight:</b> {top_hotel["Hotel Type"]} '
            f'has the highest booking volume with '
            f'{top_hotel["Bookings"]:,} bookings.'
            f'</div>',
            unsafe_allow_html=True
        )


    st.markdown("---")


    # ========================================================
    # QUESTION 2 — MONTHLY BOOKINGS
    # ========================================================

    st.markdown(
        '<div class="question">'
        'Q2. How does booking demand vary across months?'
        '</div>',
        unsafe_allow_html=True
    )


    monthly_total = (
        filtered_df["arrival_date_month"]
        .value_counts()
        .reindex(month_order)
        .fillna(0)
        .reset_index()
    )

    monthly_total.columns = [
        "Month",
        "Bookings"
    ]


    fig = px.line(
        monthly_total,
        x="Month",
        y="Bookings",
        markers=True,
        title="Monthly Booking Volume"
    )

    fig.update_layout(
        xaxis_title="Arrival Month",
        yaxis_title="Number of Bookings",
        font=dict(
            family="Arial"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    busiest_month = monthly_total.loc[
        monthly_total["Bookings"].idxmax(),
        "Month"
    ]

    quietest_month = monthly_total.loc[
        monthly_total["Bookings"].idxmin(),
        "Month"
    ]


    st.markdown(
        '<div class="caption-box">'
        '<b>Caption:</b> Booking volume changes across the '
        'different arrival months.'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        f'<div class="insight-box">'
        f'<b>Insight:</b> {busiest_month} has the highest '
        f'booking volume, while {quietest_month} has '
        f'the lowest.'
        f'</div>',
        unsafe_allow_html=True
    )


    st.markdown("---")


    # ========================================================
    # QUESTION 3 — STAY DURATION
    # ========================================================

    st.markdown(
        '<div class="question">'
        'Q3. Does the length of stay affect the cancellation rate?'
        '</div>',
        unsafe_allow_html=True
    )


    stay_analysis = (
        filtered_df
        .groupby(
            ["hotel", "total_stay"]
        )
        .agg(
            Bookings=(
                "is_canceled",
                "count"
            ),
            Cancellation_Rate=(
                "is_canceled",
                "mean"
            )
        )
        .reset_index()
    )


    stay_analysis[
        "Cancellation_Rate"
    ] = (
        stay_analysis["Cancellation_Rate"]
        * 100
    )


    stay_analysis = stay_analysis[
        stay_analysis["Bookings"] >= 30
    ].copy()


    stay_chart = stay_analysis[
        stay_analysis["total_stay"] <= 30
    ].copy()


    fig = px.line(
        stay_chart,
        x="total_stay",
        y="Cancellation_Rate",
        color="hotel",
        markers=True,
        title="Cancellation Rate by Total Stay Duration"
    )

    fig.update_layout(
        xaxis_title="Total Stay (Nights)",
        yaxis_title="Cancellation Rate (%)",
        font=dict(
            family="Arial"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.markdown(
        '<div class="caption-box">'
        '<b>Caption:</b> The chart shows how cancellation '
        'rates vary with different stay durations.'
        '</div>',
        unsafe_allow_html=True
    )


    if not stay_chart.empty:

        highest_stay = stay_chart.loc[
            stay_chart["Cancellation_Rate"].idxmax()
        ]

        st.markdown(
            f'<div class="insight-box">'
            f'<b>Insight:</b> The highest observed cancellation '
            f'rate in the displayed range is '
            f'{highest_stay["Cancellation_Rate"]:.2f}% '
            f'at {int(highest_stay["total_stay"])} nights '
            f'for {highest_stay["hotel"]}.'
            f'</div>',
            unsafe_allow_html=True
        )


    st.markdown("---")


    # ========================================================
    # QUESTION 4 — LEAD TIME
    # ========================================================

    st.markdown(
        '<div class="question">'
        'Q4. Does lead time affect the cancellation rate?'
        '</div>',
        unsafe_allow_html=True
    )


    lead_bins = [
        -1,
        7,
        30,
        90,
        180,
        365,
        float("inf")
    ]


    lead_labels = [
        "0-7 days",
        "8-30 days",
        "31-90 days",
        "91-180 days",
        "181-365 days",
        "365+ days"
    ]


    eda_df = filtered_df.copy()


    eda_df["lead_time_group"] = pd.cut(
        eda_df["lead_time"],
        bins=lead_bins,
        labels=lead_labels
    )


    lead_analysis = (
        eda_df
        .groupby(
            [
                "lead_time_group",
                "hotel"
            ],
            observed=False
        )["is_canceled"]
        .mean()
        .mul(100)
        .reset_index(
            name="Cancellation Rate"
        )
    )


    fig = px.bar(
        lead_analysis,
        x="lead_time_group",
        y="Cancellation Rate",
        color="hotel",
        barmode="group",
        text="Cancellation Rate",
        title="Cancellation Rate by Lead Time"
    )


    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )


    fig.update_layout(
        xaxis_title="Lead Time",
        yaxis_title="Cancellation Rate (%)",
        font=dict(
            family="Arial"
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.markdown(
        '<div class="caption-box">'
        '<b>Caption:</b> Cancellation rates vary across '
        'different lead-time groups.'
        '</div>',
        unsafe_allow_html=True
    )


    if not lead_analysis.empty:

        highest_lead = lead_analysis.loc[
            lead_analysis["Cancellation Rate"].idxmax()
        ]

        st.markdown(
            f'<div class="insight-box">'
            f'<b>Insight:</b> The highest observed cancellation '
            f'rate is {highest_lead["Cancellation Rate"]:.2f}% '
            f'for the {highest_lead["lead_time_group"]} '
            f'lead-time group in {highest_lead["hotel"]}.'
            f'</div>',
            unsafe_allow_html=True
        )


    st.markdown("---")


    # ========================================================
    # SUPPORTING ANALYSIS
    # ========================================================

    st.subheader("Supporting Analysis")


    col1, col2 = st.columns(2)


    # Cancellation by hotel
    with col1:

        cancellation_by_hotel = (
            filtered_df
            .groupby("hotel")["is_canceled"]
            .mean()
            .mul(100)
            .reset_index(
                name="Cancellation Rate"
            )
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
            yaxis_title="Cancellation Rate (%)",
            font=dict(
                family="Arial"
            )
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ADR by hotel
    with col2:

        adr_by_hotel = (
            filtered_df
            .groupby("hotel")["adr"]
            .mean()
            .reset_index(
                name="Average ADR"
            )
        )


        fig = px.bar(
            adr_by_hotel,
            x="hotel",
            y="Average ADR",
            text="Average ADR",
            title="Average ADR by Hotel Type"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )


        fig.update_layout(
            xaxis_title="Hotel Type",
            yaxis_title="Average ADR",
            font=dict(
                family="Arial"
            )
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# TAB 4 — INSIGHTS & RECOMMENDATIONS
# ============================================================

with insights_tab:

    st.header("Insights & Recommendations")


    # ========================================================
    # KEY INSIGHTS
    # ========================================================

    st.subheader("Key Insights")


    hotel_counts = (
        filtered_df["hotel"]
        .value_counts()
    )


    total = len(filtered_df)


    if total > 0:

        top_hotel = hotel_counts.idxmax()

        top_count = hotel_counts.max()

        top_share = (
            top_count
            / total
            * 100
        )

    else:

        top_hotel = "N/A"
        top_count = 0
        top_share = 0


    monthly_total = (
        filtered_df["arrival_date_month"]
        .value_counts()
        .reindex(month_order)
        .fillna(0)
    )


    if monthly_total.sum() > 0:

        busiest = monthly_total.idxmax()

        quietest = monthly_total.idxmin()

    else:

        busiest = "N/A"

        quietest = "N/A"


    cancellation_by_hotel = (
        filtered_df
        .groupby("hotel")["is_canceled"]
        .mean()
        .mul(100)
    )


    if not cancellation_by_hotel.empty:

        highest_cancel_hotel = (
            cancellation_by_hotel.idxmax()
        )

        highest_cancel_rate = (
            cancellation_by_hotel.max()
        )

    else:

        highest_cancel_hotel = "N/A"

        highest_cancel_rate = 0


    st.markdown(
        f"""
        - **Hotel Popularity:** {top_hotel} has the highest
          booking volume with {top_count:,} bookings
          ({top_share:.1f}%).

        - **Seasonality:** {busiest} is the busiest month,
          while {quietest} is the quietest month.

        - **Cancellation:** {highest_cancel_hotel} has the
          higher cancellation rate at approximately
          {highest_cancel_rate:.2f}%.

        - **Stay Duration:** Cancellation behaviour varies
          across different stay durations.

        - **Lead Time:** Cancellation rates vary across
          different booking lead-time groups.
        """
    )


    st.markdown("---")


    # ========================================================
    # BUSINESS RECOMMENDATIONS
    # ========================================================

    st.subheader("Business Recommendations")


    st.markdown(
        """
        <div class="recommendation-box">

        <b>1. Prepare for Seasonal Demand</b>

        <p>
        Increase room availability, staffing and operational
        readiness during high-demand months.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="recommendation-box">

        <b>2. Improve Performance of the Less-Booked Hotel Type</b>

        <p>
        Use targeted promotions, seasonal packages and attractive
        offers to increase bookings.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="recommendation-box">

        <b>3. Reduce Cancellation-Related Revenue Loss</b>

        <p>
        Review cancellation policies and booking conditions for
        segments with higher cancellation behaviour.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="recommendation-box">

        <b>4. Manage Long Lead-Time Bookings Carefully</b>

        <p>
        Use booking confirmation reminders and suitable booking
        conditions for reservations made far in advance.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="recommendation-box">

        <b>5. Use Data for Pricing and Inventory Decisions</b>

        <p>
        Combine booking demand, cancellation patterns and ADR
        behaviour when planning room inventory and pricing.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown("---")

    st.info(
        "These recommendations are based on the patterns "
        "identified during the exploratory data analysis."
    )