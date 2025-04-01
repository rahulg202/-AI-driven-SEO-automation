import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import datetime
import ssl
import socket
import time
import html
from collections import Counter

class SEOAnalyzer:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        self.response = None
        self.soup = None
        self.text_content = ""
        self.word_count = 0
        self.results = {
            "general_info": {},
            "on_page": {},
            "technical": {},
            "performance": {},
            "mobile": {},
            "semantics": {},
            "content": {}
        }

    def analyze(self):
        """Run all analysis methods and return the results"""
        try:
            self.fetch_page()
            self.get_general_info()
            self.analyze_on_page_factors()
            self.analyze_technical_factors()
            self.analyze_semantics()
            self.analyze_text_content()
            return self.results
        except Exception as e:
            return {"error": str(e)}

    def fetch_page(self):
        """Fetch the webpage and prepare BeautifulSoup object"""
        start_time = time.time()
        self.response = requests.get(self.url, headers=self.headers, timeout=10)
        load_time = time.time() - start_time

        self.soup = BeautifulSoup(self.response.text, 'html.parser')

        # Extract visible text
        for script in self.soup(["script", "style"]):
            script.extract()

        self.text_content = self.soup.get_text(separator=" ", strip=True)
        self.word_count = len(self.text_content.split())

        self.results["performance"]["load_time"] = round(load_time, 2)

    def get_general_info(self):
        """Get general information about the website"""
        self.results["general_info"] = {
            "url": self.url,
            "date": datetime.datetime.now().strftime("%d.%B %Y"),
            "user_agent": self.headers['User-Agent'],
        }

    def analyze_on_page_factors(self):
        """Analyze on-page SEO factors"""
        # Title tag
        title = self.soup.title.string if self.soup.title else ""
        title_length = len(title) if title else 0
        title_word_count = len(title.split()) if title else 0

        # Meta description
        meta_desc = ""
        meta_desc_tag = self.soup.find("meta", attrs={"name": "description"})
        if meta_desc_tag:
            meta_desc = meta_desc_tag.get("content", "")
        meta_desc_length = len(meta_desc) if meta_desc else 0
        meta_desc_word_count = len(meta_desc.split()) if meta_desc else 0

        # Links analysis
        all_links = self.soup.find_all("a", href=True)
        internal_links = [link for link in all_links if self.is_internal_link(link.get("href"))]
        external_links = [link for link in all_links if not self.is_internal_link(link.get("href"))]
        links_without_title = [link for link in all_links if not link.get("title")]
        links_without_text = [link for link in all_links if not link.text.strip()]
        nofollow_links = [link for link in all_links if link.get("rel") and "nofollow" in link.get("rel")]

        # Images analysis
        images = self.soup.find_all("img")
        images_without_alt = [img for img in images if not img.get("alt")]
        images_without_title = [img for img in images if not img.get("title")]

        # Headings analysis
        h1_tags = self.soup.find_all("h1")
        h2_tags = self.soup.find_all("h2")
        h3_tags = self.soup.find_all("h3")

        # Create heading structure
        heading_structure = []
        for h1 in h1_tags:
            heading_structure.append({"tag": "h1", "text": h1.text.strip()})
        for h2 in h2_tags:
            heading_structure.append({"tag": "h2", "text": h2.text.strip()})
        for h3 in h3_tags:
            heading_structure.append({"tag": "h3", "text": h3.text.strip()})

        self.results["on_page"] = {
            "title": {
                "text": title,
                "length": title_length,
                "word_count": title_word_count,
                "issues": []
            },
            "meta_description": {
                "text": meta_desc,
                "length": meta_desc_length,
                "word_count": meta_desc_word_count,
                "issues": []
            },
            "text": {
                "word_count": self.word_count,
                "issues": []
            },
            "links": {
                "internal_count": len(internal_links),
                "external_count": len(external_links),
                "without_title": len(links_without_title),
                "without_text": len(links_without_text),
                "nofollow_count": len(nofollow_links),
                "issues": []
            },
            "images": {
                "total": len(images),
                "without_alt": len(images_without_alt),
                "without_title": len(images_without_title),
                "issues": []
            },
            "headings": {
                "h1_count": len(h1_tags),
                "h2_count": len(h2_tags),
                "h3_count": len(h3_tags),
                "structure": heading_structure,
                "issues": []
            }
        }

        # Check for issues
        if title_length < 10:
            self.results["on_page"]["title"]["issues"].append("Title is too short")
        elif title_length > 70:
            self.results["on_page"]["title"]["issues"].append("Title is too long")

        if title_word_count < 3:
            self.results["on_page"]["title"]["issues"].append("Title has too few words")

        if meta_desc_length < 50:
            self.results["on_page"]["meta_description"]["issues"].append("Meta description is too short")
        elif meta_desc_length > 160:
            self.results["on_page"]["meta_description"]["issues"].append("Meta description is too long")

        if meta_desc_word_count < 10:
            self.results["on_page"]["meta_description"]["issues"].append("Meta description has too few words")

        if self.word_count < 400:
            self.results["on_page"]["text"]["issues"].append("Text length should be more than 400 words")

        if len(external_links) < 2:
            self.results["on_page"]["links"]["issues"].append("Too few outbound links")

        if len(links_without_title) > 0:
            self.results["on_page"]["links"]["issues"].append(f"{len(links_without_title)} links without TITLE attribute")

        if len(links_without_text) > 0:
            self.results["on_page"]["links"]["issues"].append(f"{len(links_without_text)} links without link text")

        if len(h1_tags) == 0:
            self.results["on_page"]["headings"]["issues"].append("No H1 tag found")
        elif len(h1_tags) > 1:
            self.results["on_page"]["headings"]["issues"].append("Multiple H1 tags found")

        if len(h2_tags) > 15 and self.word_count < 3000:
            self.results["on_page"]["headings"]["issues"].append("Too many H2 tags for content length")

        if len(h3_tags) > 15 and self.word_count < 3000:
            self.results["on_page"]["headings"]["issues"].append("Too many H3 tags for content length")

    def analyze_technical_factors(self):
        """Analyze technical SEO factors"""
        # Check for robots.txt
        has_robots_txt = False
        try:
            robots_url = f"{urlparse(self.url).scheme}://{self.domain}/robots.txt"
            robots_response = requests.get(robots_url, headers=self.headers, timeout=5)
            has_robots_txt = robots_response.status_code == 200
        except:
            pass

        # Check for sitemap.xml
        has_sitemap = False
        try:
            sitemap_url = f"{urlparse(self.url).scheme}://{self.domain}/sitemap.xml"
            sitemap_response = requests.get(sitemap_url, headers=self.headers, timeout=5)
            has_sitemap = sitemap_response.status_code == 200
        except:
            pass

        # Check for canonical tag
        canonical_tag = self.soup.find("link", attrs={"rel": "canonical"})
        has_canonical = canonical_tag is not None
        canonical_url = canonical_tag.get("href") if canonical_tag else ""

        # Check for robots meta tag
        robots_meta = self.soup.find("meta", attrs={"name": "robots"})
        has_robots_meta = robots_meta is not None
        robots_content = robots_meta.get("content") if robots_meta else ""

        # Check HTML5 doctype
        doctype = self.get_doctype()
        has_html5_doctype = "html" in doctype.lower() if doctype else False

        # Check HTTP/2 support
        http2_supported = self.check_http2_support()

        # Check responsive design
        viewport_meta = self.soup.find("meta", attrs={"name": "viewport"})
        has_responsive_design = viewport_meta is not None

        # Check for Open Graph tags
        og_tags = self.soup.find_all("meta", attrs={"property": re.compile("^og:")})
        has_og_tags = len(og_tags) > 0

        # Check for Twitter Card tags
        twitter_tags = self.soup.find_all("meta", attrs={"name": re.compile("^twitter:")})
        has_twitter_cards = len(twitter_tags) > 0

        # Check for schema.org / structured data
        has_structured_data = "application/ld+json" in self.response.text

        # Check for inline CSS/JS
        style_tags = self.soup.find_all("style")
        inline_styles = len(style_tags)

        script_tags = self.soup.find_all("script")
        inline_scripts = len([s for s in script_tags if not s.get("src")])
        external_scripts = len([s for s in script_tags if s.get("src")])

        # Frames check
        frames = self.soup.find_all(["frame", "iframe"])

        # Calculate code to text ratio
        code_size = len(self.response.text.encode('utf-8'))
        text_size = len(self.text_content.encode('utf-8'))
        text_ratio = round((text_size / code_size * 100), 2) if code_size > 0 else 0

        self.results["technical"] = {
            "robots_txt": has_robots_txt,
            "sitemap_xml": has_sitemap,
            "canonical": {
                "present": has_canonical,
                "url": canonical_url
            },
            "robots_meta": {
                "present": has_robots_meta,
                "content": robots_content
            },
            "html5_doctype": has_html5_doctype,
            "http2_support": http2_supported,
            "responsive_design": has_responsive_design,
            "open_graph": has_og_tags,
            "twitter_cards": has_twitter_cards,
            "structured_data": has_structured_data,
            "css_js": {
                "inline_styles": inline_styles,
                "inline_scripts": inline_scripts,
                "external_scripts": external_scripts,
                "issues": []
            },
            "frames": len(frames),
            "code_text_ratio": {
                "code_size": code_size,
                "text_size": text_size,
                "ratio": text_ratio,
                "issues": []
            }
        }

        # Check for issues
        if not has_robots_txt:
            self.results["technical"]["issues"] = self.results["technical"].get("issues", [])
            self.results["technical"]["issues"].append("No robots.txt found")

        if not has_sitemap:
            self.results["technical"]["issues"] = self.results["technical"].get("issues", [])
            self.results["technical"]["issues"].append("No sitemap.xml found")

        if not has_canonical and self.response.url != self.url:
            self.results["technical"]["issues"] = self.results["technical"].get("issues", [])
            self.results["technical"]["issues"].append("No canonical tag found for redirected URL")

        if inline_styles > 0:
            self.results["technical"]["css_js"]["issues"].append(f"Found {inline_styles} inline style tags")

        if inline_scripts > 10:
            self.results["technical"]["css_js"]["issues"].append(f"Too many inline scripts ({inline_scripts})")

        if external_scripts > 15:
            self.results["technical"]["css_js"]["issues"].append(f"Too many external scripts ({external_scripts})")

        if len(frames) > 0:
            self.results["technical"]["issues"] = self.results["technical"].get("issues", [])
            self.results["technical"]["issues"].append(f"Found {len(frames)} frames or iframes")

        if text_ratio < 25:
            self.results["technical"]["code_text_ratio"]["issues"].append("Text rate should be higher than 25%")

    def analyze_semantics(self):
        """Analyze semantic factors including keyword usage and readability"""
        # Get words and calculate frequencies
        words = re.findall(r'\b[a-zA-Z]{3,}\b', self.text_content.lower())
        word_freq = Counter(words)

        # Get top 10 words (excluding common English stopwords)
        stopwords = ['the', 'and', 'are', 'for', 'was', 'not', 'you', 'but', 'his', 'her', 'they', 'she', 'will', 'with', 'from', 'that', 'this', 'have', 'has']
        top_words = [word for word, count in word_freq.most_common(30) if word not in stopwords][:10]

        # Calculate keyword density for top words
        top_words_data = []
        for word in top_words:
            count = word_freq[word]
            density = round((count / len(words) * 100), 2) if len(words) > 0 else 0

            # Find where it appears
            in_title = word in self.soup.title.string.lower() if self.soup.title else False
            in_headings = any(word in h.text.lower() for h in self.soup.find_all(['h1', 'h2', 'h3']))
            in_meta_desc = False
            meta_desc_tag = self.soup.find("meta", attrs={"name": "description"})
            if meta_desc_tag and meta_desc_tag.get("content"):
                in_meta_desc = word in meta_desc_tag.get("content").lower()

            # Visibility score - simple algorithm based on where keyword appears
            visibility = 0
            if in_title:
                visibility += 20
            if in_headings:
                visibility += 15
            if in_meta_desc:
                visibility += 10
            visibility += min(density * 10, 30)  # Weight by density up to 30%

            top_words_data.append({
                "keyword": word,
                "count": count,
                "density": density,
                "in_title": in_title,
                "in_headings": in_headings,
                "in_meta_desc": in_meta_desc,
                "visibility": visibility
            })

        # Calculate readability (basic Flesch Reading Ease)
        word_count = len(re.findall(r'\b\w+\b', self.text_content))
        sentence_count = len(re.findall(r'[.!?]+', self.text_content)) or 1
        avg_words_per_sentence = word_count / sentence_count

        # Very basic approximation of syllables
        syllable_pattern = re.compile(r'[aeiouy]+', re.IGNORECASE)
        syllables = len(syllable_pattern.findall(self.text_content))
        syllables_per_word = syllables / word_count if word_count > 0 else 0

        # Flesch Reading Ease formula: 206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * syllables_per_word)
        flesch_score = max(0, min(100, round(flesch_score)))

        # Interpret readability score
        readability_level = "Unknown"
        if flesch_score >= 90:
            readability_level = "Very Easy"
        elif flesch_score >= 80:
            readability_level = "Easy"
        elif flesch_score >= 70:
            readability_level = "Fairly Easy"
        elif flesch_score >= 60:
            readability_level = "Standard"
        elif flesch_score >= 50:
            readability_level = "Fairly Difficult"
        elif flesch_score >= 30:
            readability_level = "Difficult"
        else:
            readability_level = "Very Difficult"

        self.results["semantics"] = {
            "top_keywords": top_words_data,
            "readability": {
                "flesch_score": flesch_score,
                "level": readability_level,
                "words_per_sentence": round(avg_words_per_sentence, 1),
                "syllables_per_word": round(syllables_per_word, 2)
            }
        }

    def analyze_text_content(self):
        """Analyze text content and phrases"""
        # Get all words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', self.text_content.lower())
        word_freq = Counter(words)

        # Get 2-word phrases
        two_word_phrases = []
        words_list = words
        for i in range(len(words_list) - 1):
            two_word_phrases.append(f"{words_list[i]} {words_list[i+1]}")
        two_word_freq = Counter(two_word_phrases)

        # Get 3-word phrases
        three_word_phrases = []
        for i in range(len(words_list) - 2):
            three_word_phrases.append(f"{words_list[i]} {words_list[i+1]} {words_list[i+2]}")
        three_word_freq = Counter(three_word_phrases)

        # Get semantic tags
        p_tags = self.soup.find_all("p")
        strong_tags = self.soup.find_all("strong")
        em_tags = self.soup.find_all("em")
        ul_tags = self.soup.find_all("ul")
        ol_tags = self.soup.find_all("ol")
        blockquote_tags = self.soup.find_all("blockquote")

        # HTML5 semantic elements
        header_tags = self.soup.find_all("header")
        footer_tags = self.soup.find_all("footer")
        nav_tags = self.soup.find_all("nav")
        article_tags = self.soup.find_all("article")
        section_tags = self.soup.find_all("section")
        aside_tags = self.soup.find_all("aside")

        self.results["content"] = {
            "word_frequencies": {word: count for word, count in word_freq.most_common(30)},
            "two_word_phrases": {phrase: count for phrase, count in two_word_freq.most_common(20)},
            "three_word_phrases": {phrase: count for phrase, count in three_word_freq.most_common(10)},
            "semantic_tags": {
                "p": len(p_tags),
                "strong": len(strong_tags),
                "em": len(em_tags),
                "ul": len(ul_tags),
                "ol": len(ol_tags),
                "blockquote": len(blockquote_tags)
            },
            "html5_elements": {
                "header": len(header_tags),
                "footer": len(footer_tags),
                "nav": len(nav_tags),
                "article": len(article_tags),
                "section": len(section_tags),
                "aside": len(aside_tags)
            }
        }

    def is_internal_link(self, href):
        """Check if a link is internal to the site"""
        if not href or href.startswith('#') or href.startswith('javascript:'):
            return True

        parsed_href = urlparse(href)

        if not parsed_href.netloc:
            return True

        return parsed_href.netloc == self.domain

    def get_doctype(self):
        """Extract doctype from the page"""
        doctype_match = re.search(r'<!DOCTYPE[^>]*>', self.response.text, re.IGNORECASE)
        return doctype_match.group(0) if doctype_match else ""

    def check_http2_support(self):
        """Check if the server supports HTTP/2"""
        try:
            parsed_url = urlparse(self.url)
            host = parsed_url.netloc
            port = 443 if parsed_url.scheme == 'https' else 80

            context = ssl.create_default_context()
            conn = socket.create_connection((host, port), timeout=10)
            if parsed_url.scheme == 'https':
                conn = context.wrap_socket(conn, server_hostname=host)

            return conn.version() == 'h2'
        except:
            return False

