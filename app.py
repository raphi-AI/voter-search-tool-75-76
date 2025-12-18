import streamlit as st
import sqlite3
import pandas as pd
import zipfile
import os

# --- CONFIGURATION ---
# We define the database name once here so everything else uses it correctly.
DB_NAME = 'electoral_data.db'
ZIP_NAME = 'electoral_data.zip'

# --- AUTO-UNZIP LOGIC ---
# This checks: "If the .db file is missing BUT the .zip file is here, unzip it."
if not os.path.exists(DB_NAME) and os.path.exists(ZIP_NAME):
    with zipfile.ZipFile(ZIP_NAME, 'r') as zip_ref:
        zip_ref.extractall('.')

def get_data(names_list):
    # Now this function can find DB_NAME because it was defined at the top
    conn = sqlite3.connect(DB_NAME)
    
    query = "SELECT * FROM voters WHERE "
    conditions = []
    params = []
    
    for name in names_list:
        conditions.append("UPPER(elector_name) LIKE ?")
        params.append(f"%{name.upper()}%")
    
    if not conditions:
        conn.close()
        return pd.DataFrame()
        
    query += " OR ".join(conditions)
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.error(f"Database Error: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
        
    return df

# --- THE INTERFACE ---
st.set_page_config(page_title="Electoral Search", layout="wide")

st.title("🔍 Electoral Roll Search Engine")
st.markdown("Enter names below to search the database generated from the PDF files.")

# Input Tab
with st.form("search_form"):
    text_input = st.text_area("Enter Names (one per line):", height=150, help="Type names here and press Search")
    submitted = st.form_submit_button("Search Database")

if submitted and text_input:
    names_to_search = [n.strip() for n in text_input.split('\n') if n.strip()]
    
    if names_to_search:
        st.info(f"Searching for: {', '.join(names_to_search)}")
        
        # Check if DB exists before querying
        if not os.path.exists(DB_NAME):
            st.error(f"Critical Error: Database file '{DB_NAME}' not found. Did the zip extraction fail?")
        else:
            results = get_data(names_to_search)
            
            if not results.empty:
                st.success(f"Found {len(results)} matches!")
                st.dataframe(results, use_container_width=True)
                
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Results as CSV",
                    csv,
                    "search_results.csv",
                    "text/csv",
                    key='download-csv'
                )
            else:
                st.warning("No matches found.")
    else:
        st.error("Please enter at least one name.")
