import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import date

# Set a darker style for matplotlib plots and adjust for dark background
plt.style.use('seaborn-v0_8-darkgrid') # Using a style that works well with darker backgrounds

# Customize matplotlib parameters for dark theme
plt.rcParams.update({
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "axes.edgecolor": "white",
    "figure.facecolor": "#262730", # Streamlit dark background color
    "axes.facecolor": "#262730",   # Match axes background to Streamlit dark background
    "savefig.facecolor": "#262730", # Savefig background color
})


# Function to plot monthly cashflow (Income vs Expense vs Savings)
def plot_monthly_cashflow(df):
    monthly = (df.groupby(['AnoMes','Tipo'])['Valor']
                 .sum()
                 .unstack(fill_value=0))

    fig, ax = plt.subplots(figsize=(10, 5)) # Standardized figure size
    # Ensure all three columns exist before plotting, provide default 0 if not
    plot_data = monthly[['Income', 'Expense', 'Savings']].fillna(0) if all(col in monthly.columns for col in ['Income', 'Expense', 'Savings']) else monthly[['Income', 'Expense']].fillna(0)


    plot_data.plot(kind='bar', stacked=False, ax=ax, color=['#4CAF50', '#FF7043', '#2196F3']) # Added colors for Savings
    plt.title('Fluxo de Caixa Mensal: Entradas vs. Saídas vs. Economias', fontsize=14, color='white') # Adjusted title color
    plt.ylabel('Valor (R$)', fontsize=10, color='white') # Adjusted font size and color
    plt.xlabel('Mês', fontsize=10, color='white') # Adjusted font size and color
    plt.xticks(rotation=45, ha='right', fontsize=8) # Adjusted font size
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('R$%.2f'))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Tipo', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8, facecolor='#262730', edgecolor='white') # Adjusted legend colors
    plt.tight_layout()
    return fig

# Function to plot cumulative balance
def plot_cumulative_balance(df):
    # Ensure the dataframe has 'Data' and 'Valor_signed' columns before plotting
    if 'Data' not in df.columns or 'Valor_signed' not in df.columns:
        st.warning("Dados insuficientes para plotar o saldo acumulado.")
        return None

    saldo = df.groupby('Data')['Valor_signed'].sum().cumsum()

    # Handle cases where saldo might be empty after filtering
    if saldo.empty:
        st.warning("Nenhum dado de saldo disponível para o período selecionado.")
        return None

    fig, ax = plt.subplots(figsize=(10, 5)) # Standardized figure size
    saldo.plot(ax=ax, color='#2196F3') # Added color
    plt.title('Saldo Líquido Acumulado ao Longo do Tempo', fontsize=14, color='white') # Adjusted title color
    plt.ylabel('Saldo (R$)', fontsize=10, color='white') # Adjusted font size and color
    plt.xlabel('Data', fontsize=10, color='white') # Adjusted font size and color
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('R$%.2f'))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    return fig

# Function to plot expense distribution by category (Pie Chart)
def plot_expense_distribution_pie(df):
    # Ensure the dataframe has 'Tipo', 'Categoria', and 'Valor' columns and contains expenses
    if 'Tipo' not in df.columns or 'Categoria' not in df.columns or 'Valor' not in df.columns or df[df['Tipo'] == 'Expense'].empty:
        st.warning("Dados de despesas insuficientes para plotar a distribuição por categoria.")
        return None

    # Filter for expenses and group by category
    gastos_por_categoria = df[df['Tipo']=='Expense'].groupby('Categoria')['Valor'].sum()

    # Handle cases where gastos_por_categoria might be empty after filtering
    if gastos_por_categoria.empty:
        st.warning("Nenhum dado de despesas por categoria disponível para os filtros selecionados.")
        return None

    # Sort values for better visualization
    gastos_por_categoria = gastos_por_categoria.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(6, 6)) # Reduced figure size for pie chart
    # Plot pie chart
    wedges, texts, autotexts = ax.pie(gastos_por_categoria,
                                      labels=gastos_por_categoria.index,
                                      autopct='%1.1f%%', # Show percentages
                                      startangle=140,
                                      colors=plt.cm.viridis(gastos_por_categoria / gastos_por_categoria.max())) # Use a color map


    plt.title('Distribuição de Despesas por Categoria (Percentual)', fontsize=14, color='white') # Adjusted font size and color
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    return fig