def run_seo_analysis(url):
    analyzer = SEOAnalyzer(url)
    results = analyzer.analyze()
    return results

def print_seo_report(results):
    """Print a formatted SEO report"""
    if "error" in results:
        print(f"Error: {results['error']}")
        return

    # Print general info
    print("\n" + "="*50)
    print("SEO ANALYSIS REPORT")
    print("="*50)

    print(f"\nURL: {results['general_info']['url']}")
    print(f"Date: {results['general_info']['date']}")

    # Print on-page factors
    print("\n" + "-"*50)
    print("ON-PAGE SEO FACTORS")
    print("-"*50)

    # Title
    title_info = results['on_page']['title']
    print(f"\nTitle: {title_info['text']}")
    print(f"Length: {title_info['length']} characters, {title_info['word_count']} words")
    if title_info['issues']:
        print("Issues:")
        for issue in title_info['issues']:
            print(f"  - {issue}")

    # Meta Description
    meta_info = results['on_page']['meta_description']
    print(f"\nMeta Description: {meta_info['text']}")
    print(f"Length: {meta_info['length']} characters, {meta_info['word_count']} words")
    if meta_info['issues']:
        print("Issues:")
        for issue in meta_info['issues']:
            print(f"  - {issue}")

    # Text
    text_info = results['on_page']['text']
    print(f"\nText Content: {text_info['word_count']} words")
    if text_info['issues']:
        print("Issues:")
        for issue in text_info['issues']:
            print(f"  - {issue}")

    # Links
    links_info = results['on_page']['links']
    print(f"\nLinks:")
    print(f"  - Internal links: {links_info['internal_count']}")
    print(f"  - External links: {links_info['external_count']}")
    print(f"  - Links without title attribute: {links_info['without_title']}")
    print(f"  - Links without text: {links_info['without_text']}")
    print(f"  - Nofollow links: {links_info['nofollow_count']}")
    if links_info['issues']:
        print("Issues:")
        for issue in links_info['issues']:
            print(f"  - {issue}")

    # Headings
    headings_info = results['on_page']['headings']
    print(f"\nHeadings:")
    print(f"  - H1 tags: {headings_info['h1_count']}")
    print(f"  - H2 tags: {headings_info['h2_count']}")
    print(f"  - H3 tags: {headings_info['h3_count']}")
    print("\nHeading Structure:")
    for heading in headings_info['structure'][:10]:  # Show first 10 headings
        print(f"  - {heading['tag']}: {heading['text'][:50]}...")
    if len(headings_info['structure']) > 10:
        print(f"  - ... and {len(headings_info['structure']) - 10} more")
    if headings_info['issues']:
        print("Issues:")
        for issue in headings_info['issues']:
            print(f"  - {issue}")

    # Technical factors
    print("\n" + "-"*50)
    print("TECHNICAL SEO FACTORS")
    print("-"*50)

    tech_info = results['technical']
    print(f"\nRobots.txt: {'Present' if tech_info['robots_txt'] else 'Not found'}")
    print(f"Sitemap.xml: {'Present' if tech_info['sitemap_xml'] else 'Not found'}")
    print(f"Canonical Tag: {'Present' if tech_info['canonical']['present'] else 'Not found'}")
    if tech_info['canonical']['present']:
        print(f"  - URL: {tech_info['canonical']['url']}")
    print(f"Robots Meta Tag: {'Present' if tech_info['robots_meta']['present'] else 'Not found'}")
    if tech_info['robots_meta']['present']:
        print(f"  - Content: {tech_info['robots_meta']['content']}")
    print(f"HTML5 Doctype: {'Present' if tech_info['html5_doctype'] else 'Not found'}")
    print(f"HTTP/2 Support: {'Supported' if tech_info['http2_support'] else 'Not supported'}")
    print(f"Responsive Design: {'Detected' if tech_info['responsive_design'] else 'Not detected'}")
    print(f"Open Graph Tags: {'Present' if tech_info['open_graph'] else 'Not found'}")
    print(f"Twitter Cards: {'Present' if tech_info['twitter_cards'] else 'Not found'}")
    print(f"Structured Data: {'Detected' if tech_info['structured_data'] else 'Not detected'}")

    print("\nCSS and JavaScript:")
    css_js_info = tech_info['css_js']
    print(f"  - Inline styles: {css_js_info['inline_styles']}")
    print(f"  - Inline scripts: {css_js_info['inline_scripts']}")
    print(f"  - External scripts: {css_js_info['external_scripts']}")
    if css_js_info['issues']:
        print("  Issues:")
        for issue in css_js_info['issues']:
            print(f"    - {issue}")

    print(f"\nFrames/iframes: {tech_info['frames']}")

    print("\nCode to Text Ratio:")
    ratio_info = tech_info['code_text_ratio']
    print(f"  - Code size: {ratio_info['code_size']} bytes")
    print(f"  - Text size: {ratio_info['text_size']} bytes")
    print(f"  - Ratio: {ratio_info['ratio']}%")
    if ratio_info['issues']:
        print("  Issues:")
        for issue in ratio_info['issues']:
            print(f"    - {issue}")

    # Semantics analysis
    print("\n" + "-"*50)
    print("SEMANTIC ANALYSIS")
    print("-"*50)

    semantic_info = results['semantics']

    print("\nTop Keywords:")
    for keyword in semantic_info['top_keywords']:
        print(f"  - {keyword['keyword']}: {keyword['count']} occurrences, {keyword['density']}% density, {keyword['visibility']} visibility score")
        locations = []
        if keyword['in_title']:
            locations.append("Title")
        if keyword['in_headings']:
            locations.append("Headings")
        if keyword['in_meta_desc']:
            locations.append("Meta Description")
        if locations:
            print(f"    Appears in: {', '.join(locations)}")

    print("\nReadability:")
    read_info = semantic_info['readability']
    print(f"  - Flesch Reading Ease Score: {read_info['flesch_score']}")
    print(f"  - Readability Level: {read_info['level']}")
    print(f"  - Average Words Per Sentence: {read_info['words_per_sentence']}")
    print(f"  - Average Syllables Per Word: {read_info['syllables_per_word']}")

    # Content analysis
    print("\n" + "-"*50)
    print("CONTENT ANALYSIS")
    print("-"*50)

    content_info = results['content']

    print("\nWord Frequencies (Top 10):")
    for word, count in list(content_info['word_frequencies'].items())[:10]:
        print(f"  - {word}: {count}")

    print("\nPopular 2-Word Phrases (Top 5):")
    for phrase, count in list(content_info['two_word_phrases'].items())[:5]:
        print(f"  - {phrase}: {count}")

    print("\nPopular 3-Word Phrases (Top 3):")
    for phrase, count in list(content_info['three_word_phrases'].items())[:3]:
        print(f"  - {phrase}: {count}")

    print("\nSemantic HTML Tags:")
    semantic_tags = content_info['semantic_tags']
    print(f"  - Paragraphs (p): {semantic_tags['p']}")
    print(f"  - Strong: {semantic_tags['strong']}")
    print(f"  - Emphasis (em): {semantic_tags['em']}")
    print(f"  - Unordered Lists (ul): {semantic_tags['ul']}")
    print(f"  - Ordered Lists (ol): {semantic_tags['ol']}")
    print(f"  - Blockquotes: {semantic_tags['blockquote']}")

    print("\nHTML5 Semantic Elements:")
    html5_elements = content_info['html5_elements']
    print(f"  - Header: {html5_elements['header']}")
    print(f"  - Footer: {html5_elements['footer']}")
    print(f"  - Nav: {html5_elements['nav']}")
    print(f"  - Article: {html5_elements['article']}")
    print(f"  - Section: {html5_elements['section']}")
    print(f"  - Aside: {html5_elements['aside']}")

    # Performance
    if 'performance' in results:
        print("\n" + "-"*50)
        print("PERFORMANCE")
        print("-"*50)

        perf_info = results['performance']
        print(f"\nPage Load Time: {perf_info['load_time']} seconds")

