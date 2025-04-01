import streamlit as st
import json
import os
import requests
import datetime
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import Counter
import re
import ssl
import socket
import tempfile
import zipfile
import io
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import google.generativeai as genai
import serpapi
import xml.dom.minidom as md

# Import the required modules
from Crawler import crawl_website
from icp import ICPChatbot
from seocheck import SEOAnalyzer

st.set_page_config(page_title="All-in-One SEO and Content Dashboard", page_icon="🚀", layout="wide")

# Hard-coded API keys
GEMINI_API_KEY = "AIzaSyC0gydmJEiVRFok1svYx3XPdmFN1WqBp2Q"
SERPAPI_API_KEY = "e8ba07c3494f92a8c88f9a4c4a6fc70263b750c9c5697247e05c790535284384"

# Initialize APIs
genai.configure(api_key=GEMINI_API_KEY)
client = serpapi.Client(api_key=SERPAPI_API_KEY)

# Custom CSS
def load_custom_css():
    st.markdown("""
    <style>
    /* Astute AI Color Scheme */
    :root {
        --primary: #8b5cf6;        
        --primary-light: #a78bfa;  
        --primary-dark: #7c3aed;   
        --secondary: #c084fc;      
        --secondary-light: #d8b4fe; 
        --secondary-dark: #a855f7; 
        --accent: #e879f9;         
        --accent-light: #f5d0fe;   
        --accent-dark: #d946ef;    
        --dark: #1e293b;          
        --light: #faf5ff;          
        --gray-100: #f9fafb;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #94a3b8;       
        --gray-500: #64748b;      
        --tertiary: #a78bfa;       
        --quaternary: #93c5fd;     
        --neutral: #f8fafc;        
    }

    /* Base styles */
    body {
        font-family: 'Poppins', sans-serif;
        background-color: var(--neutral);
        color: var(--dark);
        line-height: 1.6;
    }

    /* Header Styles */
    .app-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem 0;
        background: linear-gradient(to right, var(--primary-light), var(--primary-dark));
        border-radius: 10px;
        color: white;
    }

    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white;
    }

    .app-subtitle {
        font-size: 1.1rem;
        color: white;
        opacity: 0.9;
    }

    /* Section headers */
    .section-header {
        margin-bottom: 2rem;
        border-bottom: 2px solid var(--primary-light);
        padding-bottom: 0.5rem;
    }

    .section-header h2 {
        color: var(--primary-dark);
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }

    .section-header p {
        color: var(--gray-500);
    }

    /* Buttons */
    .stButton>button {
        border-radius: 50px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:first-child:not(:disabled) {
        background-color: var(--primary) !important;
        border-color: var(--primary) !important;
    }

    .stButton>button:first-child:not(:disabled):hover {
        background-color: var(--primary-dark) !important;
        border-color: var(--primary-dark) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }

    /* Process Step Cards */
    .process-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        border-left: 4px solid var(--primary);
    }

    .process-card h3 {
        color: var(--primary-dark);
        margin-bottom: 0.5rem;
    }

    .process-card p {
        color: var(--gray-500);
        font-size: 0.9rem;
    }

    /* Feature Cards */
    .feature-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        text-align: center;
        height: 100%;
        transition: transform 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
    }

    .feature-card h3 {
        color: var(--primary-dark);
        margin: 1rem 0;
    }

    .feature-card p {
        color: var(--gray-500);
        font-size: 0.9rem;
    }

    .feature-icon {
        font-size: 2rem;
        color: var(--primary);
    }

    /* Dashboard Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        border: 1px solid var(--gray-200);
        border-bottom: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-light) !important;
        color: white !important;
        font-weight: bold;
    }

    /* Keyword chips */
    .keyword-chip {
        background-color: var(--primary-light);
        color: white;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Expanders */
    .stExpander {
        border: 1px solid var(--gray-200) !important;
        border-radius: 12px !important;
        margin-bottom: 1rem;
    }

    /* Metrics */
    .stMetric {
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 1rem;
        background-color: white;
    }

    /* Step Progress */
    .step-container {
        display: flex;
        margin-bottom: 2rem;
        position: relative;
    }

    .step-container:before {
        content: '';
        position: absolute;
        top: 20px;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gray-300);
        z-index: 0;
    }

    .step {
        flex: 1;
        text-align: center;
        padding-top: 40px;
        position: relative;
    }

    .step-number {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: var(--gray-300);
        color: white;
        display: flex;
        justify-content: center;
        align-items: center;
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1;
    }

    .step.active .step-number {
        background-color: var(--primary);
    }

    .step.completed .step-number {
        background-color: var(--accent);
    }

    .step-title {
        font-size: 0.9rem;
        color: var(--gray-500);
        margin-top: 0.5rem;
    }

    .step.active .step-title {
        color: var(--primary-dark);
        font-weight: bold;
    }

    .step.completed .step-title {
        color: var(--accent-dark);
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------- SITEMAP GENERATOR FUNCTIONS -----------------

def generate_sitemap(urls, output_file="sitemap.xml"):
    """Generate sitemap.xml from a list of URLs"""
    
    doc = md.getDOMImplementation().createDocument(None, "urlset", None)
    root = doc.documentElement
    root.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for url in urls:
        url_element = doc.createElement("url")
        
        loc = doc.createElement("loc")
        loc_text = doc.createTextNode(url)
        loc.appendChild(loc_text)
        url_element.appendChild(loc)
        
        lastmod = doc.createElement("lastmod")
        lastmod_text = doc.createTextNode(today)
        lastmod.appendChild(lastmod_text)
        url_element.appendChild(lastmod)
        
        changefreq = doc.createElement("changefreq")
        changefreq_text = doc.createTextNode("weekly")
        changefreq.appendChild(changefreq_text)
        url_element.appendChild(changefreq)
        
        priority_value = "1.0" if url == urls[0] else "0.8"
        priority = doc.createElement("priority")
        priority_text = doc.createTextNode(priority_value)
        priority.appendChild(priority_text)
        url_element.appendChild(priority)
        
        root.appendChild(url_element)
    
    return doc.toprettyxml(indent="  ")

def generate_robots_txt(main_url, sitemap_filename="sitemap.xml"):
    """Generate robots.txt file with reference to sitemap"""
    base_url = f"{urlparse(main_url).scheme}://{urlparse(main_url).netloc}"
    sitemap_url = urljoin(base_url, sitemap_filename)
    
    content = f"""# robots.txt generated on {datetime.datetime.now().strftime("%Y-%m-%d")}
User-agent: *
Allow: /
# Disallow potential admin or private areas
Disallow: /admin/
Disallow: /private/
Disallow: /login/
Disallow: /wp-admin/
Disallow: /wp-login/
Disallow: /cart/
Disallow: /checkout/
Disallow: /auth/admin/
# Sitemap location
Sitemap: {sitemap_url}
"""
    return content

def create_zip_file(sitemap_content, robots_content):
    """Create a zip file containing sitemap.xml and robots.txt"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("sitemap.xml", sitemap_content)
        zipf.writestr("robots.txt", robots_content)
    
    zip_buffer.seek(0)
    return zip_buffer

# ----------------- BLOG GENERATOR FUNCTIONS -----------------

class BlogCalendarGenerator:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.keywords = []
        self.seo_insights = ""
        self.icp_data = {}
        self.blog_calendar = []
        self.current_blog_index = 0
        self.blogs = []

    def load_data(self, keywords_data, seo_data, icp_data) -> None:
        """Load all required data files."""
        
        try:
            if isinstance(keywords_data, dict) and "all_keywords" in keywords_data:
                self.keywords = keywords_data["all_keywords"]
            else:
                self.keywords = keywords_data
            st.success("✅ Successfully loaded keywords")
        except Exception as e:
            st.error(f"❌ Error loading keywords: {str(e)}")
            raise

        try:
            self.seo_insights = seo_data
            st.success("✅ Successfully loaded SEO insights")
        except Exception as e:
            st.error(f"❌ Error loading SEO insights: {str(e)}")
            raise

        try:
            self.icp_data = icp_data
            st.success("✅ Successfully loaded ICP data")
        except Exception as e:
            st.error(f"❌ Error loading ICP data: {str(e)}")
            raise

    def generate_calendar(self, start_date: datetime.date, duration_months: int = 6, blogs_per_week: int = 2):
        """Generate a blog calendar for the specified duration."""
        with st.status("🔄 Generating blog calendar..."):
            
            prompt = f"""
            Create a {duration_months}-month blog content calendar with {blogs_per_week} blog posts per week starting from {start_date.strftime('%Y-%m-%d')}.

            Here are the important keywords that must be incorporated into the blog topics:
            {json.dumps(self.keywords, indent=2)}

            Here are the SEO insights to consider:
            {self.seo_insights}

            Here is the Ideal Customer Profile information:
            {json.dumps(self.icp_data, indent=2)}

            For each blog post, provide:
            1. Publishing date (starting from {start_date.strftime('%Y-%m-%d')}, typically on working days)
            2. Blog title
            3. Primary target keyword
            4. Brief description (2-3 sentences)

            Return the information as a valid JSON array with objects containing these fields:
            "date", "title", "primary_keyword", "description"
            """

            try:
                response = self.model.generate_content(prompt)
                response_text = response.text

                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1

                if json_start == -1 or json_end == 0:
                    raise ValueError("Failed to parse JSON response from LLM")

                json_str = response_text[json_start:json_end]
                self.blog_calendar = json.loads(json_str)

                st.success(f"✅ Successfully generated a blog calendar with {len(self.blog_calendar)} topics")
                return self.blog_calendar

            except Exception as e:
                st.error(f"❌ Error generating blog calendar: {str(e)}")
                raise

    def display_calendar(self) -> pd.DataFrame:
        """Display the generated blog calendar in a tabular format."""
        if not self.blog_calendar:
            st.warning("⚠ No blog calendar generated yet.")
            return pd.DataFrame()

        df = pd.DataFrame(self.blog_calendar)
        return df

    def generate_blog(self, blog_index: int):
        """Generate a full blog post based on a topic from the calendar."""
        if not self.blog_calendar:
            st.warning("⚠ No blog calendar generated yet.")
            return {}

        if blog_index >= len(self.blog_calendar):
            st.warning("⚠ No more blog topics in the calendar.")
            return {}

        blog_topic = self.blog_calendar[blog_index]
        
        with st.status(f"🔄 Generating blog: {blog_topic['title']}..."):
            
            prompt = f"""
            Write a complete blog post based on the following information:

            Blog title: {blog_topic['title']}
            Primary keyword: {blog_topic['primary_keyword']}
            Description: {blog_topic['description']}
            Publishing date: {blog_topic['date']}

            Consider these SEO insights:
            {self.seo_insights}

            Consider this Ideal Customer Profile:
            {json.dumps(self.icp_data, indent=2)}

            Additional keywords to incorporate:
            {json.dumps([k for k in self.keywords if k != blog_topic['primary_keyword']][:5], indent=2)}

            Create a comprehensive blog post with:
            1. Engaging introduction
            2. 4-6 structured sections with subheadings (H2s and H3s)
            3. Actionable tips or insights
            4. Conclusion with call-to-action
            5. Total word count: 1200-1500 words

            Format the blog post in Markdown.
            """

            try:
                response = self.model.generate_content(prompt)
                blog_content = response.text

                blog = {
                    "index": blog_index,
                    "date": blog_topic['date'],
                    "title": blog_topic['title'],
                    "primary_keyword": blog_topic['primary_keyword'],
                    "content": blog_content
                }

                self.blogs.append(blog)
                
                return blog

            except Exception as e:
                st.error(f"❌ Error generating blog: {str(e)}")
                raise

# ----------------- SEO ANALYSIS FUNCTIONS -----------------

def generate_seo_report(results):
    """Generate a comprehensive text report from analysis results"""
    report = []
    
    # General Information
    report.append("="*50)
    report.append("SEO ANALYSIS REPORT")
    report.append("="*50)
    report.append(f"\nURL: {results['general_info']['url']}")
    report.append(f"Date: {results['general_info']['date']}")
    report.append(f"User Agent: {results['general_info']['user_agent']}\n")

    # On-Page Factors
    report.append("\n" + "-"*50)
    report.append("ON-PAGE SEO FACTORS")
    report.append("-"*50)
    
    # Title analysis
    title = results['on_page']['title']
    report.append(f"\nTitle Tag: {title['text']}")
    report.append(f"Length: {title['length']} characters, {title['word_count']} words")
    if title['issues']:
        report.append("Issues:")
        for issue in title['issues']:
            report.append(f"  - {issue}")

    # Meta description analysis
    meta = results['on_page']['meta_description']
    report.append(f"\nMeta Description: {meta['text']}")
    report.append(f"Length: {meta['length']} characters, {meta['word_count']} words")
    if meta['issues']:
        report.append("Issues:")
        for issue in meta['issues']:
            report.append(f"  - {issue}")

    # Content analysis
    text = results['on_page']['text']
    report.append(f"\nText Content: {text['word_count']} words")
    if text['issues']:
        report.append("Issues:")
        for issue in text['issues']:
            report.append(f"  - {issue}")

    # Semantic Analysis
    report.append("\n" + "-"*50)
    report.append("SEMANTIC ANALYSIS")
    report.append("-"*50)
    
    sem = results['semantics']
    report.append("\nTop Keywords:")
    for kw in sem['top_keywords'][:5]:
        report.append(f"  - {kw['keyword']} (Count: {kw['count']}, Density: {kw['density']}%)")

    report.append(f"\nReadability Score: {sem['readability']['flesch_score']}")
    report.append(f"Readability Level: {sem['readability']['level']}")

    # Content Structure
    report.append("\n" + "-"*50)
    report.append("CONTENT STRUCTURE")
    report.append("-"*50)
    
    content = results['content']
    report.append("\nMost Common Words:")
    for word, count in list(content['word_frequencies'].items())[:10]:
        report.append(f"  - {word}: {count}")

    return "\n".join(report)

def extract_keywords_with_gemini(content, business_description):
    """Use Gemini to extract relevant keywords based on content and business context"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Analyze the following website content and business description to extract the most relevant keywords:
        
        BUSINESS DESCRIPTION:
        {business_description}
        
        WEBSITE CONTENT:
        {content}
        
        Return a JSON list of keywords in this format:
        {{
            "keywords": ["keyword1", "keyword2", "keyword3"]
        }}
        
        IMPORTANT: 
        - Only return valid JSON format
        - Do not include any additional text or markdown
        - Return between 5-15 most relevant keywords
        """
        
        response = model.generate_content(prompt)
        
        # Clean the response to extract just the JSON portion
        try:
            # Try to parse the entire response as JSON first
            response_json = json.loads(response.text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from within the response
            json_str = response.text.split('```json')[1].split('```')[0] if '```json' in response.text else response.text
            response_json = json.loads(json_str)
        
        # Ensure the response has the expected structure
        if 'keywords' not in response_json:
            response_json['keywords'] = []
            
        return response_json
        
    except Exception as e:
        st.error(f"Error extracting keywords: {str(e)}")
        return {"keywords": []}

# ----------------- MAIN APP -----------------

def main():
    # Load custom CSS
    load_custom_css()
    
    # Page Header
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">All-in-One SEO & Content Dashboard</h1>
        <p class="app-subtitle">Analyze, Optimize, Create, and Schedule - All in One Place</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    if 'icp_complete' not in st.session_state:
        st.session_state.icp_complete = False
    
    if 'icp_data' not in st.session_state:
        st.session_state.icp_data = None
    
    if 'website_crawled' not in st.session_state:
        st.session_state.website_crawled = False
    
    if 'crawled_links' not in st.session_state:
        st.session_state.crawled_links = []
    
    if 'selected_link' not in st.session_state:
        st.session_state.selected_link = None
    
    if 'seo_analysis_done' not in st.session_state:
        st.session_state.seo_analysis_done = False
    
    if 'seo_results' not in st.session_state:
        st.session_state.seo_results = None
    
    if 'report_text' not in st.session_state:
        st.session_state.report_text = None
    
    if 'keyword_data' not in st.session_state:
        st.session_state.keyword_data = None
    
    if 'tech_seo_checked' not in st.session_state:
        st.session_state.tech_seo_checked = False
        
    if 'blog_calendar_generated' not in st.session_state:
        st.session_state.blog_calendar_generated = False
        
    if 'blog_generator' not in st.session_state:
        st.session_state.blog_generator = None
        
    if 'calendar_df' not in st.session_state:
        st.session_state.calendar_df = None
        
    if 'blog_content' not in st.session_state:
        st.session_state.blog_content = None
    
    # Progress Steps Display
    st.markdown("""
    <div class="step-container">
        <div class="step {0}">
            <div class="step-number">1</div>
            <div class="step-title">ICP Setup</div>
        </div>
        <div class="step {1}">
            <div class="step-number">2</div>
            <div class="step-title">Website Analysis</div>
        </div>
        <div class="step {2}">
            <div class="step-number">3</div>
            <div class="step-title">SEO & Keywords</div>
        </div>
        <div class="step {3}">
            <div class="step-number">4</div>
            <div class="step-title">Content Planning</div>
        </div>
        <div class="step {4}">
            <div class="step-number">5</div>
            <div class="step-title">Blog Generation</div>
        </div>
    </div>
    """.format(
        "active" if st.session_state.step == 1 else "completed" if st.session_state.step > 1 else "",
        "active" if st.session_state.step == 2 else "completed" if st.session_state.step > 2 else "",
        "active" if st.session_state.step == 3 else "completed" if st.session_state.step > 3 else "",
        "active" if st.session_state.step == 4 else "completed" if st.session_state.step > 4 else "",
        "active" if st.session_state.step == 5 else "completed" if st.session_state.step > 5 else ""
    ), unsafe_allow_html=True)
    
    # Step 1: ICP Setup
    if st.session_state.step == 1:
        st.markdown("""
        <div class="section-header">
            <h2>Step 1: Create Your Ideal Customer Profile (ICP)</h2>
            <p>Let's start by understanding your business and target audience.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.icp_complete:
            chatbot = ICPChatbot()
            chatbot.render_form()
            
            if st.session_state.get('form_complete', False):
                filename, insights = chatbot.save_form_data()
                
                with open(filename, 'r') as f:
                    st.session_state.icp_data = json.load(f)
                
                st.session_state.icp_complete = True
                st.session_state.step = 2
                st.rerun()
        else:
            st.session_state.step = 2
            st.rerun()
    
    # Step 2: Website Analysis
    elif st.session_state.step == 2:
        st.markdown("""
        <div class="section-header">
            <h2>Step 2: Website Analysis</h2>
            <p>Let's analyze your website structure to identify important pages.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get website URL from ICP data
        icp_url = None
        if st.session_state.icp_data and 'form_data' in st.session_state.icp_data:
            icp_url = st.session_state.icp_data['form_data'].get('website_url', None)
        
        url = st.text_input(
            "Enter your website URL (e.g., https://example.com)",
            value=icp_url if icp_url else "",
            key="analysis_url"
        )
        
        if st.button("Crawl Website", key="crawl_btn"):
            if url:
                with st.spinner("Crawling website... Please wait, this may take a minute..."):
                    crawled_links = crawl_website(url)
                    st.session_state.crawled_links = crawled_links
                    st.session_state.website_crawled = True
                    
                    # Save to file for reference
                    os.makedirs("data", exist_ok=True)
                    json_filename = "data/crawled_links.json"
                    with open(json_filename, "w") as f:
                        json.dump(crawled_links, f, indent=4)
                    
                    st.success(f"✅ Crawling completed! Found {len(crawled_links)} pages.")
                    
                    if crawled_links:
                        st.session_state.step = 3
                        st.rerun()
            else:
                st.error("Please enter a valid URL")
    
    # Step 3: SEO Analysis and Keywords
    elif st.session_state.step == 3:
        st.markdown("""
        <div class="section-header">
            <h2>Step 3: SEO Analysis and Keywords</h2>
            <p>Analyze your website's SEO performance and extract relevant keywords.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show ICP insights in sidebar
        with st.sidebar:
            st.header("ICP Insights")
            if st.session_state.icp_data:
                for i, insight in enumerate(st.session_state.icp_data.get('insights', []), 1):
                    st.markdown(f"{i}. {insight}")
        
        # Display crawled pages
        st.subheader("Select a page to analyze:")
        selected_link = st.selectbox(
            "Choose a page from your website:",
            st.session_state.crawled_links,
            key="link_selection"
        )
        st.session_state.selected_link = selected_link
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Run SEO Analysis", key="seo_btn"):
                if st.session_state.selected_link:
                    with st.spinner("Analyzing SEO... This may take a moment"):
                        try:
                            analyzer = SEOAnalyzer(st.session_state.selected_link)
                            results = analyzer.analyze()
                            st.session_state.seo_results = results
                            
                            report_text = generate_seo_report(results)
                            st.session_state.report_text = report_text
                            
                            domain = urlparse(st.session_state.selected_link).netloc
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            os.makedirs("reports", exist_ok=True)
                            filename = f"reports/{domain}_{timestamp}_report.txt"
                            
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(report_text)

                            st.session_state.seo_analysis_done = True
                            st.success("✅ SEO analysis completed!")
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                else:
                    st.warning("Please select a link first")
        
        with col2:
            # Check for robots.txt and sitemap.xml
            if st.session_state.selected_link:
                main_url = st.session_state.crawled_links[0]
                parsed_url = urlparse(main_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                robots_url = f"{base_url}/robots.txt"
                sitemap_url = f"{base_url}/sitemap.xml"
                
                has_robots_txt = False
                has_sitemap_xml = False
                
                try:
                    robots_response = requests.get(robots_url, timeout=5)
                    has_robots_txt = robots_response.status_code == 200
                except:
                    pass
                
                try:
                    sitemap_response = requests.get(sitemap_url, timeout=5)
                    has_sitemap_xml = sitemap_response.status_code == 200
                except:
                    pass
                
                tech_seo_issues = []
                if not has_robots_txt:
                    tech_seo_issues.append("robots.txt")
                if not has_sitemap_xml:
                    tech_seo_issues.append("sitemap.xml")
                
                if tech_seo_issues:
                    missing_files = " and ".join(tech_seo_issues)
                    st.warning(f"⚠️ Your website is missing {missing_files}")
                    
                    if st.button("Generate Technical SEO Files", key="tech_seo_btn"):
                        sitemap_content = generate_sitemap(st.session_state.crawled_links)
                        robots_content = generate_robots_txt(main_url)
                        
                        zip_file = create_zip_file(sitemap_content, robots_content)
                        
                        st.download_button(
                            label="Download Technical SEO Files",
                            data=zip_file,
                            file_name="technical_seo_files.zip",
                            mime="application/zip"
                        )
                        
                        st.session_state.tech_seo_checked = True
                else:
                    st.success("✅ Your website has both robots.txt and sitemap.xml")
                    st.session_state.tech_seo_checked = True
        
        # Display SEO Analysis Results if available
        if st.session_state.seo_analysis_done and st.session_state.seo_results:
            results = st.session_state.seo_results
            
            st.markdown("""
            <div class="section-header">
                <h2>SEO Analysis Results</h2>
                <p>Review the performance of your selected page.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Download report button
            if st.session_state.report_text:
                st.download_button(
                    label="Download SEO Report",
                    data=st.session_state.report_text,
                    file_name="seo_analysis_report.txt",
                    mime="text/plain",
                    key="download_report"
                )
            
            # Extract keywords button
            if st.button("Extract Keywords From Content", key="extract_keywords_btn"):
                with st.spinner("Analyzing content and extracting keywords..."):
                    try:
                        # Get content from SEO results
                        content = "\n".join([
                            results['on_page']['title']['text'],
                            results['on_page']['meta_description']['text'],
                            " ".join([kw['keyword'] for kw in results['semantics']['top_keywords']])
                        ])
                        
                        business_desc = ""
                        if st.session_state.icp_data and 'form_data' in st.session_state.icp_data:
                            business_desc = st.session_state.icp_data['form_data'].get('business_description', '')
                        
                        keyword_data = extract_keywords_with_gemini(content, business_desc)
                        st.session_state.keyword_data = keyword_data
                        
                        st.success("✅ Keywords extracted successfully!")
                        
                        # Save keywords to file
                        os.makedirs("data", exist_ok=True)
                        with open("data/extracted_keywords.json", "w") as f:
                            json.dump(keyword_data, f, indent=4)
                            
                        # Move to next step if both SEO analysis and keywords extraction are done
                        if st.session_state.tech_seo_checked:
                            st.session_state.step = 4
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error extracting keywords: {str(e)}")
            
            # Display SEO Results in expanders
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("On-Page SEO Analysis", expanded=True):
                    on_page = results['on_page']
                    
                    st.subheader("Title Tag")
                    st.write(f"**Text:** {on_page['title']['text']}")
                    st.write(f"**Length:** {on_page['title']['length']} characters, {on_page['title']['word_count']} words")
                    if on_page['title']['issues']:
                        st.write("**Issues:**")
                        for issue in on_page['title']['issues']:
                            st.warning(issue)
                    
                    st.subheader("Meta Description")
                    st.write(f"**Text:** {on_page['meta_description']['text']}")
                    st.write(f"**Length:** {on_page['meta_description']['length']} characters, {on_page['meta_description']['word_count']} words")
                    if on_page['meta_description']['issues']:
                        st.write("**Issues:**")
                        for issue in on_page['meta_description']['issues']:
                            st.warning(issue)
                    
                    st.subheader("Content Analysis")
                    st.write(f"**Word Count:** {on_page['text']['word_count']} words")
                    if on_page['text']['issues']:
                        st.write("**Issues:**")
                        for issue in on_page['text']['issues']:
                            st.warning(issue)
            
            with col2:
                with st.expander("Semantic Analysis", expanded=True):
                    sem = results['semantics']
                    
                    st.subheader("Top Keywords")
                    for kw in sem['top_keywords'][:5]:
                        st.write(f"**{kw['keyword']}** - {kw['count']} occurrences ({kw['density']}% density)")
                    
                    st.subheader("Readability")
                    st.write(f"**Score:** {sem['readability']['flesch_score']}")
                    st.write(f"**Level:** {sem['readability']['level']}")
                
                # If we have keywords extracted, display them
                if st.session_state.keyword_data and 'keywords' in st.session_state.keyword_data:
                    with st.expander("Extracted Keywords", expanded=True):
                        st.subheader("Recommended Keywords for Content")
                        
                        cols = st.columns(3)
                        for i, keyword in enumerate(st.session_state.keyword_data['keywords']):
                            with cols[i % 3]:
                                st.markdown(f"""
                                <div class="keyword-chip">
                                    {keyword}
                                </div>
                                """, unsafe_allow_html=True)
    
    # Step 4: Content Calendar
    elif st.session_state.step == 4:
        st.markdown("""
        <div class="section-header">
            <h2>Step 4: Content Calendar</h2>
            <p>Generate a blog content calendar based on your ICP and keywords.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.blog_calendar_generated:
            # Display extracted keywords in sidebar
            with st.sidebar:
                st.header("Your Keywords")
                if st.session_state.keyword_data and 'keywords' in st.session_state.keyword_data:
                    for i, keyword in enumerate(st.session_state.keyword_data['keywords'], 1):
                        st.write(f"{i}. {keyword}")
            
            # Calendar settings
            st.subheader("Content Calendar Settings")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                start_date = st.date_input(
                    "Start Date", 
                    value=datetime.date.today() + datetime.timedelta(days=(7 - datetime.date.today().weekday()) % 7),
                    help="Date to start the content calendar (defaults to next Monday)"
                )
            with col2:
                duration_months = st.number_input(
                    "Duration (Months)", 
                    min_value=1, 
                    max_value=12, 
                    value=3,
                    help="Number of months to generate the calendar for"
                )
            with col3:
                blogs_per_week = st.number_input(
                    "Blogs Per Week", 
                    min_value=1, 
                    max_value=5, 
                    value=2,
                    help="Number of blog posts to generate per week"
                )
            
            # SEO insights from analysis
            if st.session_state.report_text:
                seo_insights = st.session_state.report_text
            else:
                seo_insights = "Focus on creating content with at least 500 words. Include target keywords in headings and first paragraph."
            
            if st.button("Generate Content Calendar", key="calendar_btn"):
                try:
                    # Initialize blog generator
                    generator = BlogCalendarGenerator()
                    
                    # Load data
                    keywords_data = st.session_state.keyword_data.get('keywords', []) if st.session_state.keyword_data else []
                    generator.load_data(
                        keywords_data=keywords_data,
                        seo_data=seo_insights,
                        icp_data=st.session_state.icp_data.get('form_data', {})
                    )
                    
                    # Generate calendar
                    generator.generate_calendar(start_date, duration_months, blogs_per_week)
                    
                    # Store in session state
                    st.session_state.blog_generator = generator
                    st.session_state.calendar_df = generator.display_calendar()
                    st.session_state.blog_calendar_generated = True
                    
                    st.success("Content calendar generated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating content calendar: {str(e)}")
        else:
            # Display the generated calendar
            st.subheader("Your Content Calendar")
            
            if st.session_state.calendar_df is not None:
                st.dataframe(st.session_state.calendar_df, use_container_width=True)
                
                # Download as CSV
                csv = st.session_state.calendar_df.to_csv(index=False)
                st.download_button(
                    label="Download Calendar as CSV",
                    data=csv,
                    file_name=f"content_calendar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Continue to blog generation
                if st.button("Continue to Blog Generation", key="continue_to_blog_btn"):
                    st.session_state.step = 5
                    st.rerun()
            else:
                st.warning("No calendar data available. Please regenerate the calendar.")
                st.session_state.blog_calendar_generated = False
    
    # Step 5: Blog Generation
    elif st.session_state.step == 5:
        st.markdown("""
        <div class="section-header">
            <h2>Step 5: Blog Generation</h2>
            <p>Generate full blog posts based on your content calendar.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show the calendar in a collapsed expander
        with st.expander("View Content Calendar", expanded=False):
            if st.session_state.calendar_df is not None:
                st.dataframe(st.session_state.calendar_df, use_container_width=True)
        
        # Blog selection
        if st.session_state.blog_generator is not None and st.session_state.calendar_df is not None:
            st.subheader("Select a blog to generate:")
            
            # Create options for selectbox
            blog_options = [f"{i+1}: {row['title']}" for i, row in st.session_state.calendar_df.iterrows()]
            selected_blog = st.selectbox("Select a blog topic:", blog_options)
            
            if st.button("Generate Blog Post", key="generate_blog_btn"):
                try:
                    blog_index = int(selected_blog.split(":")[0]) - 1
                    with st.spinner("Generating blog post... This may take a minute..."):
                        blog = st.session_state.blog_generator.generate_blog(blog_index)
                        st.session_state.blog_content = blog
                        st.success("Blog generated successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error generating blog: {str(e)}")
            
            # Display generated blog content
            if st.session_state.blog_content:
                st.subheader(st.session_state.blog_content["title"])
                st.write(f"*Published on:* {st.session_state.blog_content['date']}")
                st.write(f"*Primary Keyword:* {st.session_state.blog_content['primary_keyword']}")
                
                with st.expander("View Blog Content", expanded=True):
                    st.markdown(st.session_state.blog_content["content"])
                
                # Download blog
                st.download_button(
                    label="Download Blog as Markdown",
                    data=f"# {st.session_state.blog_content['title']}\n\nDate: {st.session_state.blog_content['date']}\n\n{st.session_state.blog_content['content']}",
                    file_name=f"blog_{st.session_state.blog_content['primary_keyword'].replace(' ', '_')}.md",
                    mime="text/markdown"
                )
        else:
            st.warning("Blog generator not initialized. Please go back to the Content Calendar step.")
            if st.button("Go Back to Content Calendar"):
                st.session_state.step = 4
                st.rerun()

if __name__ == "__main__":
    main()