# Function to plot expense distribution by category (Bar Chart - total values)
def plot_expense_distribution_bar(df):
    # Ensure the dataframe has 'Tipo', 'Categoria', and 'Valor' columns and contains expenses
    if 'Tipo' not in df.columns or 'Categoria' not in df.columns or 'Valor' not in df.columns or df[df['Tipo'] == 'Expense'].empty:
        st.warning("Dados de despesas insuficientes para plotar a distribuição por categoria.")
        return None

    gastos = (df[df['Tipo']=='Expense']
              .groupby('Categoria')['Valor']
              .sum()
              .sort_values(ascending=False))

    # Handle cases where gastos might be empty after filtering
    if gastos.empty:
        st.warning("Nenhum dado de despesas por categoria disponível para os filtros selecionados.")
        return None


    fig, ax = plt.subplots(figsize=(10, 6)) # Standardized figure size
    gastos.plot(kind='barh', ax=ax, color='#FFB74D') # Changed color
    plt.title('Distribuição de Despesas por Categoria (Valores)', fontsize=14, color='white') # Adjusted font size and color
    plt.xlabel('Valor (R$)', fontsize=10, color='white') # Adjusted font size and color
    plt.ylabel('Categoria', fontsize=10, color='white') # Adjusted font size and color
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('R$%.2f'))
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    return fig


# Function to plot monthly expense evolution by category (Bar Chart)
def plot_monthly_category_expenses(df):
    # Ensure the dataframe has 'Tipo', 'AnoMes', 'Categoria', and 'Valor' columns and contains expenses
    if 'Tipo' not in df.columns or 'AnoMes' not in df.columns or 'Categoria' not in df.columns or 'Valor' not in df.columns or df[df['Tipo'] == 'Expense'].empty:
        st.warning("Dados de despesas insuficientes para plotar a evolução mensal por categoria.")
        return None

    monthly_category_expenses = (df[df['Tipo']=='Expense']
                                 .groupby(['AnoMes', 'Categoria'])['Valor']
                                 .sum()
                                 .unstack(fill_value=0))

    # Handle cases where monthly_category_expenses might be empty after filtering
    if monthly_category_expenses.empty:
         st.warning("Nenhum dado de despesas mensais por categoria disponível para os filtros selecionados.")
         return None


    fig, ax = plt.subplots(figsize=(12, 6)) # Standardized figure size
    monthly_category_expenses.plot(kind='bar', stacked=True, ax=ax, cmap='tab20') # Changed color map
    plt.title('Evolução Mensal das Despesas por Categoria', fontsize=14, color='white') # Adjusted font size and color
    plt.ylabel('Valor (R$)', fontsize=10, color='white') # Adjusted font size and color
    plt.xlabel('Mês', fontsize=10, color='white') # Adjusted font size and color
    plt.xticks(rotation=45, ha='right', fontsize=8) # Adjusted font size
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('R$%.2f'))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Categoria', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8, facecolor='#262730', edgecolor='white') # Adjusted legend colors
    plt.tight_layout()
    return fig

# Function to plot monthly income evolution
def plot_monthly_income(df):
    # Ensure the dataframe has 'Tipo', 'AnoMes', and 'Valor' columns and contains income
    if 'Tipo' not in df.columns or 'AnoMes' not in df.columns or 'Valor' not in df.columns or df[df['Tipo'] == 'Income'].empty:
        st.warning("Dados de receita insuficientes para plotar a evolução mensal.")
        return None

    monthly_income = (df[df['Tipo']=='Income']
                      .groupby('AnoMes')['Valor']
                      .sum())

    # Handle cases where monthly_income might be empty after filtering
    if monthly_income.empty:
        st.warning("Nenhum dado de receita mensal disponível para o período selecionado.")
        return None


    fig, ax = plt.subplots(figsize=(10, 5)) # Standardized figure size
    monthly_income.plot(ax=ax, color='#4CAF50') # Changed color
    plt.title('Evolução Mensal da Receita', fontsize=14, color='white') # Adjusted font size and color
    plt.ylabel('Valor (R$)', fontsize=10, color='white') # Adjusted font size and color
    plt.xlabel('Mês', fontsize=10, color='white') # Adjusted font size and color
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('R$%.2f'))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    return fig

