import sqlite3
import pdfplumber
import os

# --- CONFIGURATION ---
# Point this to your Google Drive folder path (e.g., G:\My Drive\...)
SOURCE_FOLDER = r'C:\Home and personal\Personal\Electoral List\75_76'
DB_NAME = 'electoral_data.db'

def create_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table matching your PDF columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial_no TEXT,
            epic_number TEXT,
            elector_name TEXT,
            source_file TEXT,
            page_number INTEGER
        )
    ''')
    # Clear old data to avoid duplicates when re-running
    c.execute('DELETE FROM voters')
    conn.commit()
    return conn

def parse_pdfs():
    conn = create_db()
    c = conn.cursor()
    
    files = [f for f in os.listdir(SOURCE_FOLDER) if f.endswith('.pdf')]
    total_files = len(files)
    print(f"Found {total_files} PDF files. Starting indexing... this may take a while.")

    count = 0
    for filename in files:
        path = os.path.join(SOURCE_FOLDER, filename)
        try:
            with pdfplumber.open(path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    table = page.extract_table()
                    if table:
                        for row in table:
                            # Basic check to ensure row has data (Serial, EPIC, Name)
                            # Adjust index [2] based on your image (Name appears to be 3rd or 4th column)
                            # Based on image: Col 0=S.No, Col 1=Serial, Col 2=EPIC, Col 3=Name
                            if len(row) > 3 and row[3]: 
                                serial = row[1]
                                epic = row[2]
                                name = row[3]
                                
                                c.execute('''
                                    INSERT INTO voters (serial_no, epic_number, elector_name, source_file, page_number)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', (serial, epic, name, filename, page_num + 1))
        except Exception as e:
            print(f"Skipping {filename}: {e}")
        
        count += 1
        print(f"Processed {count}/{total_files}: {filename}")

    conn.commit()
    conn.close()
    print("Database updated successfully!")

if __name__ == "__main__":
    parse_pdfs()