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
# SNOWFLAKE CONNECTION
# --------------------------------------------------

cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# CUSTOMER NAME
# --------------------------------------------------

name_on_order = st.text_input(
    "Name on Smoothie:"
)

try:

    # --------------------------------------------------
    # LOAD FRUIT DATA
    # --------------------------------------------------

    fruit_df = (
        session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
        .select(
            col("FRUIT_NAME"),
            col("SEARCH_ON")
        )
    )

    pd_df = fruit_df.to_pandas()

    fruit_list = pd_df["FRUIT_NAME"].tolist()

    # --------------------------------------------------
    # MULTISELECT
    # --------------------------------------------------

    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_list,
        max_selections=5
    )

    # --------------------------------------------------
    # NUTRITION SECTION
    # --------------------------------------------------

    if ingredients_list:

        ingredients_string = ", ".join(
            ingredients_list
        )

        st.subheader(
            "Nutrition Information"
        )

        for fruit_chosen in ingredients_list:

            search_on = pd_df.loc[
                pd_df["FRUIT_NAME"] == fruit_chosen,
                "SEARCH_ON"
            ].iloc[0]

            if (
                pd.isna(search_on)
                or search_on == ""
            ):
                search_on = fruit_chosen

            st.write(
                "The search value for",
                fruit_chosen,
                "is",
                search_on
            )

            api_url = (
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            try:

                response = requests.get(
                    api_url,
                    timeout=10
                )

                if response.status_code == 200:

                    st.dataframe(
                        response.json(),
                        use_container_width=True
                    )

                else:

                    st.warning(
                        f"Unable to retrieve nutrition data for {fruit_chosen}"
                    )

            except Exception as api_error:

                st.warning(
                    f"API error for {fruit_chosen}: {api_error}"
                )

        st.write(
            "Selected Ingredients:"
        )

        st.write(
            ingredients_string
        )

        # --------------------------------------------------
        # SUBMIT ORDER
        # --------------------------------------------------

        if st.button(
            "Submit Order"
        ):

            if not name_on_order:

                st.warning(
                    "Please enter a name."
                )

            else:

                safe_name = (
                    name_on_order.replace(
                        "'",
                        "''"
                    )
                )

                safe_ingredients = (
                    ingredients_string.replace(
                        "'",
                        "''"
                    )
                )

                insert_stmt = f"""
                INSERT INTO SMOOTHIES.PUBLIC.ORDERS
                (
                    INGREDIENTS,
                    NAME_ON_ORDER,
                    ORDER_FILLED
                )
                VALUES
                (
                    '{safe_ingredients}',
                    '{safe_name}',
                    FALSE
                )
                """

                session.sql(
                    insert_stmt
                ).collect()

                st.success(
                    f"✅ Your Smoothie is ordered, {name_on_order}!"
                )

except Exception as e:

    st.error(
        f"Application Error: {e}"
    )

# --------------------------------------------------
# ORDER MANAGEMENT
# --------------------------------------------------

st.divider()

st.header(
    "Order Management"
)

try:

    orders_df = (
        session.table(
            "SMOOTHIES.PUBLIC.ORDERS"
        )
    )

    st.dataframe(
        orders_df.to_pandas(),
        use_container_width=True
    )

    unfilled_orders = (
        session.table(
            "SMOOTHIES.PUBLIC.ORDERS"
        )
        .filter(
            col("ORDER_FILLED") == False
        )
        .select(
            col("NAME_ON_ORDER")
        )
        .collect()
    )

    order_names = [
        row["NAME_ON_ORDER"]
        for row in unfilled_orders
    ]

    if order_names:

        selected_order = st.selectbox(
            "Select an order to mark as filled:",
            order_names
        )

        if st.button(
            "✅ Mark Order as Filled"
        ):

            update_stmt = f"""
            UPDATE SMOOTHIES.PUBLIC.ORDERS
            SET ORDER_FILLED = TRUE
            WHERE NAME_ON_ORDER =
            '{selected_order.replace("'", "''")}'
            """

            session.sql(
                update_stmt
            ).collect()

            st.success(
                f"Order for {selected_order} marked as filled."
            )

            st.rerun()

    else:

        st.info(
            "No open orders found."
        )

except Exception as e:

    st.error(
        f"Order Management Error: {e}"
    )