# Function to plot cumulative savings
def plot_cumulative_savings(df):
    # Ensure the dataframe has 'Tipo', 'Data', and 'Valor' columns and contains savings
    if 'Tipo' not in df.columns or 'Data' not in df.columns or 'Valor' not in df.columns or df[df['Tipo'] == 'Savings'].empty:
        st.warning("Dados de economias insuficientes para plotar as economias acumuladas.")
        return None

    savings_df = df[df['Tipo'] == 'Savings'].copy()

    # Ensure 'Data' is sorted for correct cumulative sum
    savings_df = savings_df.sort_values('Data')

    cumulative_savings = savings_df.groupby('Data')['Valor'].sum().cumsum()

    # Handle cases where cumulative_savings might be empty after filtering
    if cumulative_savings.empty:
        st.warning("Nenhum dado de economias acumuladas disponível para o período selecionado.")
        return None

    fig, ax = plt.subplots(figsize=(10, 5)) # Standardized figure size
    cumulative_savings.plot(ax=ax, color='#2196F3') # Using a distinct color for savings
    plt.title('Economias Acumuladas ao Longo do Tempo', fontsize=14, color='white') # Adjusted title color
    plt.ylabel('Economias (R$)', fontsize=10, color='white') # Adjusted font size and color
    plt.xlabel('Data', fontsize=10, color='white') # Adjusted font size and color
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('R$%.2f'))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    return fig


