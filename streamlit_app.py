import streamlit as st
import pandas as pd
import requests

from snowflake.snowpark.functions import col

# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------------------------
# CUSTOMER NAME
# --------------------------------------------------

name_on_order = st.text_input(
    "Name on Smoothie:"
)

# --------------------------------------------------
# SNOWFLAKE CONNECTION
# --------------------------------------------------

cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# LOAD FRUIT OPTIONS
# --------------------------------------------------

try:

    fruit_df = (
        session.table(
            "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
        )
        .select(
            col("FRUIT_NAME"),
            col("SEARCH_ON")
        )
    )

    # Convert to Pandas DataFrame
    pd_df = fruit_df.to_pandas()

    # Fruit list for dropdown
    fruit_list = pd_df["FRUIT_NAME"].tolist()

    # --------------------------------------------------
    # MULTISELECT
    # --------------------------------------------------

    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_list,
        max_selections=5
    )

    if ingredients_list:

        ingredients_string = ", ".join(
            ingredients_list
        )

        st.header("Nutrition Information")

        for fruit_chosen in ingredients_list:

            # -------------------------------------------
            # SEARCH_ON LOOKUP
            # -------------------------------------------

            search_on = pd_df.loc[
                pd_df["FRUIT_NAME"] == fruit_chosen,
                "SEARCH_ON"
            ].iloc[0]

            # Fallback if SEARCH_ON is empty
            if pd.isna(search_on) or search_on == "":
                search_on = fruit_chosen

            st.write(
                "The search value for",
                fruit_chosen,
                "is",
                search_on
            )

            api_url = (
                f"https://my.smoothiefroot.com/"
                f"api/fruit/{search_on}"
            )

            st.write("Calling:", api_url)

            try:

                response = requests.get(
                    api_url,
                    timeout=10
                )

                if response.status_code == 200:

                    st.subheader(
                        f"{fruit_chosen} Nutrition Information"
                    )

                    st.dataframe(
                        response.json(),
                        use_container_width=True
                    )

                else:

                    st.warning(
                        f"Could not retrieve nutrition "
                        f"information for {fruit_chosen}"
                    )

            except Exception as api_error:

                st.error(
                    f"API Error for {fruit_chosen}: "
                    f"{api_error}"
                )

        # -------------------------------------------
        # SHOW CHOSEN INGREDIENTS
