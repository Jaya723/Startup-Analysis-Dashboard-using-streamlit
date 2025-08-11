import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt



df=pd.read_csv("startup_cleaned.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year
st.set_page_config(page_title="startup Funding Analysis")

def load_overall_analysis():
    st.title("Overall Analysis of startup Funding")
    total=round(df['amount'].sum())
    maximum_investment=df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    no_start=df['startup'].nunique()
    average_funding=df.groupby('startup')['amount'].sum().mean()
    
    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.markdown("**Total Money Invested till now**")
        st.metric(label="", value=str(total)+ ' Cr')
    with col2:
        st.markdown("**Maximum Investment till now**")
        st.metric(label="", value=str(maximum_investment)+ ' Cr')
    with col3:
        st.markdown("**Average funding a startup needs**")
        st.metric(label="", value=str(round(average_funding,2)) + ' Cr')
    with col4:
        st.markdown("**Total Number of Startups Funded**")
        st.metric(label="", value=no_start) 
    
    st.header('MOM graph(Month on Month Analysis)')
    option=st.selectbox('Select Type',['Total','Count'])
    if option=='Total':
        temp_df = df.groupby(['year','month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year','month'])['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')  

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(temp_df['x_axis'],temp_df['amount'])
    ax.set_xticklabels(temp_df['x_axis'], rotation=45, ha='right')  
    fig.tight_layout()  
    st.pyplot(fig)
    
        
def load_investor_details(investor_name):
    st.title(f"Investor Details for {investor_name}")
    last5_in=df[df['investors'].str.contains(investor_name)].head(5)[['date','startup','vertical','city','round','amount']]
    st.subheader(f"Investments by the {investor_name}")
    st.dataframe(last5_in)
    
    
    big_series=df[df['investors'].str.contains(investor_name)].groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
    st.subheader(f"Biggest Investments by the {investor_name}")
    fig, ax = plt.subplots(figsize=(10, 6))  
    ax.bar(big_series.index, big_series.values)
    ax.set_xticklabels(big_series.index, rotation=45, ha='right')  
    fig.tight_layout()  
    st.pyplot(fig)
    
    vertical_series=df[df['investors'].str.contains(investor_name)].groupby('vertical')['amount'].sum()
    st.subheader(f"Investment by {investor_name} in different verticals")
    fig, ax1 = plt.subplots()
    ax1.pie(vertical_series,labels=vertical_series.index, autopct='%0.001f%%')
    st.pyplot(fig)
    
    year_series=df[df['investors'].str.contains(investor_name)].groupby('year')['amount'].sum()
    st.subheader('YoY(Year on Year) Growth of Investments')
    fig2, ax2 = plt.subplots()
    ax2.plot(year_series.index,year_series.values)
    st.pyplot(fig2)


st.sidebar.title("startup Funding Analysis")
option=st.sidebar.selectbox("Select an option", ["Overall Analysis", "startup Analysis", "Investor Analysis"])

if option=="Overall Analysis":
    load_overall_analysis()

elif option=="startup Analysis":
    st.sidebar.selectbox("select startup",sorted(df['startup'].unique().tolist()))
    st.title("startup Analysis")
    st.write("This section focuses on individual startups, analyzing their funding history, growth patterns, and sector-specific insights.")
    st.sidebar.button("Show startup Details")
    
elif option=="Investor Analysis":
    selected_investor=st.sidebar.selectbox("select Investor",sorted(set(df['investors'].str.split(',').sum())))
    b2=st.sidebar.button("Show Investor Details")
    if b2:
        load_investor_details(selected_investor)
    
