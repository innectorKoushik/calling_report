hrimport streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
            path=['Group', 'Owner', 'Lead Stage'],
            values=None,
            title='Hierarchical Grouping of Leads'
        )
        st.plotly_chart(fig_hierarchy)

        # Interactive section for hierarchical value counts
        if st.button("Show Value Counts for Hierarchical View"):
            st.header("Hierarchical Value Counts")
            hierarchical_counts = filtered_df.groupby(
                ['Group', 'Lead Type', 'Owner', 'Lead Stage']
            ).size().reset_index(name='Count')
            st.dataframe(hierarchical_counts)  # Display the grouped value counts
        else:
            # Default display: Filtered data table
            st.header("Filtered Data")
            st.dataframe(filtered_df[['Lead Source', 'Lead Stage']])  # Display relevant columns

        # Additional Visualizations
        st.header("Enhanced Visualizations")

        # Donut Chart: Lead Stage Distribution
        stage_distribution = filtered_df['Lead Stage'].value_counts().reset_index()
        stage_distribution.columns = ['Lead Stage', 'Count']
        stage_distribution['Percentage'] = (stage_distribution['Count'] / stage_distribution['Count'].sum() * 100).round(1)
        fig_donut = go.Figure(data=[
            go.Pie(
                labels=stage_distribution['Lead Stage'],
                values=stage_distribution['Count'],
                hole=.5,
                hoverinfo='label+percent+value',
                textinfo='label+percent'
            )
        ])
        fig_donut.update_layout(title_text="Lead Stage Distribution (Donut Chart)")
        st.plotly_chart(fig_donut)

        # Bar Chart: Lead Source Conversion Rates
        lead_source_metrics = filtered_df.groupby('Lead Source').agg({'Lead Stage': 'count'}).reset_index()
        lead_source_metrics.columns = ['Lead Source', 'Total Leads']
        lead_source_metrics['Conversion Rate (%)'] = (
            filtered_df[filtered_df['Lead Stage'].isin(['New Lead', 'Walking Planned', 'Walking Done'])]
            .groupby('Lead Source').size() / lead_source_metrics['Total Leads'] * 100
        ).round(1)
        fig_bar = px.bar(
            lead_source_metrics,
            x='Lead Source',
            y='Conversion Rate (%)',
            color='Conversion Rate (%)',
            title='Lead Source Performance (Conversion Rates)',
            color_continuous_scale=px.colors.sequential.Blues
        )
        st.plotly_chart(fig_bar)

        # Top Performers (Table View)
        st.header("Top Performers")
        top_owners = (
            filtered_df[filtered_df['Lead Stage'].isin(['New Lead', 'Walking Planned', 'Walking Done'])]
            .groupby('Owner').size().reset_index(name='Positive Outcomes')
            .sort_values(by='Positive Outcomes', ascending=False).head(5)
        )
        st.subheader("Top Owners")
        st.table(top_owners)

        top_groups = (
            filtered_df[filtered_df['Lead Stage'].isin(['New Lead', 'Walking Planned', 'Walking Done'])]
            .groupby('Group').size().reset_index(name='Positive Outcomes')
            .sort_values(by='Positive Outcomes', ascending=False).head(3)
        )
        st.subheader("Top Groups")
        st.table(top_groups)

        # Poor Performers (Table View)
        st.header("Areas for Improvement")
        poor_owners = (
            filtered_df.groupby('Owner').size().reset_index(name='Total Leads')
            .sort_values(by='Total Leads', ascending=True).head(5)
        )
        st.subheader("Owners Needing Attention")
        st.table(poor_owners)

if __name__ == "__main__":
    main()
