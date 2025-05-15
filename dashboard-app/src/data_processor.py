import pandas as pd
from datetime import timedelta

def read_excel_file(file_path):
    df = pd.read_excel(file_path, sheet_name='BD Checklist')
    return df

def normalize_turno(val):
    if not isinstance(val, str):
        return None
    v = val.strip().lower()
    if v.startswith('1'):
        return '1º - Manhã'
    if v.startswith('2'):
        return '2º - Tarde'
    if v.startswith('3'):
        return '3º - Noite'
    return None

def process_data(df):
    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
    # Normaliza a coluna Turno para os valores padrão
    if 'Turno' in df.columns:
        df['Turno'] = df['Turno'].apply(normalize_turno)
    hoje = pd.Timestamp.today().normalize().date()
    ultimos_30 = df[df['DATA'].dt.date >= (hoje - timedelta(days=30))].copy()

    # Seleciona as três primeiras colunas de dados após 'Turno' (por posição)
    base_cols = list(df.columns)
    try:
        turno_idx = base_cols.index('Turno')
        data_cols = base_cols[turno_idx + 1:turno_idx + 4]
    except ValueError:
        data_cols = base_cols[2:5]  # fallback

    def status_bolinha_row(row):
        return "🟢" if any(pd.notna(row[c]) and str(row[c]).strip() != "" for c in data_cols) else "🔴"
    ultimos_30['Status'] = ultimos_30.apply(status_bolinha_row, axis=1)

    tabela = ultimos_30.pivot_table(
        index='DATA',
        columns='Turno',
        values='Status',
        aggfunc='first'
    ).reset_index()

    tabela = tabela.rename(columns={
        '1º - Manhã': 'Manha',
        '2º - Tarde': 'Tarde',
        '3º - Noite': 'Noite'
    })
    for col in ['Manha', 'Tarde', 'Noite']:
        if col not in tabela.columns:
            tabela[col] = "🔴"

    tabela = tabela.sort_values('DATA', ascending=False).reset_index(drop=True)
    tabela['DataFormatada'] = tabela['DATA'].dt.strftime('%d/%m/%Y')
    tabela = tabela[['DataFormatada', 'Manha', 'Tarde', 'Noite']]
    tabela.columns = ['Data', '1º - Manhã', '2º - Tarde', '3º - Noite']
    return tabela

def validate_data(daily_counts):
    valid_days = daily_counts[daily_counts >= 3]
    return valid_days.index.tolist()  # Return list of valid days with at least 3 entries

def process_mp(filepath):
    try:
        df = pd.read_excel(filepath, sheet_name='BD Checklist', header=2)
        print(f"\nPrévia das 5 primeiras linhas de {filepath}:")
        print(df.head())
        print(f"Colunas: {df.columns.tolist()}")
        if 'Turno' in df.columns:
            print(f"Valores únicos em Turno: {df['Turno'].unique()}")
    except Exception as e:
        print(f"\nErro ao ler {filepath}: {e}")
        return pd.DataFrame(columns=['DATA', 'Manha', 'Tarde', 'Noite'])

    # Normaliza nome das colunas (DATA e Turno)
    col_map = {}
    for col in df.columns:
        col_strip = str(col).strip().lower()
        if col_strip == 'data':
            col_map[col] = 'DATA'
        elif col_strip == 'turno':
            col_map[col] = 'Turno'
    df = df.rename(columns=col_map)

    if not all(c in df.columns for c in ['DATA', 'Turno']):
        return pd.DataFrame(columns=['DATA', 'Manha', 'Tarde', 'Noite'])

    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
    df['Turno'] = df['Turno'].apply(normalize_turno)
    hoje = pd.Timestamp.today().normalize().date()
    ultimos_30 = df[df['DATA'].dt.date >= (hoje - timedelta(days=30))].copy()

    # Seleciona as três primeiras colunas de dados após 'Turno'
    base_cols = list(df.columns)
    try:
        turno_idx = base_cols.index('Turno')
        data_cols = base_cols[turno_idx + 1:turno_idx + 4]
    except ValueError:
        data_cols = base_cols[2:5]  # fallback

    def status_bolinha_row(row):
        return "🟢" if any(pd.notna(row[c]) and str(row[c]).strip() != "" for c in data_cols) else "🔴"
    ultimos_30['Status'] = ultimos_30.apply(status_bolinha_row, axis=1)

    # Remove duplicatas para DATA+Turno, mantendo o primeiro registro
    ultimos_30 = ultimos_30.drop_duplicates(subset=['DATA', 'Turno'], keep='first')

    # Gera todas as combinações possíveis de DATA x TURNO nos últimos 30 dias
    dias = ultimos_30['DATA'].dropna().dt.normalize().unique()
    turnos = ['3º - Noite', '1º - Manhã', '2º - Tarde']  # ordem ajustada
    idx = pd.MultiIndex.from_product([dias, turnos], names=['DATA', 'Turno'])
    # Junta com os dados existentes
    tabela = ultimos_30.set_index(['DATA', 'Turno'])[['Status']].reindex(idx).reset_index()
    tabela['Status'] = tabela['Status'].fillna("🔴")  # só bolinha vermelha

    # Pivot para formato final
    tabela = tabela.pivot(index='DATA', columns='Turno', values='Status').reset_index()
    tabela = tabela.rename(columns={
        '1º - Manhã': 'Manha',
        '2º - Tarde': 'Tarde',
        '3º - Noite': 'Noite'
    })
    for col in ['Noite', 'Manha', 'Tarde']:
        if col not in tabela.columns:
            tabela[col] = "🔴"
    tabela = tabela[['DATA', 'Noite', 'Manha', 'Tarde']]
    return tabela

def process_multiple_mps(files):
    all_tables = {}
    for mp, path in files.items():
        tabela = process_mp(path)
        tabela = tabela.rename(columns={
            'Noite': f'{mp}_Noite',
            'Manha': f'{mp}_Manha',
            'Tarde': f'{mp}_Tarde'
        })
        all_tables[mp] = tabela

    df_final = None
    for tabela in all_tables.values():
        if df_final is None:
            df_final = tabela
        else:
            df_final = pd.merge(df_final, tabela, on='DATA', how='outer')

    df_final = df_final.sort_values('DATA', ascending=False)
    df_final['DataFormatada'] = df_final['DATA'].dt.strftime('%d/%m/%Y')
    df_final = df_final.head(10)
    cols = ['DataFormatada']
    for mp in files.keys():
        cols += [f'{mp}_Noite', f'{mp}_Manha', f'{mp}_Tarde']
    for col in cols:
        if col not in df_final.columns:
            df_final[col] = "🔴"
    df_final = df_final[cols]
    df_final = df_final.fillna("🔴").reset_index(drop=True)
    df_final.columns = ['Data'] + [f'{mp}\n{turno}' for mp in files.keys() for turno in ['3º - Noite', '1º - Manhã', '2º - Tarde']]
    return df_final