import argparse
import sys
from crawler import Crawler
from exporter import Exporter
import logging

def main():
    parser = argparse.ArgumentParser(description="Sitemap Automatic Generation Tool")
    parser.add_argument("url", help="Base URL to start crawling")
    parser.add_argument("--subdomains", nargs="*", help="Additional subdomains allowed to crawl")
    parser.add_argument("--output", default="sitemap", help="Output filename base (without extension)")
    parser.add_argument("--delay-min", type=float, default=1.0, help="Minimum delay between requests")
    parser.add_argument("--delay-max", type=float, default=3.0, help="Maximum delay between requests")
    parser.add_argument("--max-depth", type=int, help="Maximum depth to crawl")
    parser.add_argument("--excel", action="store_true", help="Output as Excel in addition to CSV")
    parser.add_argument("--include-params", action="store_true", help="Include all URL variations with query parameters (default is to skip them)")
    parser.add_argument(
        "--traversal",
        choices=["dfs", "bfs"],
        default="dfs",
        help="Traversal strategy: dfs (depth-first, default) or bfs (breadth-first)",
    )

    args = parser.parse_args()

    crawler = Crawler(
        base_url=args.url,
        allowed_subdomains=args.subdomains,
        delay_range=(args.delay_min, args.delay_max),
        max_depth=args.max_depth,
        unique_path=not args.include_params,
        traversal=args.traversal,
    )

    # 出力ファイル名の決定（指定がない場合はドメイン名を使用）
    output_base = args.output
    if output_base == "sitemap":
        from urllib.parse import urlparse
        domain = urlparse(args.url).netloc
        if domain:
            output_base = domain.replace(":", "_") # ポート等が含まれる場合の対策

    print(f"Starting crawl of {args.url}...")
    try:
        crawler.crawl()
        results = crawler.get_results()
        
        Exporter.export_csv(results, f"{output_base}.csv")
        if args.excel:
            Exporter.export_excel(results, f"{output_base}.xlsx")
            
        print(f"Crawl completed. {len(results)} pages found.")
        
    except KeyboardInterrupt:
        print("\nCrawl interrupted by user. Saving partial results...")
        results = crawler.get_results()
        Exporter.export_csv(results, f"{output_base}_partial.csv")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
