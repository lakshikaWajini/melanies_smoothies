# Import packages
import streamlit as st
from snowflake.snowpark.functions import col

# Page title
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothies:")

st.write("The name on your smoothie will be:", name_on_order)

# Get Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

try:
    # Read available fruits
    fruit_df = (
        session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
        .select(col("FRUIT_NAME"))
    )

    # Convert Snowpark DataFrame to Python list
    fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

    # Multi-select widget
    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_list,
        max_selections=5
    )

    # Process order
    if ingredients_list:

        ingredients_string = ", ".join(ingredients_list)

        st.write("Selected ingredients:")
        st.write(ingredients_string)

        # Create INSERT statement
        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
        (INGREDIENTS, NAME_ON_ORDER)
        VALUES
        ('{ingredients_string}', '{name_on_order}')
        """

        # Show generated SQL for debugging
       # st.write(my_insert_stmt)

        if st.button("Submit Order"):

            session.sql(my_insert_stmt).collect()

            st.success(
                f"✅ Your Smoothie is ordered, {name_on_order}!"
            )

except Exception as e:
    st.error(f"Error: {e}")

#new section to  display smoothiefroot nutrition information
import requests  
smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
st.text(smoothiefroot_response.json())
