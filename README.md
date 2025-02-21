# Automated Certificate Filler

This project automates the tedious task of filling certificates by integrating an interactive GUI with automated image processing. It allows you to load a certificate template and an Excel file with certificate data, define text areas interactively, and generate personalized certificates in batch.

## Features
- **Interactive UI:** Use a PyQt5 interface to load a certificate image and Excel file.
- **Easy Text Area Selection:** Draw boxes on the certificate to mark where text should be filled.
- **Automated Processing:** Uses inpainting and optimal font sizing to replace existing text with new data.
- **Batch Generation:** Processes multiple certificates from an Excel sheet and saves output as PDFs.

## Requirements
- Python 3.x
- PyQt5
- OpenCV (cv2)
- NumPy
- Pandas
- Pillow (PIL)
- 2. **Font Setup**:
   - Ensure system fonts for `NotoSansDevanagari`, `Mangal`, `Arial`, and `DejaVu Sans` are installed.
   - For non-Latin scripts, download fonts from [Google Fonts](https://fonts.google.com/) and place them in your system's font directory.

## Installation
1. Clone the repository.
2. Install the dependencies:
   ```
   pip install PyQt5 opencv-python numpy pandas pillow
   ```

## Usage
1. Run the application:
   ```
   python main.py
   ```
2. Load your certificate image.
3. Load the Excel file containing certificate data.
4. Draw boxes on the certificate image to specify where the text should be inserted.
5. Click "Submit" to process the certificates. The filled certificates will be saved as PDFs in the `result` folder.

## Project Structure
- **interface.py:** Implements the PyQt5 GUI for loading images, selecting text areas, and managing user inputs.
- **main.py:** Coordinates the GUI and calls the image processing routines.
- **Image_editor.py:** Handles image inpainting, text rendering, and saving the final output.


