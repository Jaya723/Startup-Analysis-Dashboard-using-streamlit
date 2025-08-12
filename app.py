import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt



def load_data():
    df = pd.read_csv("startup_cleaned.csv")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    return df

df = load_data()
st.set_page_config(page_title="Startup Funding Analysis", layout="wide")


def format_cr(amount):
    """Format numbers with Cr suffix and commas."""
    return f"{amount:,.0f} Cr"

def plot_bar(x, y, title, xlabel="", ylabel="", rotation=45):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, y, color="skyblue", edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(x, rotation=rotation, ha='right')
    fig.tight_layout()
    st.pyplot(fig)

def plot_line(x, y, title, xlabel="", ylabel="", rotation=45):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, marker="o", color="orange")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(x, rotation=rotation, ha='right')
    fig.tight_layout()
    st.pyplot(fig)

def load_overall_analysis():
    st.title("📊 Overall Analysis of Startup Funding")
    total = round(df['amount'].sum())
    maximum_investment = df.groupby('startup')['amount'].max().max()
    no_startups = df['startup'].nunique()
    average_funding = df.groupby('startup')['amount'].sum().mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Money Invested", format_cr(total))
    col2.metric("Max Investment in a Single Round", format_cr(maximum_investment))
    col3.metric("Average Funding per Startup", format_cr(round(average_funding, 2)))
    col4.metric("Total Startups Funded", no_startups)


    st.subheader("📈 Month-on-Month Analysis")
    option = st.selectbox('Select Type', ['Total', 'Count'])
    temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index() if option == 'Total' else df.groupby(['year', 'month'])['amount'].count().reset_index()
    temp_df['x_axis'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)
    plot_line(temp_df['x_axis'], temp_df['amount'], f"{option} Funding Over Time", "Month-Year", option)

    st.subheader("🏢 Top 20 Verticals by Number of Startups")
    industry = df.groupby('vertical')['startup'].count().sort_values(ascending=False).head(20)
    plot_bar(industry.index, industry.values, "Top 20 Verticals", "Vertical", "Count")


def load_startup_analysis(startup):
    st.title(f"🏢 Startup Analysis: {startup}")
    startup_df = df[df['startup'].str.contains(startup)]
    if startup_df.empty:
        st.warning("No data available for this startup.")
        return
    else:
        vertical = startup_df['vertical'].iloc[0]
        subvertical = startup_df['subvertical'].iloc[0]

        st.subheader("🤝 Similar Companies")
        similar_df = df[
            (df['vertical'] == vertical) &
            (df['subvertical'] == subvertical) &
            (~df['startup'].str.contains(startup))
        ][['startup', 'vertical', 'subvertical', 'city']].drop_duplicates().head(10)

        if not similar_df.empty:
            st.dataframe(similar_df)
        else:
            st.info("No similar companies found in this category.")
        

    st.subheader("Recent Funding Rounds")
    st.dataframe(startup_df[['date', 'startup', 'vertical', 'subvertical', 'city', 'round', 'amount']].head(5))

    monthly_funding = startup_df.groupby('month')['amount'].sum()
    plot_line(monthly_funding.index, monthly_funding.values, f"{startup} - Monthly Funding", "Month", "Amount (Cr)")

    yearly_funding = startup_df.groupby('year')['amount'].sum()
    plot_bar(yearly_funding.index, yearly_funding.values, f"{startup} - Yearly Funding", "Year", "Amount (Cr)", rotation=0)

def load_investor_details(investor_name):
    st.title(f"💰 Investor Analysis: {investor_name}")
    investor_df = df[df['investors'].str.contains(investor_name)]
    if investor_df.empty:
        st.warning("No data available for this investor.")
        return

    st.subheader("Recent Investments")
    st.dataframe(investor_df[['date', 'startup', 'vertical', 'city', 'round', 'amount']].head(5))

    big_investments = investor_df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
    plot_bar(big_investments.index, big_investments.values, f"Top Investments by {investor_name}", "Startup", "Amount (Cr)")

    vertical_investments = investor_df.groupby('vertical')['amount'].sum()
    st.subheader(f"Investments by {investor_name} in Different Verticals")
    fig, ax = plt.subplots()
    ax.pie(vertical_investments, labels=vertical_investments.index, autopct='%1.1f%%', startangle=90)
    st.pyplot(fig)

    year_series = investor_df.groupby('year')['amount'].sum()
    plot_line(year_series.index, year_series.values, "Year-on-Year Investment Growth", "Year", "Amount (Cr)", rotation=0)


st.sidebar.title("📊 Startup Funding Dashboard")
option = st.sidebar.selectbox("Select an option", ["Overall Analysis", "Startup Analysis", "Investor Analysis"])

if option == "Overall Analysis":
    load_overall_analysis()
elif option == "Startup Analysis":
    selected_startup = st.sidebar.selectbox("Select Startup", sorted(df['startup'].unique().tolist()))
    if st.sidebar.button("Show Startup Details"):
        load_startup_analysis(selected_startup)
elif option == "Investor Analysis":
    investors_list = sorted(set(df['investors'].str.split(',').sum()))
    selected_investor = st.sidebar.selectbox("Select Investor", investors_list)
    if st.sidebar.button("Show Investor Details"):
        load_investor_details(selected_investor)
