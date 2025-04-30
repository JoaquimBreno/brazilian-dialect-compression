import requests
import os
import time
import re
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright
import urllib.parse

# Config
SEARCH_URL = "https://libgen.is/search.php?req=M%C3%A1rcia+Kambeba+&open=0&res=25&view=simple&phrase=1&column=def"
DOWNLOAD_FOLDER = os.getcwd()  # Current directory

async def setup_browser():
    """Setup Playwright browser."""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,  # Set to True to run in background
        downloads_path=DOWNLOAD_FOLDER
    )
    context = await browser.new_context(
        accept_downloads=True
    )
    
    # Enable file downloads
    page = await context.new_page()
    return playwright, browser, context, page

def extract_book_links(html_content):
    """Extract book links from the LibGen search results page."""
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []
    
    # Find all table rows that contain book data
    rows = soup.find_all('tr', valign='top')
    
    for row in rows:
        # Skip header rows
        if 'bgcolor="#C0C0C0"' in str(row):
            continue
            
        # Find the title column which is the third td
        columns = row.find_all('td')
        if len(columns) >= 10:  # Ensure we have enough columns
            title_column = columns[2]
            book_link = title_column.find('a', href=lambda href: href and 'book/index.php?md5=' in href)
            
            if book_link:
                title = book_link.get_text(strip=True)
                md5 = book_link['href'].split('md5=')[1]
                book_url = f"https://libgen.is/{book_link['href']}"
                
                # Get author
                author = columns[1].get_text(strip=True)
                
                # Get file format
                extension = columns[8].get_text(strip=True) if len(columns) > 8 else "Unknown"
                
                # Get mirror link
                mirror_td = columns[9] if len(columns) > 9 else None
                mirror_link = mirror_td.find('a')['href'] if mirror_td and mirror_td.find('a') else None
                
                books.append({
                    'title': title,
                    'author': author,
                    'md5': md5,
                    'book_url': book_url,
                    'mirror_link': mirror_link,
                    'extension': extension
                })
    
    print(f"Found {len(books)} books")
    return books

async def download_book(book_info, page):
    """Process a single book download from LibGen."""
    title = book_info['title']
    author = book_info['author']
    extension = book_info['extension']
    
    # Clean title for filename
    clean_title = re.sub(r'[\\/*?:"<>|]', '', title)  # Remove invalid filename chars
    clean_title = re.sub(r'\s+', '_', clean_title)    # Replace spaces with underscores
    filename = f"{clean_title}.{extension.lower()}"
    
    # Check if file already exists
    if os.path.exists(os.path.join(DOWNLOAD_FOLDER, filename)):
        print(f"File '{filename}' already exists. Skipping...")
        return True
    
    print(f"\nProcessing book: {title} by {author}")
    print(f"Format: {extension}")
    
    try:
        # First visit the book details page
        print(f"Visiting book page: {book_info['book_url']}")
        await page.goto(book_info['book_url'], wait_until="networkidle")
        
        # Check if we need to use the mirror link
        if book_info['mirror_link']:
            print(f"Using mirror link: {book_info['mirror_link']}")
            await page.goto(book_info['mirror_link'], wait_until="networkidle")
            
            # We're now on the mirror page, find the GET link
            get_link_selector = "a:has-text('GET')"
            get_link = await page.query_selector(get_link_selector)
            
            if get_link:
                # Setup download listener
                download_promise = page.wait_for_event('download')
                
                # Click the GET link
                await get_link.click()
                print("Clicked GET link, downloading file...")
                
                # Wait for download to start
                download = await download_promise
                print(f"Download started: {download.suggested_filename}")
                
                # Save the file with our custom filename
                await download.save_as(os.path.join(DOWNLOAD_FOLDER, filename))
                print(f"Download complete for {title}")
                
                # Small delay to ensure file is saved properly
                await asyncio.sleep(2)
                
                return True
            else:
                print("Could not find the download GET link")
                return False
        else:
            print("No mirror link found for this book")
            return False
            
    except Exception as e:
        print(f"Error downloading {title}: {str(e)}")
        return False

async def main_async():
    print("Starting Ariano Suassuna book scraper for LibGen")
    
    # Create download folder if it doesn't exist
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    
    playwright, browser, context, page = await setup_browser()
    
    try:
        # Load the search results page
        print(f"Fetching search results from {SEARCH_URL}...")
        await page.goto(SEARCH_URL, wait_until="networkidle")
        
        # Get the page content
        content = await page.content()
        
        # Extract book links
        book_links = extract_book_links(content)
        
        if not book_links:
            print("No books found! Check the website structure or URL.")
            return
        
        # Process each book
        for i, book in enumerate(book_links, 1):
            print(f"\n{'='*50}")
            print(f"Processing book {i}/{len(book_links)}: {book['title']}")
            print(f"{'='*50}")
            
            success = await download_book(book, page)
            if success:
                print(f"Successfully processed {book['title']}")
            else:
                print(f"Failed to process {book['title']}")
            
            # Small delay between books
            await asyncio.sleep(3)
            
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
    finally:
        await context.close()
        await browser.close()
        await playwright.stop()
        print("\nScraper finished")

def main():
    """Main entry point to run the async code."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 