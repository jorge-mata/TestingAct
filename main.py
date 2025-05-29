import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

def normalize_text(text):
    # Normalize string by removing accents and converting to lowercase.
    text = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8')
    return text.lower()

@st.cache_data
def load_data():
    # Load seller data from Excel file.
    return pd.read_excel("sellers.xlsx")

def apply_region_filter(data):
    # Display region filter and return filtered DataFrame.
  
    st.subheader("Filter by Region")
    regions = data["REGION"].unique()
    selected_region = st.selectbox("Select Region", ["All"] + list(regions))
    if selected_region != "All":
        return data[data["REGION"] == selected_region], selected_region
    return data, "All"

# ---------------------------
# Main App
# ---------------------------

# Load dataset
df = load_data()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Table", "Sales Dashboard", "Vendor Lookup"])

# ---------------------------
# Page: Data Table
# ---------------------------

if page == "Data Table":
    st.title("📄 Seller Data Table")
    filtered_df, selected_region = apply_region_filter(df)
    st.write(f"Showing data for region: **{selected_region}**")
    st.dataframe(filtered_df)

# ---------------------------
# Page: Sales Dashboard
# ---------------------------

elif page == "Sales Dashboard":
    st.title("📈 Sales Dashboard")
    filtered_df, selected_region = apply_region_filter(df)

    # Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Units Sold", int(filtered_df["UNIDADES VENDIDAS"].sum()))
    with col2:
        st.metric("Total Sales", f"${filtered_df['VENTAS TOTALES'].sum():,.2f}")
    with col3:
        st.metric("Avg Sales", f"${filtered_df['VENTAS TOTALES'].mean():,.2f}")

    # Charts
    st.write("### Units Sold by Seller")
    fig1 = px.bar(filtered_df, x="NOMBRE", y="UNIDADES VENDIDAS", color="REGION")
    st.plotly_chart(fig1)

    st.write("### Total Sales by Seller")
    fig2 = px.bar(filtered_df, x="NOMBRE", y="VENTAS TOTALES", color="REGION")
    st.plotly_chart(fig2)

# ---------------------------
# Page: Vendor Lookup
# ---------------------------

elif page == "Vendor Lookup":
    st.title("🔍 Vendor Lookup")
    search_input = st.text_input("Enter vendor name (first or last, partial ok)")

    if search_input:
        normalized_input = normalize_text(search_input)

        # Create normalized full name for partial matching
        df["FULL_NAME_NORM"] = (df["NOMBRE"] + " " + df["APELLIDO"]).apply(normalize_text)

        # Filter using normalized partial match
        vendor_data = df[df["FULL_NAME_NORM"].str.contains(normalized_input, na=False)].drop(columns=["FULL_NAME_NORM"])

        if not vendor_data.empty:
            st.success(f"Found {len(vendor_data)} result(s) for '{search_input}'")
            st.dataframe(vendor_data)
        else:
            st.warning("Vendor not found.")