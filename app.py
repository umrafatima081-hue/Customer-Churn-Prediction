
    # REAL PREDICTION HISTORY
    st.divider()
    st.subheader("📊 Prediction History & Analytics")

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

                # Prepare data
                history_df["prediction_status"] = (
                    history_df["prediction"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

                history_df["churn_status"] = history_df[
                    "prediction_status"
                ].isin(["yes", "1", "true"])

                history_df["churn_probability"] = pd.to_numeric(
                    history_df["churn_probability"],
                    errors="coerce"
                )

                total_predictions = len(history_df)
                churn_count = int(history_df["churn_status"].sum())
                stay_count = total_predictions - churn_count

                churn_percentage = (
                    churn_count / total_predictions * 100
                )

                # KPI CARDS
                st.markdown("### 📌 Key Performance Indicators")

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Total Predictions",
                    total_predictions
                )

                c2.metric(
                    "Churn Rate",
                    f"{churn_percentage:.2f}%"
                )

                c3.metric(
                    "Churn Customers",
                    churn_count
                )

                c4.metric(
                    "Customers Staying",
                    stay_count
                )

                st.divider()

                # DONUT CHART
                st.markdown("### 📈 Customer Churn Analysis")

                chart_col1, chart_col2 = st.columns(2)

                donut_df = pd.DataFrame({
                    "Customer Status": ["Churn", "Not Churn"],
                    "Count": [churn_count, stay_count]
                })

                with chart_col1:
                    fig_donut = px.pie(
                        donut_df,
                        names="Customer Status",
                        values="Count",
                        hole=0.55,
                        title="Churn vs Non-Churn Customers"
                    )

                    fig_donut.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="white"
                    )

                    st.plotly_chart(
                        fig_donut,
                        use_container_width=True
                    )

                # EMPLOYEE BAR CHART
                with chart_col2:
                    employee_df = (
                        history_df.groupby("employee_id")
                        .size()
                        .reset_index(name="Predictions")
                    )

                    fig_employee = px.bar(
                        employee_df,
                        x="employee_id",
                        y="Predictions",
                        color="employee_id",
                        title="Predictions by Employee",
                        text="Predictions"
                    )

                    fig_employee.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        showlegend=False
                    )

                    st.plotly_chart(
                        fig_employee,
                        use_container_width=True
                    )

                st.divider()

                # DAILY PREDICTION TREND
                st.markdown("### 📅 Prediction Trends")

                history_df["created_at"] = pd.to_datetime(
                    history_df["created_at"],
                    utc=True,
                    errors="coerce"
                )

                trend_df = history_df.dropna(
                    subset=["created_at"]
                ).copy()

                if not trend_df.empty:

                    trend_df["prediction_date"] = (
                        trend_df["created_at"].dt.date.astype(str)
                    )

                    daily_df = (
                        trend_df.groupby("prediction_date")
                        .size()
                        .reset_index(name="Predictions")
                        .sort_values("prediction_date")
                    )

                    fig_trend = px.line(
                        daily_df,
                        x="prediction_date",
                        y="Predictions",
                        markers=True,
                        title="Daily Prediction Activity"
                    )

                    fig_trend.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_title="Date",
                        yaxis_title="Number of Predictions"
                    )

                    st.plotly_chart(
                        fig_trend,
                        use_container_width=True
                    )

                else:
                    st.info("Date-wise prediction data is not available.")

                # PROBABILITY HISTOGRAM
                st.markdown("### 🎯 Churn Probability Distribution")

                probability_df = history_df.dropna(
                    subset=["churn_probability"]
                )

                if not probability_df.empty:

                    fig_probability = px.histogram(
                        probability_df,
                        x="churn_probability",
                        nbins=10,
                        title="Customer Churn Probability",
                        labels={
                            "churn_probability": "Churn Probability (%)"
                        }
                    )

                    fig_probability.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_title="Churn Probability (%)",
                        yaxis_title="Number of Customers"
                    )

                    st.plotly_chart(
                        fig_probability,
                        use_container_width=True
                    )

                st.divider()

                # RECENT RECORDS
                st.markdown("### 📋 Recent Prediction Records")

                display_columns = [
                    "employee_id",
                    "prediction",
                    "churn_probability",
                    "created_at"
                ]

                st.dataframe(
                    history_df[display_columns],
                    use_container_width=True,
                    hide_index=True
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
