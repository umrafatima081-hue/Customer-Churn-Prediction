
import streamlit as st
import pandas as pd
import joblib
import auth
import plotly.express as px
from supabase import create_client

st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background-color: #0B1120;
    color: #FFFFFF;
}
[data-testid="stSidebar"] {
    background-color: #111C32;
}
h1, h2, h3 {
    color: #8CB8FF;
}
div.stButton > button {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
}
div.stButton > button:hover {
    background-color: #1D4ED8;
    color: white;
}
.ai-header {
    background: linear-gradient(110deg, #14213d, #25205a, #123b50);
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #334a78;
    margin-bottom: 20px;
}
.ai-header h2 {
    color: #ffffff !important;
    margin: 0;
}
.ai-header p {
    color: #b9c9e8;
    margin: 6px 0 0 0;
}
.kpi-card {
    background: linear-gradient(145deg, #17243d, #202d4a);
    border: 1px solid #344767;
    border-radius: 14px;
    padding: 18px;
    min-height: 120px;
}
.kpi-label {
    color: #a9bad5;
    font-size: 14px;
    margin-bottom: 10px;
}
.kpi-value {
    color: #ffffff;
    font-size: 29px;
    font-weight: 700;
}
.kpi-note {
    color: #8da5c9;
    font-size: 12px;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SUPABASE CONNECTION ----------------

@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    )


try:
    supabase = get_supabase()
except Exception:
    supabase = None


# ---------------- LOGIN SCREEN ----------------

if not st.session_state.get("logged_in", False):

    st.title("🔐 Customer Churn Prediction")
    st.subheader("Secure Employee Portal")
    st.write("Please login to access the dashboard.")

    with st.form("login_form"):
        employee_id = st.text_input("Employee / Admin ID")
        password = st.text_input("Password", type="password")

        login_button = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if login_button:
        if auth.login(employee_id, password):
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid Employee ID or Password.")

    st.stop()


# ---------------- LOAD MODEL ----------------

try:
    model = joblib.load("customer_churn_model.pkl")
except Exception:
    st.error("Model could not be loaded. Please contact administrator.")
    st.stop()


# ---------------- USER DETAILS ----------------

user_id = st.session_state.get("user_id", "User")
role = st.session_state.get("role", "employee")


# ---------------- SIDEBAR ----------------

st.sidebar.title("📊 Churn Dashboard")
st.sidebar.write(f"Welcome, {user_id}")
st.sidebar.write(f"Role: {role.title()}")

if st.sidebar.button("Logout", use_container_width=True):
    auth.logout()
    st.rerun()


# ==================================================
# ADMIN DASHBOARD
# ==================================================

if role == "admin":

    st.title("🛡️ Admin Dashboard")
    st.success("Welcome to the Admin Control Panel")

    st.subheader("System Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Employees", "2")
    col2.metric("System Status", "Active")
    col3.metric("ML Model", "Ready")

    st.divider()

    st.subheader("Admin Information")
    st.write("Admin ID:", user_id)
    st.write("Role: System Administrator")

    st.info(
        "You have administrator access to the "
        "Customer Churn Prediction System."
    )

    # ----------------------------------------------
    # AI INTELLIGENCE CENTER
    # ----------------------------------------------

    st.divider()

    st.markdown("""
    <div class="ai-header">
        <h2>🧠 AI Intelligence Center</h2>
        <p>Customer churn insights • Prediction monitoring • Employee activity</p>
    </div>
    """, unsafe_allow_html=True)

    if supabase is not None:

        try:
            response = (
                supabase.table("prediction_history")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            records = response.data or []
            history_df = pd.DataFrame(records)

            if not history_df.empty:

                # PREPARE DATA

                history_df["prediction_status"] = (
                    history_df["prediction"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

                history_df["churn_status"] = (
                    history_df["prediction_status"]
                    .isin(["yes", "1", "true"])
                )

                history_df["churn_probability"] = pd.to_numeric(
                    history_df["churn_probability"],
                    errors="coerce"
                )

                history_df["created_at"] = pd.to_datetime(
                    history_df["created_at"],
                    utc=True,
                    errors="coerce"
                )

                total_predictions = len(history_df)

                churn_count = int(
                    history_df["churn_status"].sum()
                )

                stay_count = (
                    total_predictions - churn_count
                )

                churn_percentage = (
                    churn_count / total_predictions * 100
                )

                avg_probability = (
                    history_df["churn_probability"].mean()
                )

                avg_probability_text = (
                    f"{avg_probability:.1f}%"
                    if pd.notna(avg_probability)
                    else "N/A"
                )

                # KPI CARDS

                st.markdown("### ⚡ System Performance Overview")

                k1, k2, k3, k4 = st.columns(4)

                kpi_items = [
                    (
                        "📊 Total Predictions",
                        f"{total_predictions:,}",
                        "All saved predictions",
                        k1
                    ),
                    (
                        "🔥 Churn Rate",
                        f"{churn_percentage:.1f}%",
                        "Customers predicted to leave",
                        k2
                    ),
                    (
                        "🟢 Customers Staying",
                        f"{stay_count:,}",
                        "Predicted as non-churn",
                        k3
                    ),
                    (
                        "🎯 Avg. Churn Probability",
                        avg_probability_text,
                        "Average model probability",
                        k4
                    )
                ]

                for label, value, note, column in kpi_items:

                    with column:

                        st.markdown(
                            f"""
                            <div class="kpi-card">
                                <div class="kpi-label">{label}</div>
                                <div class="kpi-value">{value}</div>
                                <div class="kpi-note">{note}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.divider()

                # CHURN ANALYSIS

                st.markdown("### 📈 Customer Churn Intelligence")

                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:

                    donut_df = pd.DataFrame({
                        "Customer Status": [
                            "Churn",
                            "Not Churn"
                        ],
                        "Count": [
                            churn_count,
                            stay_count
                        ]
                    })

                    fig_donut = px.pie(
                        donut_df,
                        names="Customer Status",
                        values="Count",
                        hole=0.68,
                        color="Customer Status",
                        color_discrete_map={
                            "Churn": "#EC4899",
                            "Not Churn": "#22D3EE"
                        }
                    )

                    fig_donut.update_traces(
                        textposition="inside",
                        textinfo="percent",
                        marker=dict(
                            line=dict(
                                color="#0B1120",
                                width=4
                            )
                        )
                    )

                    fig_donut.update_layout(
                        title="Churn vs Non-Churn",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#E5EEFF"),
                        height=350
                    )

                    st.plotly_chart(
                        fig_donut,
                        use_container_width=True
                    )

                with chart_col2:

                    employee_df = (
                        history_df.groupby("employee_id")
                        .size()
                        .reset_index(name="Predictions")
                        .sort_values("Predictions")
                    )

                    fig_employee = px.bar(
                        employee_df,
                        x="Predictions",
                        y="employee_id",
                        orientation="h",
                        color="Predictions",
                        color_continuous_scale=[
                            "#263B70",
                            "#22D3EE",
                            "#8B5CF6"
                        ],
                        text="Predictions"
                    )

                    fig_employee.update_layout(
                        title="Prediction Activity by Employee",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#E5EEFF"),
                        coloraxis_showscale=False,
                        xaxis_title="Number of Predictions",
                        yaxis_title="Employee",
                        height=350
                    )

                    st.plotly_chart(
                        fig_employee,
                        use_container_width=True
                    )

                st.divider()

                # DAILY PREDICTION TREND

                st.markdown("### 🌐 Prediction Activity Timeline")

                trend_df = history_df.dropna(
                    subset=["created_at"]
                ).copy()

                if not trend_df.empty:

                    trend_df["prediction_date"] = (
                        trend_df["created_at"].dt.strftime("%Y-%m-%d")
                    )

                    daily_df = (
                        trend_df.groupby("prediction_date")
                        .size()
                        .reset_index(name="Predictions")
                        .sort_values("prediction_date")
                    )

                    fig_trend = px.area(
                        daily_df,
                        x="prediction_date",
                        y="Predictions",
                        markers=True
                    )

                    fig_trend.update_traces(
                        line=dict(
                            color="#22D3EE",
                            width=3
                        ),
                        fillcolor="rgba(34,211,238,0.18)",
                        marker=dict(
                            color="#8B5CF6",
                            size=8
                        )
                    )

                    fig_trend.update_layout(
                        title="Daily Prediction Volume",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#E5EEFF"),
                        xaxis_title="Date",
                        yaxis_title="Predictions",
                        height=350
                    )

                    st.plotly_chart(
                        fig_trend,
                        use_container_width=True
                    )

                else:
                    st.info("Date-wise prediction data is not available.")

                st.divider()

                # CHURN PROBABILITY DISTRIBUTION

                st.markdown("### 🎯 AI Churn Probability Distribution")

                probability_df = history_df.dropna(
                    subset=["churn_probability"]
                )

                if not probability_df.empty:

                    fig_probability = px.histogram(
                        probability_df,
                        x="churn_probability",
                        nbins=12,
                        color_discrete_sequence=["#8B5CF6"],
                        opacity=0.9
                    )

                    fig_probability.update_traces(
                        marker_line_color="#22D3EE",
                        marker_line_width=1
                    )

                    fig_probability.update_layout(
                        title="Distribution of Predicted Churn Probability",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#E5EEFF"),
                        xaxis_title="Churn Probability (%)",
                        yaxis_title="Number of Customers",
                        height=350
                    )

                    st.plotly_chart(
                        fig_probability,
                        use_container_width=True
                    )

                else:
                    st.info("Churn probability data is not available.")

                st.divider()

                # RECENT PREDICTION RECORDS

                st.markdown("### 📋 Recent Prediction Records")

                display_columns = [
                    "employee_id",
                    "prediction",
                    "churn_probability",
                    "created_at"
                ]

                recent_df = history_df[display_columns].copy()

                recent_df["created_at"] = (
                    recent_df["created_at"]
                    .dt.strftime("%d %b %Y, %I:%M %p")
                )

                recent_df = recent_df.rename(columns={
                    "employee_id": "Employee ID",
                    "prediction": "Prediction",
                    "churn_probability": "Churn Probability (%)",
                    "created_at": "Date & Time"
                })

                st.dataframe(
                    recent_df.head(20),
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    "Showing the latest 20 records from prediction history."
                )

            else:

                st.info(
                    "No prediction history found yet. "
                    "Make a customer prediction to see analytics here."
                )

        except Exception as e:

            st.error("Could not load prediction history.")
            st.caption(str(e))

    else:

        st.warning("Supabase connection is not available.")

    st.divider()

    st.subheader("Customer Prediction Access")
    st.write("You can also use the prediction system below.")

else:

    # EMPLOYEE DASHBOARD

    st.title("👨‍💼 Employee Dashboard")
    st.info("Welcome to the Employee Prediction Portal")
    st.write("Enter customer details below to predict churn.")


# ==================================================
# CUSTOMER INFORMATION FORM
# ==================================================

st.divider()

st.subheader("👤 Customer Information")

with st.form("customer_form"):

    gender = st.selectbox("Gender", ["Male", "Female"])
    senior = st.selectbox("Senior Citizen", [0, 1])
    partner = st.selectbox("Partner", ["Yes", "No"])
    dependents = st.selectbox("Dependents", ["Yes", "No"])

    tenure = st.number_input(
        "Tenure (months)",
        0,
        100,
        12
    )

    phone = st.selectbox("Phone Service", ["Yes", "No"])

    multiple = st.selectbox(
        "Multiple Lines",
        ["Yes", "No", "No phone service"]
    )

    internet = st.selectbox(
        "Internet Service",
        ["DSL", "Fiber optic", "No"]
    )

    security = st.selectbox(
        "Online Security",
        ["Yes", "No", "No internet service"]
    )

    backup = st.selectbox(
        "Online Backup",
        ["Yes", "No", "No internet service"]
    )

    protection = st.selectbox(
        "Device Protection",
        ["Yes", "No", "No internet service"]
    )

    support = st.selectbox(
        "Tech Support",
        ["Yes", "No", "No internet service"]
    )

    tv = st.selectbox(
        "Streaming TV",
        ["Yes", "No", "No internet service"]
    )

    movies = st.selectbox(
        "Streaming Movies",
        ["Yes", "No", "No internet service"]
    )

    contract = st.selectbox(
        "Contract",
        ["Month-to-month", "One year", "Two year"]
    )

    paperless = st.selectbox(
        "Paperless Billing",
        ["Yes", "No"]
    )

    payment = st.selectbox(
        "Payment Method",
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ]
    )

    monthly = st.number_input(
        "Monthly Charges",
        min_value=0.0,
        value=70.0
    )

    total = st.number_input(
        "Total Charges",
        min_value=0.0,
        value=500.0
    )

    submitted = st.form_submit_button(
        "Predict Churn",
        use_container_width=True
    )


# ==================================================
# PREDICTION RESULT
# ==================================================

if submitted:

    input_data = pd.DataFrame([{
        "gender": gender,
        "SeniorCitizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone,
        "MultipleLines": multiple,
        "InternetService": internet,
        "OnlineSecurity": security,
        "OnlineBackup": backup,
        "DeviceProtection": protection,
        "TechSupport": support,
        "StreamingTV": tv,
        "StreamingMovies": movies,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment,
        "MonthlyCharges": monthly,
        "TotalCharges": total
    }])

    try:

        prediction = model.predict(input_data)[0]
        classes = list(model.classes_)

        churn_label = next(
            (
                label for label in classes
                if str(label).strip().lower()
                in ["yes", "1", "true"]
            ),
            None
        )

        if churn_label is None:

            st.error("Churn class could not be identified.")

        else:

            st.divider()
            st.subheader("📈 Prediction Result")

            if prediction == churn_label:

                st.error(
                    "⚠️ Customer is likely to leave (Churn)."
                )

            else:

                st.success(
                    "✅ Customer is likely to stay (No Churn)."
                )

            if hasattr(model, "predict_proba"):

                probabilities = model.predict_proba(input_data)[0]

                churn_index = classes.index(churn_label)

                churn_probability = float(
                    probabilities[churn_index] * 100
                )

                st.metric(
                    "Churn Probability",
                    f"{churn_probability:.2f}%"
                )

                st.progress(
                    min(
                        max(churn_probability / 100, 0.0),
                        1.0
                    )
                )

                # SAVE PREDICTION TO SUPABASE

                if supabase is not None:

                    try:

                        supabase.table("prediction_history").insert({
                            "employee_id": user_id,
                            "customer_data": input_data.to_dict(
                                orient="records"
                            )[0],
                            "prediction": str(prediction),
                            "churn_probability": churn_probability
                        }).execute()

                        st.success(
                            "Prediction history saved successfully!"
                        )

                    except Exception as e:

                        st.warning(
                            "Prediction completed, but history could not be saved."
                        )

                        st.caption(str(e))

                else:

                    st.warning(
                        "Prediction completed, but Supabase is not connected."
                    )

    except Exception as e:

        st.error(
            "Prediction failed. Please check the customer details."
        )

        st.caption(str(e))