def main():
    st.set_page_config(layout="wide") # Set wide layout
    st.title('Dashboard de Análise Financeira')
    st.markdown("Este dashboard apresenta uma análise do fluxo de caixa, despesas e receitas ao longo do tempo.")

    # Load data
    df = st.cache_data(pd.read_excel)('fluxo_caixa.xlsx', parse_dates=['Data'])

    # Preprocessing
    df['AnoMes'] = df['Data'].dt.to_period('M')
    # Adjusted Valor_signed to treat Expense and Savings as negative
    df['Valor_signed'] = df.apply(lambda x: x['Valor'] * (1 if x['Tipo'] == 'Income' else -1), axis=1)

    # Create AnoMes_dt here so it's available for all filter types
    df['AnoMes_dt'] = df['Data'].dt.to_period('M').dt.to_timestamp()


    # Sidebar filters
    st.sidebar.header('Filtros')
    st.sidebar.markdown("Utilize os filtros abaixo para selecionar o período de interesse.")

    filter_type = st.sidebar.radio("Selecionar Tipo de Filtro de Data:",
                                   ('Período', 'Mês Específico', 'Comparar 2 Meses'))

    date_filtered_df = df.copy()
    selected_months = []

    if filter_type == 'Período':
        min_date = df['Data'].min().date()
        max_date = df['Data'].max().date()

        start_date = st.sidebar.date_input('Data de Início', min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.sidebar.date_input('Data de Fim', min_value=min_date, max_value=max_date, value=max_date)

        if start_date and end_date:
            date_filtered_df = date_filtered_df[(date_filtered_df['Data'].dt.date >= start_date) & (date_filtered_df['Data'].dt.date <= end_date)]

    elif filter_type == 'Mês Específico':
        unique_months = sorted(df['AnoMes_dt'].unique())
        selected_month = st.sidebar.selectbox('Selecionar Mês', unique_months, format_func=lambda x: x.strftime('%Y-%m'))

        if selected_month:
            date_filtered_df = date_filtered_df[date_filtered_df['AnoMes_dt'] == selected_month]
            selected_months = [pd.Period(selected_month, 'M')]

    elif filter_type == 'Comparar 2 Meses':
        unique_months = sorted(df['AnoMes_dt'].unique())
        month1 = st.sidebar.selectbox('Selecionar Primeiro Mês', unique_months, index=len(unique_months)-1 if len(unique_months) > 0 else 0, format_func=lambda x: x.strftime('%Y-%m'))
        month2 = st.sidebar.selectbox('Selecionar Segundo Mês', unique_months, index=len(unique_months)-2 if len(unique_months) > 1 else 0, format_func=lambda x: x.strftime('%Y-%m'))

        if month1 and month2:
            date_filtered_df = date_filtered_df[date_filtered_df['AnoMes_dt'].isin([month1, month2])]
            selected_months = [pd.Period(month1, 'M'), pd.Period(month2, 'M')]

    # Category filter removed as requested
    # all_categories = ['All'] + sorted(df['Categoria'].unique().tolist())
    # selected_categories = st.sidebar.multiselect('Selecionar Categoria', all_categories, default='All')


    # Create dataframes filtered ONLY by date (category filter removed)
    cashflow_filtered_df = date_filtered_df.copy()
    cumulative_balance_filtered_df = date_filtered_df.copy()
    expense_distribution_filtered_df = date_filtered_df[date_filtered_df['Tipo'] == 'Expense'].copy() # Filter only expenses
    monthly_category_expense_filtered_df = date_filtered_df[date_filtered_df['Tipo'] == 'Expense'].copy() # Filter only expenses
    income_filtered_df = date_filtered_df[date_filtered_df['Tipo'] == 'Income'].copy() # Filter only Income
    cumulative_savings_filtered_df = date_filtered_df[date_filtered_df['Tipo'] == 'Savings'].copy() # Filter only Savings


    # Calculate monthly summaries and changes within the main function
    # Expenses should NOT include Savings
    monthly_total_expenses = (cashflow_filtered_df[cashflow_filtered_df['Tipo'] == 'Expense']
                              .groupby('AnoMes')['Valor']
                              .sum())

    monthly_total_income = (cashflow_filtered_df[cashflow_filtered_df['Tipo'] == 'Income']
                            .groupby('AnoMes')['Valor']
                            .sum())

    # Calculate total savings monthly
    monthly_total_savings = (cashflow_filtered_df[cashflow_filtered_df['Tipo'] == 'Savings']
                             .groupby('AnoMes')['Valor']
                             .sum())

    # Calculate monthly net balance including savings
    monthly_net_balance = monthly_total_income.sub(monthly_total_expenses, fill_value=0).sub(monthly_total_savings, fill_value=0)


    # Display summaries using st.metric
    st.header('Resumo Mensal')

    if filter_type == 'Mês Específico' and selected_months:
        current_month = selected_months[0]
        last_month_expenses = monthly_total_expenses.get(current_month, 0)
        last_month_income = monthly_total_income.get(current_month, 0)
        last_month_balance = monthly_net_balance.get(current_month, 0)
        last_month_savings = monthly_total_savings.get(current_month, 0)

        st.write(f"Resumo para o mês de **{current_month.strftime('%Y-%m')}**:")
        col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4) # Added a column for savings

        with col_metrics1:
             st.metric(label="Total Receita", value=f"R${last_month_income:,.2f}")

        with col_metrics2:
            st.metric(label="Total Despesas", value=f"R${last_month_expenses:,.2f}")

        with col_metrics3:
            st.metric(label="Total Economias", value=f"R${last_month_savings:,.2f}") # Display total savings

        with col_metrics4:
            st.metric(label="Saldo Líquido", value=f"R${last_month_balance:,.2f}")


        # Display expense summary by category for the selected month (text list)
        st.subheader(f'Resumo de Despesas por Categoria ({current_month.strftime("%Y-%m")})')
        # Use expense_distribution_filtered_df for category breakdown
        if not expense_distribution_filtered_df.empty: # Use the filtered df for distribution (bar/pie)
             last_month_expenses_by_category = (expense_distribution_filtered_df[
                expense_distribution_filtered_df['AnoMes'] == current_month]
                .groupby('Categoria')['Valor']
                .sum()
                .sort_values(ascending=False)
            )
             if not last_month_expenses_by_category.empty:
                for category, value in last_month_expenses_by_category.items():
                    st.write(f"- {category}: R${value:,.2f}")
             else:
                st.write("Nenhuma despesa por categoria para o mês selecionado.")
        else:
            st.write("Nenhum dado de despesas disponível para o período ou filtros selecionados.")


    elif filter_type == 'Comparar 2 Meses' and len(selected_months) == 2:
        month1_period = selected_months[0]
        month2_period = selected_months[1]

        month1_expenses = monthly_total_expenses.get(month1_period, 0)
        month2_expenses = monthly_total_expenses.get(month2_period, 0)
        expense_change = month2_expenses - month1_expenses

        month1_income = monthly_total_income.get(month1_period, 0)
        month2_income = monthly_total_income.get(month2_period, 0)
        income_change = month2_income - month1_income

        month1_balance = monthly_net_balance.get(month1_period, 0)
        month2_balance = monthly_net_balance.get(month2_period, 0)
        balance_change = month2_balance - month1_balance

        month1_savings = monthly_total_savings.get(month1_period, 0)
        month2_savings = monthly_total_savings.get(month2_period, 0)
        savings_change = month2_savings - month1_savings


        st.write(f"Comparativo entre **{month1_period.strftime('%Y-%m')}** e **{month2_period.strftime('%Y-%m')}**:")
        col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4) # Added a column for savings change

        with col_metrics1:
             st.metric(label=f"Total Receita ({month2_period.strftime('%Y-%m')})", value=f"R${month2_income:,.2f}", delta=f"R${income_change:,.2f}")

        with col_metrics2:
            st.metric(label=f"Total Despesas ({month2_period.strftime('%Y-%m')})", value=f"R${month2_expenses:,.2f}", delta=f"R${expense_change:,.2f}")

        with col_metrics3:
            st.metric(label=f"Total Economias ({month2_period.strftime('%Y-%m')})", value=f"R${month2_savings:,.2f}", delta=f"R${savings_change:,.2f}") # Display savings change

        with col_metrics4:
            st.metric(label=f"Saldo Líquido ({month2_period.strftime('%Y-%m')})", value=f"R${month2_balance:,.2f}", delta=f"R${balance_change:,.2f}")


    else: # Default to Period filter summary
        # Calculate changes based on the last two months in the filtered data
        last_month_expenses = monthly_total_expenses.iloc[-1] if not monthly_total_expenses.empty else 0
        prev_month_expenses = monthly_total_expenses.iloc[-2] if len(monthly_total_expenses) >= 2 else 0
        expense_change = last_month_expenses - prev_month_expenses

        last_month_income = monthly_total_income.iloc[-1] if not monthly_total_income.empty else 0
        prev_month_income = monthly_total_income.iloc[-2] if len(monthly_total_income) >= 2 else 0
        income_change = last_month_income - prev_month_income

        last_month_balance = monthly_net_balance.iloc[-1] if not monthly_net_balance.empty else 0
        prev_month_balance = monthly_net_balance.iloc[-2] if len(monthly_net_balance) >= 2 else 0
        balance_change = last_month_balance - prev_month_balance

        last_month_savings = monthly_total_savings.iloc[-1] if not monthly_total_savings.empty else 0
        prev_month_savings = monthly_total_savings.iloc[-2] if len(monthly_total_savings) >= 2 else 0
        savings_change = last_month_savings - prev_month_savings


        st.markdown("Resumo para o **período selecionado** (último mês exibido vs mês anterior):")
        col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4) # Added a column for savings change

        with col_metrics1:
            st.metric(label="Total Receita Último Mês", value=f"R${last_month_income:,.2f}", delta=f"R${income_change:,.2f}")

        with col_metrics2:
            st.metric(label="Total Despesas Último Mês", value=f"R${last_month_expenses:,.2f}", delta=f"R${expense_change:,.2f}")

        with col_metrics3:
            st.metric(label="Total Economias Último Mês", value=f"R${last_month_savings:,.2f}", delta=f"R${savings_change:,.2f}") # Display savings change

        with col_metrics4:
            st.metric(label="Saldo Líquido Último Mês", value=f"R${last_month_balance:,.2f}", delta=f"R${balance_change:,.2f}")


        # Display expense summary by category for the last month in the filtered data (text list)
        st.subheader('Resumo de Despesas por Categoria (Último Mês do Período)')
        # Use expense_distribution_filtered_df for category breakdown
        if not expense_distribution_filtered_df.empty: # Use the filtered df for distribution (bar/pie)
            # Get the last month from the filtered data for expense distribution
            last_month_anomes = expense_distribution_filtered_df['AnoMes'].max() if not expense_distribution_filtered_df['AnoMes'].empty else None

            if last_month_anomes:
                last_month_expenses_by_category = (expense_distribution_filtered_df[
                    expense_distribution_filtered_df['AnoMes'] == last_month_anomes]
                    .groupby('Categoria')['Valor']
                    .sum()
                    .sort_values(ascending=False)
                )
                if not last_month_expenses_by_category.empty:
                    for category, value in last_month_expenses_by_category.items():
                        st.write(f"- {category}: R${value:,.2f}")
                else:
                    st.write("Nenhuma despesa por categoria para o último mês no período selecionado.")
            else:
                 st.write("Nenhum dado de despesas total mensal disponível para o período selecionado.")
        else:
            st.write("Nenhum dado de despesas disponível para o período ou filtros selecionados.")


    # --- Dashboard Sections ---

    st.header('Visão Geral Mensal')
    st.markdown("Comparativo mensal entre entradas, saídas e economias, e a evolução da receita.")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Fluxo de Caixa Mensal')
        fig1 = plot_monthly_cashflow(cashflow_filtered_df)
        if fig1:
            st.pyplot(fig1)
            plt.close(fig1)

    with col2:
        st.subheader('Evolução Mensal da Receita')
        fig5 = plot_monthly_income(income_filtered_df)
        if fig5:
            st.pyplot(fig5)
            plt.close(fig5)

    st.header('Análise de Despesas por Categoria') # Adjusted title
    st.markdown("Distribuição das despesas por categoria em valores e percentual para o período selecionado.") # Adjusted markdown
    col3, col4 = st.columns(2)

    with col3:
        st.subheader('Despesas por Categoria (Valores)') # Title for bar chart
        fig_bar_dist = plot_expense_distribution_bar(expense_distribution_filtered_df)
        if fig_bar_dist:
            st.pyplot(fig_bar_dist)
            plt.close(fig_bar_dist)

    with col4:
        st.subheader('Despesas por Categoria (Percentual)') # Title for pie chart
        fig_pie_dist = plot_expense_distribution_pie(expense_distribution_filtered_df)
        if fig_pie_dist:
            st.pyplot(fig_pie_dist)
            plt.close(fig_pie_dist)


    st.header('Evolução ao Longo do Tempo') # New section title
    st.markdown("Visualização do saldo acumulado, a evolução mensal das despesas por categoria e a evolução das economias ao longo do período selecionado.") # Adjusted markdown
    col5, col6 = st.columns(2) # Use new columns for detailed evolution

    with col5:
        st.subheader('Saldo Líquido Acumulado') # Shortened title
        fig2 = plot_cumulative_balance(cumulative_balance_filtered_df)
        if fig2:
            st.pyplot(fig2)
            plt.close(fig2)

    with col6:
         st.subheader('Economias Acumuladas') # Shortened title
         fig_savings = plot_cumulative_savings(cumulative_savings_filtered_df)
         if fig_savings:
             st.pyplot(fig_savings)
             plt.close(fig_savings)

    st.subheader('Evolução Mensal das Despesas por Categoria') # This chart is for evolution over time
    fig4 = plot_monthly_category_expenses(monthly_category_expense_filtered_df)
    if fig4:
        st.pyplot(fig4)
        plt.close(fig4)

    # Add section for raw expense data table
    st.header('Dados de Despesas Detalhados')
    st.markdown("Visualização em tabela das despesas do período selecionado.")

    # Filter dataframe to show only Expense type for the table
    expense_data_for_table = date_filtered_df[date_filtered_df['Tipo'] == 'Expense'].copy()

    if not expense_data_for_table.empty:
        # Use st.expander to show/hide the table
        with st.expander("Ver Tabela de Despesas"):
            # Select relevant columns for display in the table
            table_cols = ['Data', 'Descrição', 'Categoria', 'Valor', 'Recorrente']
            st.dataframe(expense_data_for_table[table_cols].reset_index(drop=True))
    else:
        st.info("Nenhum dado de despesa disponível para o período selecionado.")


if __name__ == '__main__':
    main()