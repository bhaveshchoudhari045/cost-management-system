# TODO for Cost Management Web App

- [x] Import necessary modules (datetime, os, tempfile)
- [x] Initialize session state for carts list
- [x] Display "Cost Management" title at top center with pretty font and margin
- [x] Display existing carts in columns (image, price in rupees, date, cost_per_day) with borders, glow, hover, zoom
- [x] Add plus button fixed at right corner of screen, styled as blue button with white text
- [x] Handle plus button: show form in sidebar for inputs
- [x] Form: file uploader for image, number input for price, date input for buy date, submit button
- [x] On submit: calculate days since buy, cost_per_day, save image to temp, add to carts list
- [x] Limit to 5 carts per row, align left to right, fix overlapping
- [x] Increase cart size, add blur and random glow effects, ensure data shown inside cart
- [x] Ensure images have same size and dimensions
- [x] Test the app by running streamlit run app.py
- [x] Add import base64 for image embedding
- [x] Change cart display to use flexbox for alignment and gaps
- [x] Encode images to base64 and embed in HTML div
- [x] Remove st.image and place content inside cart div
- [x] Remove blue button and use standard Streamlit button
- [x] Test the fixes for alignment, gaps, and content display
