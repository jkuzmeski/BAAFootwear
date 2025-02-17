# Boston Marathon Footwear Analysis

A tool to collect and analyze what shoes runners wear in the Boston Marathon. This project helps identify trends in running shoe choices among marathon participants.

## What This Tool Does

1. Collects runner data from the Boston Marathon results
2. Shows you photos of runners from MarathonFoto
3. Lets you identify what shoes each runner is wearing
4. Saves this information for later analysis

## Before You Start

You'll need:
- A computer running Windows or Mac
- Internet connection
- About 10GB of free disk space
- Basic knowledge of using command prompt (Windows) or terminal (Mac)

## Installation Guide

### Step 1: Install Python

#### Windows:
1. Go to [Python.org](https://www.python.org/downloads/)
2. Download the latest Python installer
3. Run the installer
4. ✓ Check "Add Python to PATH" during installation
5. Click "Install Now"

#### Mac:
1. Open Terminal
2. Install Homebrew if you don't have it:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
   ```
3. Install Python:
   ```
   brew install python
   ```

### Step 2: Install Chrome Browser and WebDriver

1. Install Google Chrome if you don't have it: [Download Chrome](https://www.google.com/chrome/)

2. Download ChromeDriver:
   - Go to [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Download the version that matches your Chrome browser

3. Setup ChromeDriver:
   #### Windows:
   - Create folder: `C:\Program Files (x86)\chromedriver-win64`
   - Extract chromedriver.exe to this folder

   #### Mac:
   - Extract chromedriver to `/usr/local/bin`:
     ```
     sudo mv ~/Downloads/chromedriver /usr/local/bin
     ```

### Step 3: Set Up the Project

1. Download this project:
   - Click the green "Code" button above
   - Choose "Download ZIP"
   - Extract the ZIP file somewhere on your computer

2. Open command prompt (Windows) or terminal (Mac)

3. Navigate to the project folder:
   ```
   cd path/to/extracted/folder
   ```

4. Install required software:
   ```
   pip install -r requirements.txt
   ```

## Using the Tool

1. Start the data collection:
   ```
   python src/data/make_dataset.py
   ```
   This will gather runner information from the marathon results.

2. Start the shoe identification tool:
   ```
   python src/data/ScrapingMarathonfoto.py
   ```

3. For each runner:
   - A window will open showing marathon photos
   - Another window will show shoe options
   - Click the shoe that matches what the runner is wearing
   - The tool automatically moves to the next runner

## Help & Troubleshooting

Common issues:

1. "Python not found"
   - Reinstall Python and make sure to check "Add Python to PATH"

2. "ChromeDriver error"
   - Make sure Chrome browser is installed
   - Download the matching ChromeDriver version
   - Check if ChromeDriver is in the correct location

3. "Module not found"
   - Run `pip install -r requirements.txt` again

For more help, create an issue on GitHub or contact the project maintainers.

## Privacy & Usage

- This tool only accesses publicly available race photos
- Data is stored locally on your computer
- Please use responsibly and respect marathon participants' privacy

## Contributing

Want to help improve this project? We welcome:
- Bug reports
- Feature suggestions
- Code improvements
- Documentation updates

## License

This project is shared under the MIT license. You're free to use and modify it.
