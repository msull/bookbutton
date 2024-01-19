import json
import urllib.request
from random import Random, choice

import streamlit as st


@st.cache_data()
def fetch_json(url):
    try:
        with urllib.request.urlopen(url) as response:
            # Check if the response is successful (HTTP 200 OK)
            if response.status == 200:
                data = response.read()
                json_data = json.loads(data)
                return json_data
            else:
                return f"Error: HTTP {response.status}"
    except Exception as e:
        return f"Error: {e}"


class Consts:
    data_url_base = "https://d1qi7pnap4qiwq.cloudfront.net/bookbutton/"
    data_url = data_url_base + "data.json"


def main():
    available_books: dict = fetch_json(Consts.data_url)
    _, col, _ = st.columns((1, 2, 1))
    with col:
        if st.button("BOOK BUTTON", use_container_width=True, type='primary'):
            st.session_state.book_choice = choice(list(available_books.keys()))

        if book_choice := st.session_state.get("book_choice"):
            title = book_choice.replace("-", " ").title()
            book = available_books[book_choice]


            st.header(title)
            if image_name := book["png"]:
                st.image(Consts.data_url_base + image_name, width=400)
            st.audio(Consts.data_url_base + book["m4a"])


if __name__ == "__main__":
    main()

