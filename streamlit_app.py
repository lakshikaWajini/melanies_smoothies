# Import packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# ----------------------------
# Page Title
# ----------------------------
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# ----------------------------
# Name Input
# ----------------------------
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write("The name on your smoothie will be:", name_on_order)

# ----------------------------
# Snowflake Connection
# ----------------------------
cnx = st.connection("snowflake")
session = cnx.session()

try:

    # ----------------------------
    # Read Fruits from Snowflake
    # ----------------------------
    fruit_df = (
        session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
        .select(
            col("FRUIT_NAME"),
            col("SEARCH_ON")
        )
    )

    fruit_rows = fruit_df.collect()

    # Display values in dropdown
    fruit_list = [
        row["FRUIT_NAME"]
        for row in fruit_rows
    ]

    # Map GUI value to API value
    fruit_search_map = {
        row["FRUIT_NAME"]: row["SEARCH_ON"]
        for row in fruit_rows
    }

    # ----------------------------
    # Fruit Selection
    # ----------------------------
    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        options=fruit_list,
        max_selections=5
    )

    # ----------------------------
    # Display Nutrition Data
    # ----------------------------
    if ingredients_list:

        ingredients_string = ", ".join(ingredients_list)

        st.subheader("Nutrition Information")

        for fruit_chosen in ingredients_list:

            search_value = fruit_search_map.get(
                fruit_chosen,
                fruit_chosen
            )

            st.markdown(f"### {fruit_chosen}")

            try:

                api_url = (
                    f"https://my.smoothiefroot.com/api/fruit/{search_value}"
                )

                response = requests.get(api_url)

                if response.status_code == 200:

                    st.dataframe(
                        response.json(),
                        use_container_width=True
                    )

                else:

                    st.warning(
                        f"No nutrition data found for {fruit_chosen}"
                    )

            except Exception as api_error:

                st.error(
                    f"API Error for {fruit_chosen}: {api_error}"
                )

        # ----------------------------
        # Show Selections
        # ----------------------------
        st.write("Selected ingredients:")
        st.write(ingredients_string)

        # ----------------------------
        # Submit Order
        # ----------------------------
        if st.button("Submit Order"):

            if not name_on_order:

                st.warning(
                    "Please enter a name before submitting."
                )

            else:

                # Escape single quotes
                safe_name = name_on_order.replace("'", "''")
                safe_ingredients = ingredients_string.replace(
                    "'",
                    "''"
                )

                insert_stmt = f"""
                INSERT INTO SMOOTHIES.PUBLIC.ORDERS
                (
                    INGREDIENTS,
                    NAME_ON_ORDER
                )
                VALUES
                (
                    '{safe_ingredients}',
                    '{safe_name}'
                )
                """

                session.sql(insert_stmt).collect()

                st.success(
                    f"✅ Your Smoothie is ordered, {name_on_order}!"
                )

except Exception as e:

    st.error(f"Application Error: {e}")
except Exception as e:
    st.error(f"Error: {e}")


 
