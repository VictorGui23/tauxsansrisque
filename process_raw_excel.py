import os 
import re
import sys
import pandas as pd 
from datetime import datetime
from constants import DB_COLUMNS as db_columns
from constants import NAMES_TO_COLLECT_VPS as names_to_collect

def extract_date(text):
    pattern = r'(\d{2}_\d{2}_\d{4})'
    match = re.search(pattern, text)
    if match:
        yr = match.group(1)[6:10]
        m = match.group(1)[3:5]
        d = match.group(1)[0:2]
        outstr = yr + "-" + m + "-" + d
        return outstr
    return None

def extract_shock(text):
    text = text.lower()
    if "shock_up" in text:
        return 1
    elif "shock_down" in text:
        return -1
    else:
        return 0

def extract_va(text):
    text = text.lower()
    if "with_va" in text:
        return 1
    elif "no_va" in text:
        return 0
    else:
        return 0  # Default case if none of the expected strings are found

def process_dfs(init_data, names_to_collect):
    processed_sheets = {}
    for sheet_name in names_to_collect:
        df = init_data[sheet_name]
        # Select columns from B onwards (index 1 onwards)
        df_filtered = df.iloc[:, 1:]
        
        # Use row 2 (index 1) as column names
        new_columns = df_filtered.iloc[0]
        new_columns.iat[0] = "INDEX"
        df_filtered = df_filtered.iloc[1:]  # Now start from row 3 (index 2)
        df_filtered.columns = new_columns
        
        # Reset the index
        df_filtered = df_filtered.reset_index(drop=True)
        
        # Store the processed dataframe
        df_filtered.loc[0, "INDEX"] = "ID_COLUMN"
        df_filtered = df_filtered.fillna(0)
        processed_sheets[sheet_name] = df_filtered
    return processed_sheets

def fill_db_df(init_df, sheet_name, countries):
    indexed_df = init_df.set_index("INDEX")
    depth = 150
    rows = []

    for country in countries:
        for i in range(1, depth + 1):
            row = {
                "country": country,
                "coupon_freq": indexed_df.at["Coupon_freq", country],
                "llp": indexed_df.at["LLP", country],
                "convergence": indexed_df.at["Convergence", country],
                "ufr": indexed_df.at["UFR", country],
                "alpha": indexed_df.at["alpha", country],
                "cra": indexed_df.at["CRA", country],
                "va": indexed_df.at["VA", country],
                "period": i,
                "rate": indexed_df.at[i, country],
                "date_upload": datetime.today().strftime('%Y-%m-%d'),
                "curve_name": sheet_name,
                "date": extract_date(indexed_df.at["ID_COLUMN", country]),
                "va_int": extract_va(sheet_name),
                "shock_int": extract_shock(sheet_name)
            }
            rows.append(row)

    db_df = pd.DataFrame(rows, columns=db_columns)
    return db_df

def create_complete_db(dict_of_dfs, countries):
    dfs_list = []
    for sheet_name in dict_of_dfs.keys():
        df = fill_db_df(dict_of_dfs[sheet_name], sheet_name, countries)
        dfs_list.append(df)
    complete_db = pd.concat(dfs_list, ignore_index=True)
    complete_db = pd.DataFrame(complete_db, columns=db_columns)
    return complete_db

def file_to_db_format(path_to_input: str,
                        path_to_output_folder: str = None):
    
    file_name = os.path.basename(path_to_input)
    
    output_file = "ready_for_db_" + file_name

    curve = pd.read_excel(path_to_input, sheet_name = None, engine = "openpyxl")

    processed_sheets = process_dfs(curve, names_to_collect)

    df_spot_no_va = processed_sheets["RFR_SPOT_NO_VA"]

    countries = [x for x in df_spot_no_va.columns if x != "INDEX"]

    db = create_complete_db(processed_sheets, countries)
    print(db.head())
    if path_to_output is not None:
        db.to_excel(os.path.join(path_to_output_folder, output_file), index= False)

    return db
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 process_raw_excel.py file_path output_folder_path")
        sys.exit(1)

    path_to_file = sys.argv[1]
    path_to_output = sys.argv[2]

    file_to_db_format(path_to_file, path_to_output)

