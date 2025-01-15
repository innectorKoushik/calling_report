import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from pathlib import Path

def main():
    st.set_page_config(page_title="Lead Analysis Dashboard", layout="wide")
    st.title("Lead Analysis Dashboard")

    # File upload
    uploaded_file = st.file_uploader("Upload your lead data CSV", type=['csv'])

    if uploaded_file is not None:
        # Read the data
        df = pd.read_csv(uploaded_file)

        # Sidebar filters
        st.sidebar.header("Filters")

        # Lead Source filter with "Select All" option
        all_sources = df['Lead Source'].unique()
        if st.sidebar.button("Select All Lead Sources"):
            selected_sources = all_sources.tolist()
        else:
            selected_sources = st.sidebar.multiselect(
                "Select Lead Source", options=all_sources, default=all_sources.tolist()
            )

        # Filter the dataframe
        filtered_df = df[df['Lead Source'].isin(selected_sources)]

        # Value counts for Lead Stage with hierarchical grouping
        lead_stage_counts = filtered_df.groupby(['Lead Stage', 'Lead Source']).size().reset_index(name='Count')

        # Visualization: Lead Stage Distribution
        st.header("Lead Stage Distribution")
        fig_stage = px.bar(
            lead_stage_counts,
            x='Lead Stage',
            y='Count',
            color='Lead Source',
            title='Lead Stage Distribution with Lead Source',
            barmode='stack'
        )
        st.plotly_chart(fig_stage)

        # Hierarchical grouping visualization
        st.header("Hierarchical View of Leads")
        fig_hierarchy = px.sunburst(
            filtered_df,
            path=['Group', 'Lead Type', 'Owner'],
            values=None,
            title='Hierarchical Grouping of Leads'
        )
        st.plotly_chart(fig_hierarchy)

        # Display filtered data table (optional)
        st.header("Filtered Data")
        st.dataframe(filtered_df[['Lead Source', 'Lead Stage']])  # Display relevant columns

if __name__ == "__main__":
    main()
