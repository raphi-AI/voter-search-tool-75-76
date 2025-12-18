import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURATION ---
DB_NAME = 'electoral_data.db'

def get_data(names_list):
    conn = sqlite3.connect(DB_NAME)
    
    # Dynamic SQL query generation
    # We use UPPER() to make it case insensitive
    query = "SELECT * FROM voters WHERE "
    conditions = []
    params = []
    
    for name in names_list:
        conditions.append("UPPER(elector_name) LIKE ?")
        params.append(f"%{name.upper()}%") # The % symbols allow partial matches
    
    if not conditions:
        return pd.DataFrame()
        
    query += " OR ".join(conditions)
    
    df = pd.read_sql_query(query, conn, params=params)
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
    # Process input: split by new lines and remove empty spaces
    names_to_search = [n.strip() for n in text_input.split('\n') if n.strip()]
    
    if names_to_search:
        st.info(f"Searching for: {', '.join(names_to_search)}")
        
        # Query Database
        results = get_data(names_to_search)
        
        if not results.empty:
            st.success(f"Found {len(results)} matches!")
            # Display as a clean interactive table
            st.dataframe(results, use_container_width=True)
            
            # Download Button
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