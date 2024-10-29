from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import Optional

app = FastAPI()

# Initialize the database with 10 rows of data directly in the code
def initialize_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('networking_data.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Timestamp TEXT,
        User_ID TEXT,
        Application_Type TEXT,
        Signal_Strength TEXT,
        Latency TEXT,
        Required_Bandwidth TEXT,
        Allocated_Bandwidth TEXT,
        Resource_Allocation TEXT
    )
    """)

    # Insert 10 rows of data 
    sample_data = [
        ("9/3/2023 10:02", "User_001", "Web_Browsing", "-92 dBm", "25 ms", "0.8 Mbps", "0.8 Mbps", "70%"),
        ("9/3/2023 10:05", "User_002", "Video_Streaming", "-88 dBm", "45 ms", "1.5 Mbps", "1.5 Mbps", "65%"),
        ("9/3/2023 10:08", "User_003", "Gaming", "-90 dBm", "30 ms", "2 Mbps", "1.8 Mbps", "80%"),
        ("9/3/2023 10:10", "User_004", "File_Download", "-85 dBm", "20 ms", "5 Mbps", "4.5 Mbps", "75%"),
        ("9/3/2023 10:15", "User_005", "Email", "-78 dBm", "10 ms", "0.2 Mbps", "0.2 Mbps", "90%"),
        ("9/3/2023 10:20", "User_006", "VoIP_Call", "-82 dBm", "35 ms", "0.5 Mbps", "0.4 Mbps", "85%"),
        ("9/3/2023 10:25", "User_007", "Web_Browsing", "-94 dBm", "40 ms", "1 Mbps", "1 Mbps", "60%"),
        ("9/3/2023 10:30", "User_008", "Video_Streaming", "-88 dBm", "50 ms", "3 Mbps", "2.9 Mbps", "72%"),
        ("9/3/2023 10:35", "User_009", "Gaming", "-92 dBm", "28 ms", "2.2 Mbps", "2 Mbps", "78%"),
        ("9/3/2023 10:40", "User_010", "File_Download", "-86 dBm", "22 ms", "4 Mbps", "3.5 Mbps", "83%"),
    ]

    for row in sample_data:
        cursor.execute("""
        INSERT INTO data_table (Timestamp, User_ID, Application_Type, Signal_Strength, 
                                Latency, Required_Bandwidth, Allocated_Bandwidth, Resource_Allocation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Call the function to initialize the database
initialize_database()

# Define Pydantic model based on dataset columns
class DataModel(BaseModel):
    id: Optional[int] = None
    Timestamp: str
    User_ID: str
    Application_Type: str
    Signal_Strength: str
    Latency: str
    Required_Bandwidth: str
    Allocated_Bandwidth: str
    Resource_Allocation: str

# CRUD Operations

# Establish SQLite3 connection for each request
def get_db_connection():
    conn = sqlite3.connect('networking_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# Get all records
@app.get("/records/")
def read_all():
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM data_table").fetchall()
    conn.close()
    return [dict(record) for record in records]

# Get record by ID
@app.get("/records/{record_id}")
def read_record(record_id: int):
    conn = get_db_connection()
    record = conn.execute("SELECT * FROM data_table WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return dict(record)

# Add a new record
@app.post("/records/")
def create_record(record: DataModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO data_table (Timestamp, User_ID, Application_Type, Signal_Strength, 
                                Latency, Required_Bandwidth, Allocated_Bandwidth, Resource_Allocation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.Timestamp, record.User_ID, record.Application_Type, record.Signal_Strength, 
        record.Latency, record.Required_Bandwidth, record.Allocated_Bandwidth, record.Resource_Allocation
    ))
    conn.commit()
    conn.close()
    return record

# Update an existing record by ID
@app.put("/records/{record_id}")
def update_record(record_id: int, record: DataModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE data_table
        SET Timestamp = ?, User_ID = ?, Application_Type = ?, Signal_Strength = ?, 
            Latency = ?, Required_Bandwidth = ?, Allocated_Bandwidth = ?, Resource_Allocation = ?
        WHERE id = ?
    """, (
        record.Timestamp, record.User_ID, record.Application_Type, record.Signal_Strength, 
        record.Latency, record.Required_Bandwidth, record.Allocated_Bandwidth, record.Resource_Allocation, record_id
    ))
    conn.commit()
    conn.close()
    return record

# Delete a record by ID
@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM data_table WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return {"message": "Record deleted successfully"}

# To run the app, use: uvicorn main:app --reload
