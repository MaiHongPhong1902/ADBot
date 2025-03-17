# ADBot - Automated Content Analysis Tool

ADBot is an automated tool for analyzing content from online news articles using AI to summarize and analyze content.

## Features

- Automatic content extraction from news articles
- Content analysis using AI (DeepSeek or GPT-3.5)
- Automatic updates to Google Sheets
- Support for multiple URL formats
- Automatic data backup

## Requirements

- Python 3.8 or higher
- OpenRouter account (for DeepSeek) or OpenAI account (for GPT-3.5)
- Google Cloud account with Google Sheets API enabled
- Required Python libraries (see requirements.txt)

## Installation

1. Clone repository:
```bash
git clone https://github.com/MaiHongPhong1902/ADBot.git
cd ADBot
```

2. Create and activate virtual environment:
```bash
conda create -n Bot python=3.8
conda activate Bot
```

3. Install required libraries:
```bash
pip install -r requirements.txt
```

4. Configure sensitive files:
   - Copy `.env.example` to `.env` and fill in your API keys
   - Create `credentials.json` from Google Cloud Console and place it in the root directory
   - DO NOT commit these files to git

5. Set up Google Cloud:
- Visit Google Cloud Console
- Create a new project or select existing one
- Enable Google Sheets API
- Create Service Account and download credentials.json
- Place credentials.json in the project root directory

## Usage

1. Run the program:
```bash
python main.py <URL>?
```

2. Enter the article URL when prompted

3. Choose AI model for analysis (DeepSeek or GPT-3.5)

4. Results will be automatically updated to Google Sheets

## Data Structure

Analysis results are stored in Google Sheets with columns:
- URL: Original article link
- Topic: Main topic of the article
- Summary: Brief content summary
- Conclusion: Main conclusions from the article
- Timestamp: Analysis time

## Data Backup

Data is automatically backed up to JSON files by date:
- Format: backup_YYYYMMDD.json
- Each entry contains timestamp, URL, and analysis results

## Error Handling

If you encounter Google Sheets access errors:
1. Open the Google Sheet at the provided URL
2. Click Share button
3. Add service account email with Editor permissions
4. Run the program again

## Important Notes

- DO NOT commit sensitive files to git:
  - `.env` (contains API keys)
  - `credentials.json` (contains Google Cloud credentials)
  - Backup files
- These files are already added to `.gitignore`
- If accidentally committed, remove them from git history immediately

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

Copyright (c) 2024 Mai Hong Phong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author

- **Mai Hong Phong**
  - Email: maihongphong.work@gmail.com
  - Phone: 0865243215
  - GitHub: [@MaiHongPhong1902](https://github.com/MaiHongPhong1902)
  - University: Ho Chi Minh City University of Technology and Education
