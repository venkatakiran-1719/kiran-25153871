import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Data Analytics Dashboard", layout="wide")

POSTGRES_URI = "postgresql://postgres:System%40123@localhost:5432/apdv_2026"

@st.cache_data
def load_data(table_name):
    engine = create_engine(POSTGRES_URI)
    df = pd.read_sql(f'SELECT * FROM {table_name}', engine)
    return df

def add_bar_annotations(fig):
    # Add text on top of the bars
    fig.update_traces(texttemplate='%{y:.2s}', textposition='outside')
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25), showlegend=True)
    return fig

st.title(" Analytics Programming and Data Visualisation")
st.markdown("This dashboard presents exploratory data analysis for three distinct datasets related to energy.")

#  colors for dashboard
VIBRANT_COLORS = px.colors.qualitative.Prism

tab1, tab2, tab3 = st.tabs([" Energy Dataset (JSON)", " SEI06 Dataset (CSV)", " Europe Electricity (CSV)"])

# Tab 1
with tab1:
    st.header("Energy Dataset Analysis")
    try:
        df1 = load_data('clean_energy')
        
        # Calculations 
        cons_cols = [col for col in df1.columns if "consumption_" in col]
        df1["total_consumption"] = df1[cons_cols].sum(axis=1)
        
        col1, col2 = st.columns(2)
        
        # Total Energy Consumption Trend Over Years
        with col1:
            yearly_total = df1.groupby("year", as_index=False)["total_consumption"].sum().round(2)
            fig1 = px.line(yearly_total, x="year", y="total_consumption", markers=True, title="Total Energy Consumption Trend Over Years", color_discrete_sequence=['#8E44AD'])
            peak_row = yearly_total.loc[yearly_total["total_consumption"].idxmax()]
            fig1.add_scatter(x=[peak_row["year"]], y=[peak_row["total_consumption"]], mode='markers+text', marker=dict(size=14, color='#E74C3C'), name='Peak Year', text=[f'{peak_row["total_consumption"]:,.0f}'], textposition='top center')
            
            #  annotations
            start_row = yearly_total.iloc[0]
            fig1.add_annotation(x=start_row["year"], y=start_row["total_consumption"], yshift=15, text=f"{start_row['total_consumption']:,.0f}", showarrow=False)
            
            try:
                end_row = yearly_total[yearly_total["year"].astype(str).str.contains("2020")]
                if not end_row.empty:
                    fig1.add_annotation(x=end_row["year"].iloc[0], y=end_row["total_consumption"].iloc[0], yshift=15, text=f"{end_row['total_consumption'].iloc[0]:,.0f}", showarrow=False)
            except Exception:
                pass
            
            last_row = yearly_total.iloc[-1]
            fig1.add_annotation(x=last_row["year"], y=last_row["total_consumption"], yshift=15, text=f"{last_row['total_consumption']:,.0f}", showarrow=False)
                
            fig1.update_layout(xaxis_title="Year", yaxis_title="Total Consumption", showlegend=False, margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig1, use_container_width=True)
            
        #  Petroleum vs Natural Gas Consumption Trend
        with col2:
            petro_cols = [col for col in df1.columns if "petroleum" in col]
            gas_cols = [col for col in df1.columns if "natural_gas" in col]
            df1["petroleum_total"] = df1[petro_cols].sum(axis=1)
            df1["gas_total"] = df1[gas_cols].sum(axis=1)
            
            trend = df1.groupby("year", as_index=False)[["petroleum_total", "gas_total"]].sum()
            fig2 = px.line(trend, x="year", y=["petroleum_total", "gas_total"], markers=True, title="Petroleum vs Natural Gas Consumption Trend", color_discrete_sequence=['#E67E22', '#2980B9'])
            
            petro_peak = trend.loc[trend["petroleum_total"].idxmax()]
            gas_peak = trend.loc[trend["gas_total"].idxmax()]
            
            fig2.add_scatter(x=[petro_peak["year"]], y=[petro_peak["petroleum_total"]], mode='markers+text', marker=dict(size=14, color='#D35400'), name='Peak Petroleum', text=[f'Peak Petro: {petro_peak["petroleum_total"]:,.0f}'], textposition='top center')
            fig2.add_scatter(x=[gas_peak["year"]], y=[gas_peak["gas_total"]], mode='markers+text', marker=dict(size=14, color='#2471A3'), name='Peak Gas', text=[f'Peak Gas: {gas_peak["gas_total"]:,.0f}'], textposition='top center')
            
            fig2.add_annotation(x=trend["year"].iloc[0], y=trend["petroleum_total"].iloc[0], yshift=-15, text=f"{trend['petroleum_total'].iloc[0]:,.0f}", showarrow=False)
            fig2.add_annotation(x=trend["year"].iloc[-1], y=trend["petroleum_total"].iloc[-1], yshift=15, text=f"{trend['petroleum_total'].iloc[-1]:,.0f}", showarrow=False)
            fig2.add_annotation(x=trend["year"].iloc[0], y=trend["gas_total"].iloc[0], yshift=15, text=f"{trend['gas_total'].iloc[0]:,.0f}", showarrow=False)
            fig2.add_annotation(x=trend["year"].iloc[-1], y=trend["gas_total"].iloc[-1], yshift=-15, text=f"{trend['gas_total'].iloc[-1]:,.0f}", showarrow=False)
            
            fig2.update_layout(xaxis_title="Year", yaxis_title="Consumption", legend_title="Type", margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig2, use_container_width=True)
            
        col3, col4 = st.columns(2)
        
        #  Average Energy Consumption by Sector 
        with col3:
            commercial_cols = [col for col in df1.columns if "commercial" in col.lower()]
            industrial_cols = [col for col in df1.columns if "industrial" in col.lower()]
            residential_cols = [col for col in df1.columns if "residential" in col.lower()]
            transport_cols = [col for col in df1.columns if "transportation" in col.lower()]
            
            df1["Commercial"] = df1[commercial_cols].sum(axis=1) if commercial_cols else 0
            df1["Industrial"] = df1[industrial_cols].sum(axis=1) if industrial_cols else 0
            df1["Residential"] = df1[residential_cols].sum(axis=1) if residential_cols else 0
            df1["Transport"] = df1[transport_cols].sum(axis=1) if transport_cols else 0
            
            sector_mean = df1[["Commercial", "Industrial", "Residential", "Transport"]].mean().round(2).reset_index()
            sector_mean.columns = ["sector", "avg_consumption"]
            sector_mean = sector_mean.sort_values("avg_consumption")
            
            fig3 = px.bar(sector_mean, x="avg_consumption", y="sector", orientation='h', title="Average Energy Consumption by Sector", color="avg_consumption", color_continuous_scale=px.colors.sequential.Sunset)
            fig3.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
            fig3.update_layout(xaxis_title="Average Consumption", yaxis_title="Sector", showlegend=False, margin=dict(t=50, l=25, r=90, b=25))
            fig3.update_xaxes(range=[0, sector_mean["avg_consumption"].max() * 1.3])
            st.plotly_chart(fig3, use_container_width=True)
            
        # Pie chart: Petroleum Share
        with col4:
            petrol_top = df1.groupby('state')['consumption_commercial_petroleum'].sum().reset_index().nlargest(5, 'consumption_commercial_petroleum')
            fig4 = px.pie(petrol_top, names='state', values='consumption_commercial_petroleum', title="Top 5 States Commercial Petroleum Consumption", hole=0.4, color_discrete_sequence=VIBRANT_COLORS)
            fig4.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig4, use_container_width=True)
            
        col5, col6 = st.columns(2)
        
        # Top 10 States by Total Energy Consumption 
        with col5:
            state_total = df1.groupby("state", as_index=False)["total_consumption"].sum().sort_values("total_consumption", ascending=False).head(10).sort_values("total_consumption", ascending=True)
            
            fig5 = px.bar(state_total, x="total_consumption", y="state", orientation='h', title="Top 10 States by Total Energy Consumption", color="total_consumption", color_continuous_scale=px.colors.sequential.Viridis)
            fig5.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
            fig5.update_layout(xaxis_title="Total Consumption", yaxis_title="State", showlegend=False, margin=dict(t=50, l=25, r=80, b=25))
            fig5.update_xaxes(range=[0, state_total["total_consumption"].max() * 1.3])
            st.plotly_chart(fig5, use_container_width=True)
            
        with col6:
             st.write("") 

    except Exception as e:
        st.error(f"Waiting for clean_energy table to be generated in PostgreSQL: {e}")

