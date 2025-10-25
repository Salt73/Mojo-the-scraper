import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
from urllib.parse import urlparse, urljoin
import re
from typing import List, Dict, Optional
import io


# For JavaScript-rendered content
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


# For scheduling
from apscheduler.schedulers.background import BackgroundScheduler
import threading


# For data visualization
import plotly.express as px
import plotly.graph_objects as go



class AdvancedWebScraper:
    """
    Advanced web scraper with multiple extraction methods,
    JavaScript handling, and data processing capabilities
    """
    
    def __init__(self, url: str, use_selenium: bool = False):
        self.url = url
        self.use_selenium = use_selenium
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.soup = None
        self.html = None
        
    def fetch_page_requests(self) -> Optional[str]:
        """Fetch page using requests (for static content)"""
        try:
            response = self.session.get(
                self.url, 
                headers=self.headers, 
                timeout=15,
                allow_redirects=True
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error fetching page: {e}")
            return None
    
    def fetch_page_selenium(self) -> Optional[str]:
        """Fetch page using Selenium (for JavaScript-rendered content)"""
        if not SELENIUM_AVAILABLE:
            st.warning("⚠️ Selenium not available. Install selenium and chromedriver.")
            return None
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            driver = webdriver.Chrome(options=options)
            driver.get(self.url)
            
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            
            html = driver.page_source
            driver.quit()
            
            return html
        except Exception as e:
            st.error(f"❌ Selenium error: {e}")
            return None
    
    def fetch_page(self) -> bool:
        """Main fetch method - chooses between requests and selenium"""
        if self.use_selenium:
            self.html = self.fetch_page_selenium()
        else:
            self.html = self.fetch_page_requests()
        
        if self.html:
            self.soup = BeautifulSoup(self.html, 'html.parser')
            return True
        return False
    
    def extract_tables(self) -> List[pd.DataFrame]:
        """Extract all HTML tables from the page"""
        try:
            tables = pd.read_html(io.StringIO(str(self.html)))
            return tables
        except ValueError:
            return []
    
    def extract_links(self) -> pd.DataFrame:
        """Extract all links from the page"""
        links_data = []
        for link in self.soup.find_all('a', href=True):
            links_data.append({
                'text': link.get_text(strip=True),
                'url': urljoin(self.url, link['href']),
                'is_external': not link['href'].startswith(('/', '#'))
            })
        return pd.DataFrame(links_data)
    
    def extract_images(self) -> pd.DataFrame:
        """Extract all images from the page"""
        images_data = []
        for img in self.soup.find_all('img'):
            images_data.append({
                'alt': img.get('alt', ''),
                'src': urljoin(self.url, img.get('src', '')),
                'title': img.get('title', '')
            })
        return pd.DataFrame(images_data)
    
    def extract_custom_selector(self, selector: str, attrs: List[str] = None) -> pd.DataFrame:
        """Extract data using custom CSS selectors"""
        if attrs is None:
            attrs = ['text']
        
        elements = self.soup.select(selector)
        data = []
        
        for element in elements:
            item = {}
            if 'text' in attrs:
                item['text'] = element.get_text(strip=True)
            if 'href' in attrs:
                item['href'] = element.get('href', '')
            if 'src' in attrs:
                item['src'] = element.get('src', '')
            if 'class' in attrs:
                item['class'] = ' '.join(element.get('class', []))
            if 'id' in attrs:
                item['id'] = element.get('id', '')
            
            # Get all attributes if 'all' specified
            if 'all' in attrs:
                item.update(element.attrs)
                item['text'] = element.get_text(strip=True)
            
            data.append(item)
        
        return pd.DataFrame(data)
    
    def extract_structured_data(self) -> Dict:
        """Extract JSON-LD and schema.org structured data"""
        structured_data = []
        
        # Find JSON-LD scripts
        for script in self.soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except json.JSONDecodeError:
                continue
        
        return structured_data
    
    def extract_meta_data(self) -> pd.DataFrame:
        """Extract meta tags information"""
        meta_data = []
        
        for meta in self.soup.find_all('meta'):
            meta_info = {
                'name': meta.get('name', ''),
                'property': meta.get('property', ''),
                'content': meta.get('content', '')
            }
            if meta_info['name'] or meta_info['property']:
                meta_data.append(meta_info)
        
        return pd.DataFrame(meta_data)
    
    def extract_text_content(self, tags: List[str] = None) -> pd.DataFrame:
        """Extract text content from specific HTML tags"""
        if tags is None:
            tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'span', 'div']
        
        content_data = []
        for tag in tags:
            elements = self.soup.find_all(tag)
            for element in elements:
                text = element.get_text(strip=True)
                if text:  # Only add non-empty text
                    content_data.append({
                        'tag': tag,
                        'content': text,
                        'length': len(text)
                    })
        
        return pd.DataFrame(content_data)



