import pandas as pd
from datetime import timedelta

def read_excel_file(file_path):
    df = pd.read_excel(file_path, sheet_name='BD')
    return df

def process_data(df):
    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
    hoje = pd.Timestamp.today().normalize().date()
    ultimos_30 = df[df['DATA'].dt.date >= (hoje - timedelta(days=30))].copy()

    # Função para checar se Formato [m] está preenchido
    def status_bolinha(val):
        return "🟢" if pd.notna(val) and str(val).strip() != "" else "🔴"

    # Pivot para cada dia e turno
    tabela = ultimos_30.pivot_table(
        index='DATA',
        columns='Turno',
        values='Formato [m]',
        aggfunc=lambda x: status_bolinha(x.iloc[0])
    ).reset_index()

    tabela = tabela.rename(columns={
        '1º - Manhã': 'Manha',
        '2º - Tarde': 'Tarde',
        '3º - Noite': 'Noite'
    })
    for col in ['Manha', 'Tarde', 'Noite']:
        if col not in tabela.columns:
            tabela[col] = "🔴"

    # Ordena pela data real (mais recente primeiro)
    tabela = tabela.sort_values('DATA', ascending=False).reset_index(drop=True)
    # Formata a data como dd/mm/aaaa
    tabela['DataFormatada'] = tabela['DATA'].dt.strftime('%d/%m/%Y')
    tabela = tabela[['DataFormatada', 'Manha', 'Tarde', 'Noite']]
    tabela.columns = ['Data', '1º - Manhã', '2º - Tarde', '3º - Noite']
    return tabela

def validate_data(daily_counts):
    valid_days = daily_counts[daily_counts >= 3]
    return valid_days.index.tolist()  # Return list of valid days with at least 3 entries