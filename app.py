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
        "You have administrator access to the Customer Churn Prediction System."
    )

    st.divider()

    st.subheader("Customer Prediction Access")
    st.write("You can also use the prediction system below.")

else:

    st.title("👨‍💼 Employee Dashboard")
    st.info("Welcome to the Employee Prediction Portal")

    st.write("Enter customer details below to predict churn.")

st.divider()
