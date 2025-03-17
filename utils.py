import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List, Tuple, Literal
from urllib.parse import urlparse
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound
import gspread
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = 30
MAX_CONTENT_LENGTH = 50000  # ~50KB
BATCH_SIZE = 100

# API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENROUTER_API_KEY and not OPENAI_API_KEY:
    raise Exception("Cần ít nhất một API key (OPENROUTER_API_KEY hoặc OPENAI_API_KEY) trong file .env")

# OpenRouter Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_HEADERS = {
    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
    'HTTP-Referer': 'https://github.com/phonghoang2k/adbot',
    'X-Title': 'ADBOT',
    'Content-Type': 'application/json',
    'OpenAI-Organization': 'org-123',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
} if OPENROUTER_API_KEY else {}

# OpenAI Configuration
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_HEADERS = {
    'Authorization': f'Bearer {OPENAI_API_KEY}',
    'Content-Type': 'application/json'
} if OPENAI_API_KEY else {}

# Model Configuration
MODEL_CONFIGS = {
    'deepseek': {
        'name': 'deepseek/deepseek-r1:free',
        'api_url': OPENROUTER_API_URL,
        'headers': OPENROUTER_HEADERS,
        'max_tokens': 1000,
        'temperature': 0.3
    },
    'gpt3.5': {
        'name': 'gpt-3.5-turbo',
        'api_url': OPENAI_API_URL,
        'headers': OPENAI_HEADERS,
        'max_tokens': 1000,
        'temperature': 0.3
    }
}

def is_valid_url(url: str) -> bool:
    """Kiểm tra URL có hợp lệ không."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_text_from_url(url: str) -> str:
    """
    Extract readable text content from a given URL.
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        str: Extracted text content
    """
    if not is_valid_url(url):
        raise ValueError("URL không hợp lệ")
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                print(f"Lần thử {attempt + 1} thất bại, đang thử lại...")
                time.sleep(RETRY_DELAY)
                
        # Detect encoding
        if response.encoding == 'ISO-8859-1':
            response.encoding = 'utf-8'
        else:
            response.encoding = response.apparent_encoding
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript', 'meta', 'link']):
            element.decompose()
            
        # Try to find main article content
        article = None
        
        # Các class phổ biến cho nội dung chính
        content_classes = [
            'article-content', 'article-body', 'article-text',
            'content', 'main-content', 'post-content',
            'entry-content', 'story-content', 'detail-content',
            'article-detail', 'article-main', 'article'
        ]
        
        # Tìm theo class
        for class_name in content_classes:
            article = soup.find(class_=re.compile(class_name, re.I))
            if article:
                break
                
        # Nếu không tìm thấy, tìm theo thẻ article hoặc main
        if not article:
            article = soup.find('article') or soup.find('main')
            
        # Nếu vẫn không tìm thấy, tìm theo cấu trúc phổ biến
        if not article:
            # Tìm div chứa nội dung chính
            main_div = soup.find('div', class_=re.compile(r'main|content|article|post', re.I))
            if main_div:
                article = main_div
                
        if article:
            # Lấy tiêu đề
            title = soup.find('h1')
            if title:
                title_text = title.get_text(strip=True)
                content = f"Tiêu đề: {title_text}\n\n"
            else:
                content = ""
                
            # Lấy nội dung chính
            paragraphs = article.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content += '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        else:
            # Fallback to all paragraph text
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            
        # Clean up content
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Remove multiple newlines
        content = re.sub(r'\s+', ' ', content)  # Remove multiple spaces
        content = content.strip()
            
        # Limit content length
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "..."
            
        if not content:
            raise Exception("Không tìm thấy nội dung trong trang web")
            
        return content
        
    except Exception as e:
        raise Exception(f"Lỗi khi trích xuất nội dung từ URL: {str(e)}")

def analyze_content(content: str, model_type: Literal['deepseek', 'gpt3.5'] = 'deepseek') -> Dict[str, str]:
    """
    Analyze content using specified AI model.
    
    Args:
        content (str): The content to analyze
        model_type (str): The model to use ('deepseek' or 'gpt3.5')
        
    Returns:
        Dict[str, str]: Analysis results with topic, summary, and conclusion
    """
    if not content:
        raise ValueError("Nội dung trống")
        
    if model_type not in MODEL_CONFIGS:
        raise ValueError(f"Model không hợp lệ. Chọn một trong: {', '.join(MODEL_CONFIGS.keys())}")
    
    config = MODEL_CONFIGS[model_type]
    
    if model_type == 'deepseek' and not OPENROUTER_API_KEY:
        raise Exception("Thiếu OPENROUTER_API_KEY trong file .env")
    elif model_type == 'gpt3.5' and not OPENAI_API_KEY:
        raise Exception("Thiếu OPENAI_API_KEY trong file .env")
        
    try:
        # Tạo prompt
        prompt = """Hãy phân tích nội dung sau và trả về kết quả theo định dạng chính xác:

