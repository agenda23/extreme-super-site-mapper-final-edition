import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self, base_url, allowed_subdomains=None, delay_range=(1.0, 3.0), max_depth=None, unique_path=True, user_agent="SitemapGenerator/1.0 (+https://github.com/koguchimasataka/extreme-super-site-mapper-final-edition)"):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.allowed_domains = {self.domain}
        if allowed_subdomains:
            for sub in allowed_subdomains:
                self.allowed_domains.add(sub)
        
        self.delay_range = delay_range
        self.max_depth = max_depth
        self.unique_path = unique_path
        self.headers = {'User-Agent': user_agent}
        
        self.visited_urls = set()
        self.visited_paths = set()
        self.results = []

    def is_valid_url(self, url):
        parsed = urlparse(url)
        # ドメインチェック
        if parsed.netloc not in self.allowed_domains:
            return False
        # プロトコルチェック
        if parsed.scheme not in ('http', 'https'):
            return False
        
        # クエリパラメータを無視した一意パスのチェック
        if self.unique_path:
            path_only = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if path_only in self.visited_paths:
                return False
        else:
            # 完全一致での重複チェック
            if url in self.visited_urls:
                return False
        
        return True

    def crawl(self, url=None, depth=0):
        if url is None:
            url = self.base_url
        
        if self.max_depth is not None and depth > self.max_depth:
            return

        if not self.is_valid_url(url):
            return

        logger.info(f"Crawling: {url} (Depth: {depth})")
        self.visited_urls.add(url)
        
        # パスを記録
        parsed = urlparse(url)
        path_only = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        self.visited_paths.add(path_only)
        
        # 負荷対策の待機
        time.sleep(random.uniform(*self.delay_range))

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            status_code = response.status_code
            
            # 文字コードの自動判別
            response.encoding = response.apparent_encoding
            
            # Content-Typeのチェック (HTMLのみ対象)
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.info(f"Skipping non-HTML content: {url} ({content_type})")
                self.results.append({
                    'url': url,
                    'title': 'Non-HTML Content',
                    'status': status_code,
                    'depth': depth
                })
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'No Title'
            
            self.results.append({
                'url': url,
                'title': title,
                'status': status_code,
                'depth': depth
            })

            # リンクの抽出と再帰的クロール
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                # フラグメントの除去
                next_url = next_url.split('#')[0]
                if self.is_valid_url(next_url):
                    self.crawl(next_url, depth + 1)

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            self.results.append({
                'url': url,
                'title': f'Error: {type(e).__name__}',
                'status': 'Error',
                'depth': depth
            })

    def get_results(self):
        return self.results
