from interface import main as UI
from Image_editor import image_changer
import pandas as pd
from datetime import datetime

def main():
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    coordinates, file_path, excel_path = UI()
    df = pd.read_excel(excel_path)
    for index, row in df.iterrows():
        words = row.to_dict() 
        image_changer(file_path, coordinates, words, current_time)

if __name__ == "__main__":
    main()