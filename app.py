
import streamlit as st
import pandas as pd
import joblib
import auth

# Page configuration
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide"
)

# Dark dashboard styling
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
</style>
""", unsafe_allow_html=True)


# LOGIN SCREEN
if not st.session_state.get("logged_in", False):

    st.title("🔐 Customer Churn Prediction")
    st.subheader("Secure Employee Portal")
    st.write("Please login to access the prediction dashboard.")

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


# LOAD MODEL AFTER LOGIN
try:
    model = joblib.load("customer_churn_model.pkl")
except Exception as e:
    st.error("Model could not be loaded. Please contact the administrator.")
    st.stop()


# SIDEBAR
user_id = st.session_state.get("user_id", "User")
role = st.session_state.get("role", "employee")

st.sidebar.title("📊 Churn Dashboard")
st.sidebar.write(f"Welcome, {user_id}")
st.sidebar.write(f"Role: {role.title()}")

if st.sidebar.button("Logout", use_container_width=True):
    auth.logout()
    st.rerun()


# MAIN DASHBOARD
st.title("Customer Churn Prediction")
st.write("Analyze customer details and predict the possibility of churn.")

if role == "admin":
    st.success("Admin Access: You are logged in as an administrator.")
else:
    st.info("Employee Access: You can use the customer prediction system.")


st.divider()

st.subheader("👤 Customer Information")

with st.form("customer_form"):

    gender = st.selectbox("Gender", ["Male", "Female"])
    senior = st.selectbox("Senior Citizen", [0, 1])
    partner = st.selectbox("Partner", ["Yes", "No"])
    dependents = st.selectbox("Dependents", ["Yes", "No"])
    tenure = st.number_input("Tenure (months)", 0, 100, 12)

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
    paperless = st.selectbox("Paperless Billing", ["Yes", "No"])

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


# PREDICTION
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
                st.error("⚠️ Customer is likely to leave (Churn).")
            else:
                st.success("✅ Customer is likely to stay (No Churn).")

            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(input_data)[0]
                churn_index = classes.index(churn_label)
                churn_probability = probabilities[churn_index] * 100

                st.metric(
                    "Churn Probability",
                    f"{churn_probability:.2f}%"
                )

                st.progress(
                    min(max(float(churn_probability) / 100, 0.0), 1.0)
                )

    except Exception:
        st.error("Prediction failed. Please check the customer details.")

