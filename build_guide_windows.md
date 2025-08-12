# Build Guide for client.py on Windows

This guide describes how to create a standalone executable for `client.py` on Windows using PyInstaller.

## Prerequisites

- A Windows OS machine.
- Python 3.x installed.
- Required packages installed as per `requirements_client.txt`.

## Steps

1. Open a Command Prompt and navigate to the project directory:
   ```
   cd /Work/projects/Deep-Live-Cam
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements_client.txt
   pip install pyinstaller
   ```

4. Build the executable with PyInstaller:
   ```
   pyinstaller --onefile --windowed client.py
   ```

   - The `--onefile` flag packages everything into a single executable.
   - The `--windowed` flag ensures no console window appears (useful for GUI apps).

5. After the build completes, the executable will be located in the `dist` folder:
   ```
   dist\client.exe
   ```

6. Test the executable by running it on your Windows machine.

*Optional:*  
If you encounter any missing module errors during runtime, add them as hidden imports:
   ```
   pyinstaller --onefile --windowed --hidden-import=module_name client.py
   ```

This guide builds a Windows exe for `client.py` on a Windows machine. If you need to build from Ubuntu, consider setting up a cross-compilation environment using Wine.