# Tab 2 
with tab2:
    st.header("SEI06 Dataset Analysis")
    try:
        df2 = load_data('clean_sei06')
        
        col1, col2 = st.columns(2)
        
        #  Top 10 Fuel Types by Value
        with col1:
            filtered_df2 = df2[~df2['fuel_type'].str.contains('sum of all fuel products', case=False, na=False)]
            fuel_dist = filtered_df2.groupby('fuel_type')['value'].sum().reset_index().nlargest(10, 'value')
            fig1 = px.bar(fuel_dist, x='fuel_type', y='value', color='fuel_type', title="Top 10 Fuel Types by Value", color_discrete_sequence=VIBRANT_COLORS)
            st.plotly_chart(add_bar_annotations(fig1), use_container_width=True)
            
        # Yearly Total Fuel Consumption Trend
        with col2:
            yearly_total = df2.groupby("year", as_index=False)["value"].sum().round(2).sort_values("year")
            fig2 = px.line(yearly_total, x="year", y="value", markers=True, title="Yearly Total Fuel Consumption Trend", color_discrete_sequence=['#8E44AD'])
            max_row = yearly_total.loc[yearly_total["value"].idxmax()]
            min_row = yearly_total.loc[yearly_total["value"].idxmin()]
            
            fig2.add_scatter(x=[max_row["year"]], y=[max_row["value"]], mode='markers+text', marker=dict(size=14, color='#E74C3C'), name='Peak Year', text=[f'{max_row["value"]:,.0f}'], textposition='top center')
            fig2.add_scatter(x=[min_row["year"]], y=[min_row["value"]], mode='markers+text', marker=dict(size=14, color='#3498DB'), name='Lowest Year', text=[f'{min_row["value"]:,.0f}'], textposition='bottom center')
            
            # Annote 
            last_row = yearly_total.iloc[-1]
            fig2.add_annotation(x=last_row["year"], y=last_row["value"], yshift=15, text=f"{last_row['value']:,.0f}", showarrow=False)
            
            fig2.update_layout(xaxis_title="Year", yaxis_title="Fuel Consumption", margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig2, use_container_width=True)
            
        col3, col4 = st.columns(2)
        
        #  Top 3 Sectors: Yearly Average Fuel Consumption Trend (NEW)
        with col3:
            top3_sectors = df2.groupby("sector")["value"].sum().sort_values(ascending=False).head(3).index
            sector_trend = df2[df2["sector"].isin(top3_sectors)].groupby(["year", "sector"], as_index=False)["value"].mean().round(2).sort_values("year")
            
            fig3 = px.line(sector_trend, x="year", y="value", color="sector", markers=True, title="Top 3 Sectors: Avg Fuel Consumption Trend", color_discrete_sequence=VIBRANT_COLORS)
            
            for sector in top3_sectors:
                temp = sector_trend[sector_trend["sector"] == sector]
                if not temp.empty:
                    peak_row = temp.loc[temp["value"].idxmax()]
                    fig3.add_scatter(x=[peak_row["year"]], y=[peak_row["value"]], mode='text', text=[f'{peak_row["value"]:,.0f}'], textposition='top center', showlegend=False)
                    
                    start_row = temp.iloc[0]
                    end_row = temp.iloc[-1]
                    fig3.add_annotation(x=start_row["year"], y=start_row["value"], yshift=-15, text=f"{start_row['value']:,.0f}", showarrow=False)
                    fig3.add_annotation(x=end_row["year"], y=end_row["value"], yshift=15, text=f"{end_row['value']:,.0f}", showarrow=False)
            
            fig3.update_layout(xaxis_title="Year", yaxis_title="Average Fuel Consumption", legend_title="Sector", margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig3, use_container_width=True)
            
        #  Pie chart: Distribution of Top 5 Fuel Types 
        with col4:
            fig4 = px.pie(fuel_dist.head(5), names='fuel_type', values='value', title="Distribution of Top 5 Fuel Types", color_discrete_sequence=VIBRANT_COLORS)
            fig4.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig4, use_container_width=True)
            
        col5, col6 = st.columns(2)
        
        # Renewable Energy Insights Table
        with col5:
            renew_df = df2[df2["fuel_type"].str.fullmatch("Sum of all renewable energies", case=False, na=False)]
            if not renew_df.empty:
                renew_trend = renew_df.groupby("year", as_index=False)["value"].sum().round(0).sort_values("year").reset_index(drop=True)
                renew_trend["change"] = renew_trend["value"].diff()

                milestone_rows = [
                    ("Latest Year", renew_trend.iloc[-1]),
                    ("Peak Year", renew_trend.loc[renew_trend["value"].idxmax()]),
                    ("Lowest Year", renew_trend.loc[renew_trend["value"].idxmin()]),
                    ("Strongest Increase", renew_trend.loc[renew_trend["change"].idxmax()]),
                    ("Largest Decline", renew_trend.loc[renew_trend["change"].idxmin()])
                ]

                milestone_map = {}
                for label, row in milestone_rows:
                    year = int(row["year"])
                    if year not in milestone_map:
                        milestone_map[year] = {"value": int(round(row["value"])), "positions": []}
                    milestone_map[year]["positions"].append(label)

                insights_table = pd.DataFrame(
                    [
                        {
                            "Year": year,
                            "Average Value (ktoe)": details["value"],
                            "Position": ", ".join(details["positions"])
                        }
                        for year, details in sorted(milestone_map.items())
                    ]
                )

                st.subheader("Renewable Energy Key Years")
                st.dataframe(insights_table, hide_index=True, use_container_width=True)
            else:
                st.write("Renewable energy data not found.")
                
        # Top 10 Sectors by Average Fuel Consumption (NEW)
        with col6:
            sector_avg = df2.groupby("sector", as_index=False)["value"].mean().round(2).sort_values("value", ascending=False).head(10).sort_values("value", ascending=True)
            fig6 = px.bar(sector_avg, x="value", y="sector", orientation='h', title="Top 10 Sectors by Average Fuel Consumption", color="sector", color_discrete_sequence=VIBRANT_COLORS)
            fig6.update_traces(texttemplate='%{x:,.1f}', textposition='outside')
            fig6.update_layout(xaxis_title="Average Fuel Consumption", yaxis_title="Sector", showlegend=False, margin=dict(t=50, l=25, r=80, b=25))
            fig6.update_xaxes(range=[0, sector_avg["value"].max() * 1.3])
            st.plotly_chart(fig6, use_container_width=True)

    except Exception as e:
        st.error(f"Waiting for clean_sei06 table to be generated in PostgreSQL: {e}")

