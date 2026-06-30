import requests
from bs4 import BeautifulSoup
import time
import random
from collections import deque
from urllib.parse import urljoin, urlparse
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(
        self,
        base_url,
        allowed_subdomains=None,
        delay_range=(1.0, 3.0),
        max_depth=None,
        unique_path=True,
        traversal="dfs",
        user_agent="SitemapGenerator/1.0 (+https://github.com/koguchimasataka/extreme-super-site-mapper-final-edition)",
    ):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.allowed_domains = {self.domain}
        if allowed_subdomains:
            for sub in allowed_subdomains:
                self.allowed_domains.add(sub)

        self.delay_range = delay_range
        self.max_depth = max_depth
        self.unique_path = unique_path
        self.traversal = traversal
        self.headers = {'User-Agent': user_agent}

        self.visited_urls = set()
        self.visited_paths = set()
        self.results = []

    def is_valid_url(self, url):
        if not self._is_allowed_url(url):
            return False

        if self.unique_path:
            path_only = self._path_only(url)
            if path_only in self.visited_paths:
                return False
        elif url in self.visited_urls:
            return False

        return True

    def _is_allowed_url(self, url):
        parsed = urlparse(url)
        if parsed.netloc not in self.allowed_domains:
            return False
        if parsed.scheme not in ('http', 'https'):
            return False
        return True

    def _path_only(self, url):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def _reserve_url(self, url):
        if not self.is_valid_url(url):
            return False

        self.visited_urls.add(url)
        self.visited_paths.add(self._path_only(url))
        return True

    def _normalize_url(self, base_url, href):
        next_url = urljoin(base_url, href)
        return next_url.split('#')[0]

    def _extract_links(self, soup, base_url):
        links = []
        for link in soup.find_all('a', href=True):
            next_url = self._normalize_url(base_url, link['href'])
            if self._is_allowed_url(next_url):
                links.append(next_url)
        return links

    def _process_url(self, url, depth):
        logger.info(f"Crawling: {url} (Depth: {depth})")

        time.sleep(random.uniform(*self.delay_range))

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            status_code = response.status_code
            response.encoding = response.apparent_encoding

            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.info(f"Skipping non-HTML content: {url} ({content_type})")
                self.results.append({
                    'url': url,
                    'title': 'Non-HTML Content',
                    'status': status_code,
                    'depth': depth
                })
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'No Title'

            self.results.append({
                'url': url,
                'title': title,
                'status': status_code,
                'depth': depth
            })
            return soup

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            self.results.append({
                'url': url,
                'title': f'Error: {type(e).__name__}',
                'status': 'Error',
                'depth': depth
            })
            return None

    def crawl(self):
        if self.traversal == "bfs":
            self._crawl_bfs()
        else:
            self._crawl_dfs(self.base_url, 0)

    def _crawl_dfs(self, url, depth):
        if self.max_depth is not None and depth > self.max_depth:
            return

        if not self._reserve_url(url):
            return

        soup = self._process_url(url, depth)
        if soup is None:
            return

        for next_url in self._extract_links(soup, url):
            self._crawl_dfs(next_url, depth + 1)

    def _crawl_bfs(self):
        queue = deque()

        if self._reserve_url(self.base_url):
            queue.append((self.base_url, 0))

        while queue:
            url, depth = queue.popleft()

            if self.max_depth is not None and depth > self.max_depth:
                continue

            soup = self._process_url(url, depth)
            if soup is None:
                continue

            child_depth = depth + 1
            if self.max_depth is not None and child_depth > self.max_depth:
                continue

            for next_url in self._extract_links(soup, url):
                if self._reserve_url(next_url):
                    queue.append((next_url, child_depth))

    def get_results(self):
        return self.results
