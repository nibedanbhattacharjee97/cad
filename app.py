import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# Database connection settings
DB_HOST = "localhost"
DB_USER = "root"  # Change if necessary
DB_PASSWORD = ""  # Change if necessary
DB_NAME = "anudip"  # Change to your actual database name
TABLE_NAME = "me_reject"

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )

# Upload Page
def upload_page():
    st.title("Excel Upload to MySQL (me_reject Table)")
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("Preview of uploaded file:")
        st.dataframe(df)
        
        if st.button("Upload to Database"):
            insert_data(df)

def insert_data(df):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {TABLE_NAME} (unique_id, reason_for_rejection) VALUES (%s, %s)",
                (int(row["unique_id"]), str(row["reason_for_rejection"]))
            )
        
        conn.commit()
        st.success("Data successfully uploaded to the database!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# View Data Page
def view_data_page():
    st.title("Rejection Reasons Analysis")
    
    try:
        conn = get_db_connection()
        query = f"SELECT reason_for_rejection, COUNT(*) as count FROM {TABLE_NAME} GROUP BY reason_for_rejection"
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            fig = px.bar(df, x="reason_for_rejection", y="count", title="Rejections Count by Reason", labels={"reason_for_rejection": "Reason", "count": "Count"})
            st.plotly_chart(fig)
        else:
            st.warning("No data found in the database.")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload Data", "View Data"])

if page == "Upload Data":
    upload_page()
elif page == "View Data":
    view_data_page()
