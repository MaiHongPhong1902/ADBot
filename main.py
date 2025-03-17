import sys
from utils import extract_text_from_url, analyze_with_deepseek, update_google_sheet

def main():
    """
    Main function to run the content analysis pipeline.
    """
    try:
        # Get URL from command line argument
        if len(sys.argv) != 2:
            print("Usage: python main.py <url>")
            sys.exit(1)
            
        url = sys.argv[1]
        
        # Extract content from URL
        print(f"Đang trích xuất nội dung từ {url}...")
        content = extract_text_from_url(url)
        
        if not content:
            print("Không thể trích xuất nội dung từ URL này.")
            sys.exit(1)
            
        # Analyze content with DeepSeek
        print("Đang phân tích nội dung...")
        analysis = analyze_with_deepseek(content)
        
        # Update Google Sheet
        print("Đang cập nhật Google Sheet...")
        update_google_sheet(analysis, url)
        
        # Print results
        print("\nKết quả phân tích:")
        print(f"Chủ đề: {analysis['topic']}")
        print(f"Tóm tắt: {analysis['summary']}")
        print(f"Kết luận: {analysis['conclusion']}")
        print("\nĐã cập nhật Google Sheet thành công!")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
