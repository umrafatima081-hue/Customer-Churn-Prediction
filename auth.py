
import streamlit as st
import hashlib
import hmac

# Demo credentials
# Production mein credentials ko Streamlit Secrets mein rakhein.

USERS = {
    "EMP001": {
        "password_hash": hashlib.sha256("Employee@123".encode()).hexdigest(),
        "role": "employee"
    },
    "EMP002": {
        "password_hash": hashlib.sha256("Employee@456".encode()).hexdigest(),
        "role": "employee"
    },
    "ADMIN001": {
        "password_hash": hashlib.sha256("Admin@123".encode()).hexdigest(),
        "role": "admin"
    }
}


def login(employee_id, password):
    user = USERS.get(employee_id.strip().upper())

    if not user:
        return False

    entered_hash = hashlib.sha256(password.encode()).hexdigest()

    if hmac.compare_digest(entered_hash, user["password_hash"]):
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = employee_id.strip().upper()
        st.session_state["role"] = user["role"]
        return True

    return False


def logout():
    for key in ["logged_in", "user_id", "role"]:
        st.session_state.pop(key, None)