class DataProcessor:
    """Utilities for cleaning and processing scraped data"""
    
    @staticmethod
    def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Flatten MultiIndex columns to simple strings"""
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                ' '.join([str(level).strip() for level in col if str(level).strip() and str(level) != 'nan'])
                .strip()
                for col in df.columns.values
            ]
        # Clean any remaining whitespace
        df.columns = df.columns.str.strip()
        return df
    


    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and optimize DataFrame"""
        df = df.drop_duplicates()
        
        # Remove rows where **all values**  are NaN
        df = df.dropna(how='all')
        
        # Clean string columns - remove \n, \r, extra whitespace
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.replace(r'\n', ' ', regex=True)  # Replace \n with space
            df[col] = df[col].str.replace(r'\r', ' ', regex=True)  # Replace \r with space
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)  # Replace multiple spaces with single
            df[col] = df[col].str.strip()  # Remove leading/trailing whitespace
        
        # Remove empty strings
        df = df.replace('', pd.NA)
        
        return df


    
    @staticmethod
    def remove_empty_columns(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
        """Remove columns with too many missing values"""
        missing_ratio = df.isnull().sum() / len(df)
        cols_to_keep = missing_ratio[missing_ratio < threshold].index
        return df[cols_to_keep]
    
    @staticmethod
    def detect_column_types(df: pd.DataFrame) -> pd.DataFrame:
        """Auto-detect and convert column types"""
        for col in df.columns:
            # Try to convert to numeric
            try:
                df[col] = pd.to_numeric(df[col])
                continue
            except (ValueError, TypeError):
                pass
            
            # Try to convert to datetime
            try:
                df[col] = pd.to_datetime(df[col])
                continue
            except (ValueError, TypeError):
                pass
        
        return df
    
    @staticmethod
    def export_to_csv(df: pd.DataFrame, filename: str = None) -> bytes:
        """Export DataFrame to CSV"""
        if filename is None:
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return df.to_csv(index=False).encode('utf-8')
    
    @staticmethod
    def export_to_excel(df: pd.DataFrame, filename: str = None) -> bytes:
        """Export DataFrame to Excel"""
        if filename is None:
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Make a copy to avoid modifying original (as modifying the OG may cause a severe heart attack)
        df = df.copy()
        
        # Flatten columns if MultiIndex
        df = DataProcessor.flatten_columns(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Scraped Data')
        
        return output.getvalue()




    @staticmethod
    def export_to_json(df: pd.DataFrame) -> str:
        """Export DataFrame to JSON"""
        return df.to_json(orient='records', indent=2)
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict:
        """Generate summary statistics for the DataFrame"""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum()
        }



class ScraperScheduler:
    """Background scheduler for automated scraping tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.jobs = {}
    
    def add_job(self, job_id: str, url: str, interval_minutes: int, 
                export_format: str = 'csv', use_selenium: bool = False):
        """Add a new scheduled scraping job"""
        
        def scrape_job():
            try:
                scraper = AdvancedWebScraper(url, use_selenium=use_selenium)
                if scraper.fetch_page():
                    # Try to extract tables first
                    tables = scraper.extract_tables()
                    if tables:
                        df = tables[0]  
                    else:
                        # Fallback to text content
                        df = scraper.extract_text_content()
                    
                    # Save to file
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    if export_format == 'csv':
                        df.to_csv(f"scheduled_{job_id}_{timestamp}.csv", index=False)
                    elif export_format == 'excel':
                        df.to_excel(f"scheduled_{job_id}_{timestamp}.xlsx", index=False)
                    
                    print(f"✓ Job {job_id} completed at {datetime.now()}")
            except Exception as e:
                print(f"✗ Job {job_id} failed: {e}")
        
        job = self.scheduler.add_job(
            scrape_job,
            'interval',
            minutes=interval_minutes,
            id=job_id
        )
        
        self.jobs[job_id] = {
            'url': url,
            'interval': interval_minutes,
            'next_run': job.next_run_time
        }
        
        return job_id
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            return True
        return False
    
    def list_jobs(self) -> Dict:
        """List all scheduled jobs"""
        return self.jobs
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()



def main():
    # Page configuration
    st.set_page_config(
        page_title="MOJO the scraper",
        page_icon="🐵",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # some CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .success-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'scraped_data' not in st.session_state:
        st.session_state.scraped_data = None
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = ScraperScheduler()
    if 'scraping_history' not in st.session_state:
        st.session_state.scraping_history = []
    
    # Header
    st.markdown('<div class="main-header">🐵 MOJO the Scraper', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # URL Input
        url = st.text_input(
            "🌐 Website URL",
            placeholder="https://example.com",
            help="Enter the full URL of the website you want to scrape"
        )
        
        # JavaScript rendering option (for the dynamic web pages shit)
        use_selenium = st.checkbox(
            "🔄 Handle JavaScript-rendered content",
            value=False,
            help="Enable this for websites that load content dynamically with JavaScript (slower)"
        )
        
        # Extraction method 
        st.subheader("📊 Extraction Method")
        extraction_method = st.selectbox(
            "Choose extraction method:",
            [
                "Auto-detect Tables",
                "Extract Links",
                "Extract Images",
                "Extract Text Content",
                "Custom CSS Selector",
                "Meta Tags",
                "Structured Data (JSON-LD)"
            ]
        )
        
        # Custom selector input
        custom_selector = None
        custom_attrs = None
        if extraction_method == "Custom CSS Selector":
            custom_selector = st.text_input(
                "CSS Selector",
                placeholder="div.product, .item, #main-content",
                help="Enter CSS selector (e.g., 'div.classname', '#id', 'tag')"
            )
            custom_attrs = st.multiselect(
                "Attributes to extract:",
                ['text', 'href', 'src', 'class', 'id', 'all'],
                default=['text']
            )
        
        # Text content tags
        text_tags = None
        if extraction_method == "Extract Text Content":
            text_tags = st.multiselect(
                "Select HTML tags:",
                ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'span', 'div', 'a'],
                default=['h1', 'h2', 'h3', 'p']
            )
        
        st.divider()
        
        # Data cleaning options
        st.subheader("🧹 Data Cleaning")
        clean_data = st.checkbox("Remove duplicates", value=True)
        remove_empty = st.checkbox("Remove empty columns", value=True)
        auto_convert_types = st.checkbox("Auto-detect data types", value=True)
        
        st.divider()
        
        # Rate limiting (trying to convince it that I'm a human LMAO)
        st.subheader("⏱️ Rate Limiting")
        delay = st.slider(
            "Delay between requests (seconds)",
            min_value=0,
            max_value=10,
            value=2,
            help="Add delay to avoid overwhelming the server"
        )
    
    # Main content area - Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Scrape", "📅 Schedule", "📊 Data Analysis", "📚 History"])
    
    # TAB 1: Scraping
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            scrape_button = st.button("🚀 Start Scraping", type="primary", use_container_width=True)
        
        with col2:
            if st.session_state.scraped_data is not None:
                clear_button = st.button("🗑️ Clear Data", use_container_width=True)
                if clear_button:
                    st.session_state.scraped_data = None
                    st.rerun()
        
        # Scraping logic
        if scrape_button and url:
            with st.spinner("🕸️ Scraping in progress..."):
                # Add delay
                if delay > 0:
                    time.sleep(delay)
                
                # Initialize scraper
                scraper = AdvancedWebScraper(url, use_selenium=use_selenium)
                
                # Fetch page
                if scraper.fetch_page():
                    st.success("✅ Page fetched successfully!")
                    
                    # Extract data based on method
                    df = None
                    
                    try:
                        if extraction_method == "Auto-detect Tables":
                            tables = scraper.extract_tables()
                            if tables:
                                if len(tables) > 1:
                                    table_idx = st.selectbox(
                                        "Multiple tables found. Select one:",
                                        range(len(tables)),
                                        format_func=lambda x: f"Table {x+1} ({tables[x].shape[0]} rows × {tables[x].shape[1]} cols)"  # FIX 2: Use shape[0] and shape[1]
                                    )
                                    df = tables[table_idx]
                                    # FIX: Flatten MultiIndex columns
                                    if isinstance(df.columns, pd.MultiIndex):
                                        df.columns = [
                                            " ".join([str(level) for level in tup if str(level) != "nan" and level is not None]).strip()
                                            for tup in df.columns.values
                                        ]

                                else:
                                    df = tables[0]  # FIX 3: Get first table from list
                                    # FIX: Flatten MultiIndex columns
                                    df = DataProcessor.flatten_columns(df)
                                    if isinstance(df.columns, pd.MultiIndex):
                                        df.columns = [
                                            " ".join([str(level) for level in tup if str(level) != "nan" and level is not None]).strip()
                                            for tup in df.columns.values
                                        ]
                                st.success(f"✅ Found {len(tables)} table(s)")

                            else:
                                st.warning("⚠️ No tables found. Try another extraction method.")
                        
                        elif extraction_method == "Extract Links":
                            df = scraper.extract_links()
                            st.success(f"✅ Extracted {len(df)} links")
                        
                        elif extraction_method == "Extract Images":
                            df = scraper.extract_images()
                            st.success(f"✅ Extracted {len(df)} images")
                        
                        elif extraction_method == "Extract Text Content":
                            df = scraper.extract_text_content(text_tags)
                            st.success(f"✅ Extracted {len(df)} text elements")
                        
                        elif extraction_method == "Custom CSS Selector" and custom_selector:
                            df = scraper.extract_custom_selector(custom_selector, custom_attrs)
                            st.success(f"✅ Extracted {len(df)} elements")
                        
                        elif extraction_method == "Meta Tags":
                            df = scraper.extract_meta_data()
                            st.success(f"✅ Extracted {len(df)} meta tags")
                        
                        elif extraction_method == "Structured Data (JSON-LD)":
                            structured = scraper.extract_structured_data()
                            if structured:
                                st.json(structured)
                                # Convert to DataFrame if possible
                                try:
                                    df = pd.json_normalize(structured)
                                except:
                                    st.info("Structured data displayed above. Cannot convert to table format.")
                            else:
                                st.warning("⚠️ No structured data found")
                        
                        # Process data
                        if df is not None and not df.empty:
                            processor = DataProcessor()
                            
                            if clean_data:
                                df = processor.clean_dataframe(df)
                            
                            if remove_empty:
                                df = processor.remove_empty_columns(df)
                            
                            if auto_convert_types:
                                df = processor.detect_column_types(df)
                            
                            # Store in session state
                            st.session_state.scraped_data = df
                            
                            # Add to history
                            st.session_state.scraping_history.append({
                                'timestamp': datetime.now(),
                                'url': url,
                                'method': extraction_method,
                                'rows': len(df),
                                'columns': len(df.columns)
                            })
                            
                    except Exception as e:
                        st.error(f"❌ Error during extraction: {e}")
                else:
                    st.error("❌ Failed to fetch the page")
        
        elif scrape_button and not url:
            st.warning("⚠️ Please enter a URL")
        
        # Display scraped data
        if st.session_state.scraped_data is not None:
            df = st.session_state.scraped_data
            
            st.divider()
            st.subheader("📊 Scraped Data Preview")
            
            # Data summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())
            with col4:
                st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            # Data preview
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download options
            st.divider()
            st.subheader("💾 Download Data")
            
            col1, col2, col3, col4 = st.columns(4)
            
            processor = DataProcessor()
            
            with col1:
                csv_data = processor.export_to_csv(df)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                excel_data = processor.export_to_excel(df)
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col3:
                json_data = processor.export_to_json(df)
                st.download_button(
                    label="📋 Download JSON",
                    data=json_data,
                    file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col4:
                # Copy to clipboard button
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.code(df.to_csv(index=False), language="csv")
                    st.info("👆 Data displayed above - copy manually")
    
    # TAB 2: Scheduling
    with tab2:
        st.subheader("📅 Schedule Automatic Scraping")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            schedule_url = st.text_input(
                "URL to scrape automatically",
                placeholder="https://example.com"
            )
            
            schedule_interval = st.number_input(
                "Scraping interval (minutes)",
                min_value=1,
                max_value=1440,
                value=60,
                help="How often to scrape the website"
            )
            
            schedule_format = st.selectbox(
                "Export format",
                ["csv", "excel", "json"]
            )
            
            schedule_selenium = st.checkbox(
                "Use JavaScript rendering",
                value=False,
                key="schedule_selenium"
            )
            
            if st.button("➕ Add Scheduled Job", type="primary"):
                if schedule_url:
                    job_id = f"job_{len(st.session_state.scheduler.jobs) + 1}"
                    st.session_state.scheduler.add_job(
                        job_id=job_id,
                        url=schedule_url,
                        interval_minutes=schedule_interval,
                        export_format=schedule_format,
                        use_selenium=schedule_selenium
                    )
                    st.success(f"✅ Job '{job_id}' added successfully!")
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a URL")
        
        with col2:
            st.info("""
            **ℹ️ Scheduled Jobs Info**
            
            - Jobs run in the background
            - Data saved automatically
            - Files named with timestamp
            - Check 'History' tab for logs
            """)
        
        # Display active jobs
        st.divider()
        st.subheader("📋 Active Scheduled Jobs")
        
        jobs = st.session_state.scheduler.list_jobs()
        
        if jobs:
            for job_id, job_info in jobs.items():
                with st.expander(f"🔄 {job_id}", expanded=True):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**URL:** {job_info['url']}")
                        st.write(f"**Interval:** {job_info['interval']} minutes")
                    
                    with col2:
                        st.write(f"**Next Run:** {job_info['next_run']}")
                    
                    with col3:
                        if st.button("🗑️ Remove", key=f"remove_{job_id}"):
                            st.session_state.scheduler.remove_job(job_id)
                            st.success(f"✅ Job '{job_id}' removed")
                            st.rerun()
        else:
            st.info("No scheduled jobs yet. Add one above!")
    
    # TAB 3: Data Analysis
    with tab3:
        if st.session_state.scraped_data is not None:
            df = st.session_state.scraped_data
            
            st.subheader("📊 Data Analysis & Visualization")
            
            # Column statistics
            st.write("### Column Statistics")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if numeric_cols:
                selected_col = st.selectbox("Select column to analyze:", numeric_cols)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Mean", f"{df[selected_col].mean():.2f}")
                with col2:
                    st.metric("Median", f"{df[selected_col].median():.2f}")
                with col3:
                    st.metric("Std Dev", f"{df[selected_col].std():.2f}")
                with col4:
                    st.metric("Max", f"{df[selected_col].max():.2f}")
                
                # Histogram
                fig = px.histogram(
                    df,
                    x=selected_col,
                    title=f"Distribution of {selected_col}",
                    nbins=30
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Value counts for categorical columns
            st.write("### Top Values in Columns")
            
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if categorical_cols:
                cat_col = st.selectbox("Select categorical column:", categorical_cols)
                
                value_counts = df[cat_col].value_counts().head(10)
                
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Top 10 values in {cat_col}",
                    labels={'x': cat_col, 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Missing values heatmap
            st.write("### Missing Values Analysis")
            
            missing_data = df.isnull().sum()
            missing_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Missing %': (missing_data.values / len(df) * 100).round(2)
            })
            
            fig = px.bar(
                missing_df,
                x='Column',
                y='Missing %',
                title='Missing Values by Column',
                color='Missing %',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Data quality score
            st.write("### Data Quality Score")
            
            completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            uniqueness = (df.nunique().sum() / (len(df) * len(df.columns))) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=completeness,
                    title={'text': "Completeness"},
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [
                               {'range': [0, 50], 'color': "lightgray"},
                               {'range': [50, 80], 'color': "gray"},
                               {'range': [80, 100], 'color': "lightgreen"}
                           ]}
                ))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=uniqueness,
                    title={'text': "Uniqueness"},
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': "darkgreen"},
                           'steps': [
                               {'range': [0, 30], 'color': "lightgray"},
                               {'range': [30, 70], 'color': "gray"},
                               {'range': [70, 100], 'color': "lightblue"}
                           ]}
                ))
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("👆 Scrape some data first to see analysis!")
    
    # TAB 4: History
    with tab4:
        st.subheader("📚 Scraping History")
        
        if st.session_state.scraping_history:
            history_df = pd.DataFrame(st.session_state.scraping_history)
            
            st.dataframe(
                history_df,
                use_container_width=True,
                column_config={
                    'timestamp': st.column_config.DatetimeColumn(
                        'Timestamp',
                        format="DD/MM/YYYY HH:mm:ss"
                    ),
                    'url': st.column_config.TextColumn('URL', width='large'),
                    'method': 'Extraction Method',
                    'rows': st.column_config.NumberColumn('Rows', format="%d"),
                    'columns': st.column_config.NumberColumn('Columns', format="%d")
                }
            )
            
            # Statistics
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Scrapes", len(history_df))
            with col2:
                st.metric("Total Rows Scraped", history_df['rows'].sum())
            with col3:
                st.metric("Unique URLs", history_df['url'].nunique())
            
         
            if st.button("🗑️ Clear History", type="secondary"):
                st.session_state.scraping_history = []
                st.rerun()
        
        else:
            st.info("No scraping history yet. Start scraping to see history!")
    
  
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: gray; padding: 2rem;'>
            <p><strong>⚠️ Friendly Reminder:</strong></p>
            <p>You better do a useful project bro, I almost died to make this tool</p>
            <p>Have a good project 😁</p>    
            
        </div>
    """, unsafe_allow_html=True)



if __name__ == "__main__":
    main()