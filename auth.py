import streamlit as st
import hashlib
import hmac


def login(employee_id, password):
    employee_id = employee_id.strip().upper()

    try:
        users = st.secrets["users"]
        user = users[employee_id]

        salt = bytes.fromhex(user["salt"])
        stored_hash = user["password_hash"]

        entered_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200000
        ).hex()

        if hmac.compare_digest(entered_hash, stored_hash):
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = employee_id
            st.session_state["role"] = user["role"]
            return True

    except (KeyError, ValueError, TypeError):
        return False

    return False


def logout():
    for key in ["logged_in", "user_id", "role"]:
        st.session_state.pop(key, None)
