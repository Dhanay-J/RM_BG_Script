---

# RM_BG_Script
Helper module to remove backgrounds from images using **briaai/RMBG-2.0** on Windows.

---

## CUDA Usage
To enable CUDA support, uncomment the relevant lines in `requirements.txt` or install a suitable CUDA version as per the official **briaai/RMBG-2.0** documentation.

---

## Installation Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/Dhanay-J/RM_BG_Script.git
   ```
2. Navigate to the project directory:
   ```bash
   cd RM_BG_Script
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv env
   ```
4. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source env/bin/activate
     ```
   - On Windows:
     ```cmd
     .\env\Scripts\activate
     ```
5. Install the required dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
6. Start the application:
   ```bash
   waitress-serve --listen=127.0.0.1:5000 app:app
   ```

---

### Notes:
- Replace `python3` with `python` if you're using Windows, as `python` is typically the default command there.
- Ensure that Python 3.x is installed on your system.
- If CUDA support is enabled, verify that your GPU drivers and CUDA toolkit are correctly installed.

---