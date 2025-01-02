# Streamlit app
import os
import streamlit as st
from scrape_clean import scrape_and_clean_all
from ai import interact_with_ai, convert_ai_response_to_df  # Importing interact_with_ai from ai.py
from datetime import datetime

def render_page():
    st.title("💬Web Scraper")

    # Initialize session state for scraped data, chat history, and AI responses
    if 'scraped_data' not in st.session_state:
        st.session_state.scraped_data = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Input field for URL
    url = st.text_input("🌐 Enter the URL to scrape:")
    wait_key = st.slider("⏳ Choose a wait time for the site to load (in seconds):", min_value=20, max_value=600, value=60)
    st.write(f"Your chosen wait time: {wait_key} seconds")

    # Button to trigger scraping
    if st.button("Scrape"):
        if url:
            with st.spinner("Scraping...⛏️"):
                st.session_state.scraped_data = scrape_and_clean_all(url, wait_key)

    # Display scraped data only after scraping
    if st.session_state.scraped_data:
        with st.expander('📜 View Scraped Result'):
            st.text_area("Scraped Data", st.session_state.scraped_data, height=400, key="scraped_data_display")

        # Chatbox-like interaction area
        st.subheader("💡 Chat with Gemini AI")
        user_input = st.text_area("Your Message:", key="chat_input", placeholder="Type your question here...")

        # Submit button for the chat
        if st.button("Send", key="send_message"):
            if user_input:
                with st.spinner("Gemini is thinking...🤖"):
                    try:
                        # Get AI response
                        ai_response = interact_with_ai(st.session_state.scraped_data, user_input)
                        # Append user input to chat history
                        st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
                        st.session_state.chat_history.append({"role": "model", "parts": [ai_response]})
                    except Exception as e:
                        st.error(f"Error interacting with Gemini: {str(e)} 🚨")

        # Display chat history in a structured layout
        if st.session_state.chat_history:
            with st.expander(label='chat history'):
                #st.subheader("📜 Chat History")
                for chat in st.session_state.chat_history:
                    if chat["role"] == "user":
                        st.markdown(f"**You:** {chat['parts'][0]}")
                    else:
                        st.markdown(f"**Gemini AI:** {chat['parts'][0]}")

        # Convert the last AI response to Excel and CSV files
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "model":
            last_response = st.session_state.chat_history[-1]["parts"][0]
            # Convert AI response to DataFrame
            df = convert_ai_response_to_df(last_response)
            with st.expander(label='Preview Data Frame'):
                st.table(df)

            # Generate unique file names
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            excel_path = os.path.join('sheets', f'gemini_chat_{timestamp}.xlsx')
            csv_path = os.path.join('sheets', f'gemini_chat_{timestamp}.csv')

            # Add buttons for downloading Excel and CSV
            if st.button("Convert to spreadsheet📥"):
                try:
                    os.makedirs('sheets', exist_ok=True)
                    df.to_excel(excel_path, index=False, header=True)

                    with open(excel_path, "rb") as excel_file:
                        st.download_button(
                            label="Download Excel File 📥",
                            data=excel_file,
                            file_name=os.path.basename(excel_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    os.remove(excel_path)
                    if not os.listdir('sheets'):
                        os.rmdir('sheets')

                except Exception as e:
                    st.error(f"Error processing Excel file: {str(e)} 🚨")

            if st.button("Convert to CSV📥"):
                try:
                    os.makedirs('sheets', exist_ok=True)
                    df.to_csv(csv_path, index=False)

                    with open(csv_path, "rb") as csv_file:
                        st.download_button(
                            label="Download CSV File 📥",
                            data=csv_file,
                            file_name=os.path.basename(csv_path),
                            mime="text/csv"
                        )
                    os.remove(csv_path)
                    if not os.listdir('sheets'):
                        os.rmdir('sheets')

                except Exception as e:
                    st.error(f"Error processing files: {str(e)} 🚨")