Chủ đề: [chủ đề chính]
Tóm tắt: [tóm tắt ngắn gọn]
Kết luận: [kết luận chính]

Nội dung cần phân tích:
{content}

Lưu ý: Phải trả về đúng định dạng với các từ khóa 'Chủ đề:', 'Tóm tắt:', 'Kết luận:' ở đầu mỗi phần.""".format(content=content)

        data = {
            "model": config['name'],
            "messages": [
                {
                    "role": "system", 
                    "content": "Bạn là một trợ lý AI chuyên phân tích nội dung. Hãy trả về kết quả theo đúng định dạng được yêu cầu."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": config['temperature'],
            "max_tokens": config['max_tokens']
        }

        # Gọi API với retry
        print(f"\nĐang gửi request tới {model_type.upper()} API...")
        response = None
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    config['api_url'],
                    headers=config['headers'],
                    json=data,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise Exception(f"Lỗi khi gọi API sau {MAX_RETRIES} lần thử: {str(e)}")
                print(f"Lần thử {attempt + 1} thất bại, đang thử lại...")
                time.sleep(RETRY_DELAY)
        
        if not response:
            raise Exception("Không nhận được phản hồi từ API")
            
        # Xử lý kết quả
        print("Đang xử lý kết quả từ API...")
        result = response.json()
        
        if 'choices' not in result or not result['choices']:
            raise Exception("Kết quả API không hợp lệ")
            
        content = result['choices'][0]['message']['content']
        print("\nKết quả gốc từ API:")
        print(content)
        
        # Tách và chuẩn hóa các phần
        sections = {
            'Chủ đề': '',
            'Tóm tắt': '',
            'Kết luận': ''
        }
        
        # Tìm vị trí của từng phần
        current_section = None
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Kiểm tra xem dòng có phải là header không
            for section in sections.keys():
                if line.startswith(section + ':'):
                    current_section = section
                    # Lấy nội dung sau dấu :
                    content_after_colon = line[len(section + ':'):].strip()
                    if content_after_colon:
                        sections[section] = content_after_colon
                    break
            else:
                # Nếu không phải header và đang ở trong một section
                if current_section and line:
                    if sections[current_section]:
                        sections[current_section] += '\n' + line
                    else:
                        sections[current_section] = line
        
        # Chuyển key về dạng tiếng Anh để tương thích với code cũ
        result = {
            'topic': sections['Chủ đề'].strip(),
            'summary': sections['Tóm tắt'].strip(),
            'conclusion': sections['Kết luận'].strip()
        }
        
        # Kiểm tra kết quả
        empty_sections = [k for k, v in result.items() if not v]
        if empty_sections:
            print(f"\n! Cảnh báo: Các phần sau trống: {', '.join(empty_sections)}")
        
        print("\nKết quả phân tích đã xử lý:")
        for key, value in result.items():
            print(f"{key.title()}: {value}")
        
        return result
        
    except Exception as e:
        raise Exception(f"Lỗi khi phân tích nội dung với {model_type}: {str(e)}")

def analyze_with_deepseek(content: str) -> Dict[str, str]:
    """
    Analyze content using DeepSeek R1 API (Legacy function).
    """
    return analyze_content(content, model_type='deepseek')

def setup_google_sheets() -> Tuple[gspread.Client, str]:
    """Thiết lập kết nối với Google Sheets API."""
    print("\n=== Thiết lập Google Sheets API ===")
    
    # 1. Kiểm tra và đọc file credentials
    credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
    if not credentials_file:
        raise Exception("Thiếu biến GOOGLE_SHEETS_CREDENTIALS_FILE trong file .env")
        
    if not os.path.exists(credentials_file):
        raise Exception(f"Không tìm thấy file credentials: {credentials_file}")
        
    print(f"✓ Đã tìm thấy file credentials: {credentials_file}")
    
    # Đọc và kiểm tra nội dung credentials
    try:
        with open(credentials_file, 'r') as f:
            creds_content = f.read()
            if '"type": "service_account"' not in creds_content:
                raise Exception("File credentials không phải là Service Account key")
            
            creds_json = json.loads(creds_content)
            service_account_email = creds_json.get('client_email', '')
            if not service_account_email:
                raise Exception("Không tìm thấy email trong file credentials")
                
            print(f"✓ Service Account Email: {service_account_email}")
    except json.JSONDecodeError:
        raise Exception("File credentials không đúng định dạng JSON")
    
    # 2. Khởi tạo credentials
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        credentials = Credentials.from_service_account_file(
            credentials_file,
            scopes=scopes
        )
        print("✓ Đã khởi tạo credentials thành công")
    except Exception as e:
        raise Exception(f"Lỗi khởi tạo credentials: {str(e)}")
    
    # 3. Kết nối API
    try:
        client = gspread.authorize(credentials)
        print("✓ Đã kết nối với Google Sheets API")
    except Exception as e:
        raise Exception(f"Lỗi kết nối Google Sheets API: {str(e)}")
        
    return client, service_account_email

def get_or_create_spreadsheet(
    client: gspread.Client,
    service_account_email: str
) -> Tuple[gspread.Spreadsheet, gspread.Worksheet]:
    """Lấy hoặc tạo spreadsheet và worksheet."""
    print("\n=== Xử lý Spreadsheet ===")
    
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    if not spreadsheet_id:
        raise Exception("Thiếu biến GOOGLE_SHEETS_SPREADSHEET_ID trong file .env")
        
    print(f"Đang xử lý spreadsheet với ID: {spreadsheet_id}")
    
    try:
        # Thử mở spreadsheet bằng ID
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"✓ Đã tìm thấy spreadsheet")
        
        # Kiểm tra quyền truy cập
        try:
            spreadsheet.share(
                service_account_email,
                perm_type='user',
                role='writer'
            )
            print("✓ Đã cấp quyền cho service account")
        except Exception:
            print("! Service account đã có quyền truy cập")
            
    except Exception as e:
        raise Exception(f"Không thể mở spreadsheet với ID {spreadsheet_id}: {str(e)}")
    
    # Xử lý worksheet
    print("\nĐang xử lý worksheet...")
    try:
        worksheet = spreadsheet.get_worksheet(0)
        if not worksheet:
            worksheet = spreadsheet.add_worksheet(
                title="Sheet1",
                rows="1000",
                cols="20"
            )
            print("✓ Đã tạo worksheet mới")
        else:
            print("✓ Đã tìm thấy worksheet")
    except Exception as e:
        raise Exception(f"Lỗi xử lý worksheet: {str(e)}")
        
    return spreadsheet, worksheet

def update_google_sheet(data: Dict[str, str], url: str) -> None:
    """
    Update Google Sheet with analysis results.
    
    Args:
        data (Dict[str, str]): Analysis results
        url (str): Original URL analyzed
    """
    try:
        # Thiết lập kết nối
        client, service_account_email = setup_google_sheets()
        
        # Lấy hoặc tạo spreadsheet
        spreadsheet, worksheet = get_or_create_spreadsheet(client, service_account_email)
        
        # Kiểm tra và thêm headers
        try:
            headers = ['URL', 'Chủ đề', 'Tóm tắt', 'Kết luận', 'Timestamp']
            first_row = worksheet.row_values(1)
            
            if not first_row:
                print("\nThêm headers vào sheet...")
                worksheet.append_row(headers)
                print("✓ Đã thêm headers")
            else:
                print("\n✓ Headers đã tồn tại")
        except Exception as e:
            raise Exception(f"Lỗi xử lý headers: {str(e)}")
        
        # Chuẩn bị dữ liệu mới
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [
            url,
            data.get('topic', 'Không có thông tin'),
            data.get('summary', 'Không có thông tin'),
            data.get('conclusion', 'Không có thông tin'),
            timestamp
        ]
        
        # Thêm dữ liệu mới
        try:
            print("\nĐang thêm dữ liệu mới...")
            worksheet.append_row(new_row)
            print("✓ Đã thêm dữ liệu thành công")
            
            # Backup dữ liệu vào file JSON
            backup_data = {
                'timestamp': timestamp,
                'url': url,
                'analysis': data
            }
            
            backup_file = f'backup_{datetime.now().strftime("%Y%m%d")}.json'
            with open(backup_file, 'a') as f:
                json.dump(backup_data, f)
                f.write('\n')
            
            print(f"✓ Đã backup dữ liệu vào {backup_file}")
            
        except Exception as e:
            raise Exception(f"Lỗi khi thêm dữ liệu: {str(e)}")
        
        # In thông tin tổng hợp
        print("\n=== Thông tin Spreadsheet ===")
        print(f"- URL: {spreadsheet.url}")
        print(f"- Tên: {spreadsheet.title}")
        print(f"- Sheet: {worksheet.title}")
        print(f"- Số dòng hiện tại: {worksheet.row_count}")
        print("============================\n")
        
    except APIError as e:
        error_msg = str(e).lower()
        if "permission" in error_msg or "access" in error_msg:
            print("\n!!! LỖI QUYỀN TRUY CẬP !!!")
            print(f"Email service account: {service_account_email}")
            print("\nCác bước khắc phục:")
            print("1. Mở Google Sheet tại URL:", spreadsheet.url if 'spreadsheet' in locals() else 'N/A')
            print("2. Click nút Share ở góc phải")
            print("3. Thêm email service account ở trên với quyền Editor")
            print("4. Chạy lại chương trình")
            raise Exception("Lỗi quyền truy cập Google Sheet")
        else:
            raise Exception(f"Lỗi Google Sheets API: {str(e)}")
    except Exception as e:
        raise Exception(f"Lỗi cập nhật Google Sheet: {str(e)}")