# Tab 3 
with tab3:
    st.header("Global Electricity Load Analysis")
    try:
        df3 = load_data('clean_gloelec')
        df3_samp = df3.sample(n=min(10000, len(df3)), random_state=42) if len(df3) > 10000 else df3

        col1, col2 = st.columns(2)
        
        #  Average Electricity Load by Year
        with col1:
            yearly_avg = df3.groupby("year", as_index=False)["load"].mean().round(2).sort_values("year")
            yearly_avg["year_str"] = yearly_avg["year"].astype(str)
            fig1 = px.bar(yearly_avg, x="year_str", y="load", title="Average Electricity Load by Year", color="year_str", color_discrete_sequence=VIBRANT_COLORS)
            fig1.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
            fig1.update_layout(xaxis_title="Year", yaxis_title="Average Load", showlegend=False, margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig1, use_container_width=True)
            
        #  Average Monthly Electricity Load Pattern
        with col2:
            monthly_avg = df3.groupby("month", as_index=False)["load"].mean().round(2).sort_values("month")
            month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
            monthly_avg["month_name"] = monthly_avg["month"].map(month_names)
            
            fig2 = px.line(monthly_avg, x="month_name", y="load", markers=True, text="load", title="Average Monthly Electricity Load Pattern", color_discrete_sequence=['#F39C12'])
            fig2.update_traces(texttemplate='%{text:,.0f}', textposition='top center')
            
            max_idx = monthly_avg["load"].idxmax()
            min_idx = monthly_avg["load"].idxmin()
            
            fig2.add_scatter(x=[monthly_avg.loc[max_idx, "month_name"]], y=[monthly_avg.loc[max_idx, "load"]], mode='markers', marker=dict(size=14, color='#E74C3C'), name='Highest')
            fig2.add_scatter(x=[monthly_avg.loc[min_idx, "month_name"]], y=[monthly_avg.loc[min_idx, "load"]], mode='markers', marker=dict(size=14, color='#3498DB'), name='Lowest')
            
            fig2.update_layout(xaxis_title="Month", yaxis_title="Average Load", margin=dict(t=50, l=25, r=25, b=25))
            fig2.update_yaxes(range=[monthly_avg["load"].min() * 0.95, monthly_avg["load"].max() * 1.1])
            st.plotly_chart(fig2, use_container_width=True)
            
        col3, col4 = st.columns(2)
        
        # Hourly Electricity Load Profile: Weekday vs Weekend
        with col3:
            hourly_pattern = df3.groupby(["hour", "isweekend"], as_index=False)["load"].mean().round(2)
            hourly_pattern['Day Type'] = hourly_pattern['isweekend'].map({0: 'Weekday', 1: 'Weekend'})
            
            fig3 = px.line(hourly_pattern, x="hour", y="load", color="Day Type", markers=True, title="Hourly Electricity Load: Weekday vs Weekend", color_discrete_sequence=['#3498DB', '#E74C3C'])
            
            weekday = hourly_pattern[hourly_pattern["isweekend"] == 0]
            weekend = hourly_pattern[hourly_pattern["isweekend"] == 1]
            weekday_peak = weekday.loc[weekday["load"].idxmax()]
            weekend_peak = weekend.loc[weekend["load"].idxmax()]
            
            fig3.add_scatter(x=[weekday_peak["hour"]], y=[weekday_peak["load"]], mode='text', text=[f'Peak: {weekday_peak["load"]:,.0f}'], textposition='top center', showlegend=False)
            fig3.add_scatter(x=[weekend_peak["hour"]], y=[weekend_peak["load"]], mode='text', text=[f'Peak: {weekend_peak["load"]:,.0f}'], textposition='top center', showlegend=False)
            
            weekday_start = weekday.iloc[0]
            weekday_end = weekday.iloc[-1]
            weekend_start = weekend.iloc[0]
            weekend_end = weekend.iloc[-1]
            
            fig3.add_annotation(x=weekday_start["hour"], y=weekday_start["load"], yshift=-15, text=f"{weekday_start['load']:,.0f}", showarrow=False)
            fig3.add_annotation(x=weekday_end["hour"], y=weekday_end["load"], yshift=15, text=f"{weekday_end['load']:,.0f}", showarrow=False)
            fig3.add_annotation(x=weekend_start["hour"], y=weekend_start["load"], yshift=15, text=f"{weekend_start['load']:,.0f}", showarrow=False)
            fig3.add_annotation(x=weekend_end["hour"], y=weekend_end["load"], yshift=-15, text=f"{weekend_end['load']:,.0f}", showarrow=False)
            
            fig3.update_layout(xaxis_title="Hour of Day", yaxis_title="Average Load", xaxis=dict(tickmode='linear', tick0=0, dtick=2), margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig3, use_container_width=True)
            
        #  Average Electricity Load by Country
        with col4:
            country_avg = df3.groupby("country", as_index=False)["load"].mean().round(2).sort_values("load", ascending=True)
            
            fig4 = px.bar(country_avg, x="load", y="country", orientation='h', title="Average Electricity Load by Country", color="country", color_discrete_sequence=VIBRANT_COLORS)
            fig4.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
            fig4.update_layout(xaxis_title="Average Load", yaxis_title="Country", showlegend=False, margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig4, use_container_width=True)
            
        #  Ireland Monthly Electricity Load Pattern 
        st.markdown("### Country Detail Analysis: Ireland")
        ireland_df = df3[df3["country"].str.lower() == "ireland"]
        if not ireland_df.empty:
            monthly_avg_ire = ireland_df.groupby("month", as_index=False)["load"].mean().round(2).sort_values("month")
            monthly_avg_ire["month_name"] = monthly_avg_ire["month"].map(month_names)
            
            fig5 = px.line(monthly_avg_ire, x="month_name", y="load", markers=True, text="load", title="Ireland Monthly Electricity Load Pattern", color_discrete_sequence=['#2ECC71'])
            fig5.update_traces(texttemplate='%{text:,.0f}', textposition='top center')
            
            max_row = monthly_avg_ire.loc[monthly_avg_ire["load"].idxmax()]
            min_row = monthly_avg_ire.loc[monthly_avg_ire["load"].idxmin()]
            
            fig5.add_scatter(x=[max_row["month_name"]], y=[max_row["load"]], mode='markers', marker=dict(size=14, color='#E74C3C'), name='Peak Month')
            fig5.add_scatter(x=[min_row["month_name"]], y=[min_row["load"]], mode='markers', marker=dict(size=14, color='#3498DB'), name='Lowest Month')
            
            fig5.update_layout(xaxis_title="Month", yaxis_title="Average Load", margin=dict(t=50, l=25, r=25, b=25))
            fig5.update_yaxes(range=[monthly_avg_ire["load"].min() * 0.95, monthly_avg_ire["load"].max() * 1.1])
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.write("Ireland data not found in the dataset.")

    except Exception as e:
        st.error(f"Waiting for clean_gloelec table to be generated in PostgreSQL: {e}")
