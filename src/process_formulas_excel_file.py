import sys
import formulas 

def calculate_file(path_to_file, path_to_output_folder):
    """
    Runs in like 5 minutes and takes 4.5G of RAM for a 5MB file for some reason
    The resulting file also has extension ".XLSX" so we have to take care of 
    that in the bash script
    """
    xl_model = formulas.ExcelModel().loads(path_to_file).finish()
    xl_model.calculate()
    xl_model.write(dirpath = path_to_output_folder)
    return

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python3 process_formulas_excel_file.py path_to_excel path_to_output_folder".format(len(sys.argv)))
    else:
        file_path = sys.argv[1]
        output_folder = sys.argv[2]
        calculate_file(file_path, output_folder)
