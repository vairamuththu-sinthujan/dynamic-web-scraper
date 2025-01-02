import streamlit as st
import os
import pandas as pd
from datetime import datetime

def render_page():
    # Function to ensure the upload folder exists
    def create_upload_folder(folder_name="user_upload"):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    # Function to save uploaded files with user order preserved
    def save_files(uploaded_files, folder_name="user_upload"):
        create_upload_folder(folder_name)
        saved_file_paths = []
        for i, file in enumerate(uploaded_files):
            file_path = os.path.join(folder_name, f"{i+1:02d}_{file.name}")
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            saved_file_paths.append(file_path)
        return saved_file_paths

    # Function to generate a unique file name
    def generate_unique_filename(base_name, extension):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"

    # Function to merge CSV files
    def merge_csv_files(file_paths, output_folder="user_upload"):
        dfs = [pd.read_csv(file) for file in file_paths]
        merged_df = pd.concat(dfs, ignore_index=True)
        unique_file_name = generate_unique_filename("merged_csv", "csv")
        output_path = os.path.join(output_folder, unique_file_name)
        merged_df.to_csv(output_path, index=False)
        return output_path

    # Function to merge Excel files
    def merge_excel_files(file_paths, output_folder="user_upload"):
        dfs = [pd.read_excel(file) for file in file_paths]
        merged_df = pd.concat(dfs, ignore_index=True)
        unique_file_name = generate_unique_filename("merged_excel", "xlsx")
        output_path = os.path.join(output_folder, unique_file_name)
        merged_df.to_excel(output_path, index=False)
        return output_path

    # Function to clean up the upload folder
    def clean_upload_folder(folder_name="user_upload"):
        if os.path.exists(folder_name):
            for file in os.listdir(folder_name):
                file_path = os.path.join(folder_name, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            if not os.listdir(folder_name):
                os.rmdir(folder_name)  # Remove the folder if empty

    # Streamlit UI
    st.title("🖇️Merge Files")

    # Buttons for upload workflows
    choice = st.radio("Choose file type to upload and merge:", ["CSV", "Excel"])

    if choice == "CSV":
        csv_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)
        
        if len(csv_files) < 2:
            st.warning("You must upload at least 2 CSV files to merge.")
        elif len(csv_files) > 10:
            st.warning("You can upload a maximum of 10 CSV files.")
        else:
            if st.button("Merge CSV Files"):
                saved_csv_paths = save_files(csv_files)
                merged_csv_path = merge_csv_files(saved_csv_paths)
                st.success("CSV files merged successfully!")

                with open(merged_csv_path, "rb") as merged_file:
                    st.download_button(
                        "Download Merged CSV",
                        data=merged_file,
                        file_name=os.path.basename(merged_csv_path),
                        mime="text/csv"
                    )
                # Cleanup files and folder
                os.remove(merged_csv_path)
                for file_path in saved_csv_paths:
                    os.remove(file_path)
                clean_upload_folder()

    elif choice == "Excel":
        excel_files = st.file_uploader("Upload Excel files", type=["xls", "xlsx"], accept_multiple_files=True)
        
        if len(excel_files) < 2:
            st.warning("You must upload at least 2 Excel files to merge.")
        elif len(excel_files) > 10:
            st.warning("You can upload a maximum of 10 Excel files.")
        else:
            if st.button("Merge Excel Files"):
                saved_excel_paths = save_files(excel_files)
                merged_excel_path = merge_excel_files(saved_excel_paths)
                st.success("Excel files merged successfully!")

                with open(merged_excel_path, "rb") as merged_file:
                    st.download_button(
                        "Download Merged Excel",
                        data=merged_file,
                        file_name=os.path.basename(merged_excel_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                # Cleanup files and folder
                os.remove(merged_excel_path)
                for file_path in saved_excel_paths:
                    os.remove(file_path)
                clean_upload_folder()

    st.warning("""
        1. Ensure Compatibility: Both files should have a similar structure (e.g., same column names).\n
        2. Consistent File Formats: Ensure both files are in .xlsx or .xls or .csv format.
    """)
