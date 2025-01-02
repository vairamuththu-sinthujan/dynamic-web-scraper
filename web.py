import streamlit as st
from streamlit.runtime.scriptrunner import RerunData, RerunException

def main():
    # Define your pages
    def scrap_page():
        import page1 as page1
        page1.render_page()

    def upload_page():
        import page2 as page2
        page2.render_page()


    # Add navigation menu
    pages = {
        "⛏️ Scrap": scrap_page,
        "🖇️ Merge": upload_page
    }

    st.sidebar.title("Navigation")
    # Updated key to be more unique
    selection = st.sidebar.radio("Go to", list(pages.keys()), key="navigation_radio")

    # Call the selected page
    try:
        pages[selection]()
    except RerunException as e:
        raise RerunException(e.rerun_data if e.rerun_data else RerunData())

