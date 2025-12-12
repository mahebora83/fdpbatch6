import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Student Management", layout="wide")

# ===========================
# DATABASE FUNCTIONS
# ===========================

def get_connection():
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect('data.db')
    return conn


def create_table():
    """Create the students table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def insert_student(name, email, phone, age):
    """Insert a new student record into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO students (name, email, phone, age)
            VALUES (?, ?, ?, ?)
        ''', (name, email, phone, age))
        
        conn.commit()
        st.success("✅ Student added successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error adding student: {str(e)}")
        return False
    finally:
        conn.close()


def view_all_students():
    """Retrieve all student records from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name, email, phone, age FROM students')
        records = cursor.fetchall()
        
        if records:
            df = pd.DataFrame(records, columns=['ID', 'Name', 'Email', 'Phone', 'Age'])
            return df
        else:
            return None
    except Exception as e:
        st.error(f"❌ Error retrieving records: {str(e)}")
        return None
    finally:
        conn.close()


def get_student_by_id(student_id):
    """Retrieve a specific student record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name, email, phone, age FROM students WHERE id = ?', (student_id,))
        record = cursor.fetchone()
        return record
    except Exception as e:
        st.error(f"❌ Error retrieving student: {str(e)}")
        return None
    finally:
        conn.close()


def get_all_student_ids():
    """Get a list of all student IDs and names for selection."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name FROM students ORDER BY name')
        records = cursor.fetchall()
        return records
    except Exception as e:
        st.error(f"❌ Error retrieving student list: {str(e)}")
        return []
    finally:
        conn.close()


def update_student(student_id, name, email, phone, age):
    """Update an existing student record."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE students
            SET name = ?, email = ?, phone = ?, age = ?
            WHERE id = ?
        ''', (name, email, phone, age, student_id))
        
        conn.commit()
        st.success("✅ Student updated successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error updating student: {str(e)}")
        return False
    finally:
        conn.close()


def delete_student(student_id):
    """Delete a student record from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        st.success("✅ Student deleted successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error deleting student: {str(e)}")
        return False
    finally:
        conn.close()


# ===========================
# INITIALIZE DATABASE
# ===========================

# Create table on app startup
create_table()


# ===========================
# STREAMLIT UI
# ===========================

st.title("📚 Student Management System")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("Navigation")
operation = st.sidebar.radio(
    "Select Operation",
    ["📖 View All", "➕ Add Student", "✏️ Update Student", "🗑️ Delete Student"]
)

# ===========================
# VIEW ALL STUDENTS
# ===========================
if operation == "📖 View All":
    st.header("View All Students")
    
    df = view_all_students()
    
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.info(f"Total Students: {len(df)}")
    else:
        st.info("📭 No students found in the database.")


# ===========================
# ADD NEW STUDENT
# ===========================
elif operation == "➕ Add Student":
    st.header("Add New Student")
    
    with st.form("add_student_form"):
        name = st.text_input("Full Name", placeholder="Enter student name")
        email = st.text_input("Email", placeholder="Enter email address")
        phone = st.text_input("Phone Number", placeholder="Enter phone number")
        age = st.number_input("Age", min_value=1, max_value=100, step=1)
        
        submit_btn = st.form_submit_button("➕ Add Student", use_container_width=True)
        
        if submit_btn:
            if name and email and phone and age:
                insert_student(name, email, phone, age)
            else:
                st.error("❌ Please fill in all fields!")


# ===========================
# UPDATE STUDENT
# ===========================
elif operation == "✏️ Update Student":
    st.header("Update Student Record")
    
    students = get_all_student_ids()
    
    if students:
        # Create a selection option (ID - Name)
        options = [f"{student[0]} - {student[1]}" for student in students]
        selected = st.selectbox("Select Student to Update", options)
        
        # Extract the student ID from the selection
        student_id = int(selected.split(" - ")[0])
        
        # Get the current student data
        student = get_student_by_id(student_id)
        
        if student:
            st.info(f"Editing: {student[1]}")
            
            with st.form("update_student_form"):
                name = st.text_input("Full Name", value=student[1])
                email = st.text_input("Email", value=student[2])
                phone = st.text_input("Phone Number", value=student[3])
                age = st.number_input("Age", value=student[4], min_value=1, max_value=100, step=1)
                
                submit_btn = st.form_submit_button("✏️ Update Student", use_container_width=True)
                
                if submit_btn:
                    if name and email and phone and age:
                        update_student(student_id, name, email, phone, age)
                    else:
                        st.error("❌ Please fill in all fields!")
    else:
        st.info("📭 No students found. Please add a student first.")


# ===========================
# DELETE STUDENT
# ===========================
elif operation == "🗑️ Delete Student":
    st.header("Delete Student Record")
    
    students = get_all_student_ids()
    
    if students:
        # Create a selection option (ID - Name)
        options = [f"{student[0]} - {student[1]}" for student in students]
        selected = st.selectbox("Select Student to Delete", options)
        
        # Extract the student ID from the selection
        student_id = int(selected.split(" - ")[0])
        
        # Get the current student data for confirmation
        student = get_student_by_id(student_id)
        
        if student:
            st.warning(f"⚠️ Are you sure you want to delete: **{student[1]}**?")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Confirm Delete", use_container_width=True, type="secondary"):
                    delete_student(student_id)
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.info("Deletion cancelled.")
    else:
        st.info("📭 No students found. Please add a student first.")


# ===========================
# FOOTER
# ===========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <p>Student Management System v1.0 | Powered by Streamlit & SQLite3</p>
</div>
""", unsafe_allow_html=True)
