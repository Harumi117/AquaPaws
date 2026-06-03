#!/usr/bin/env python3
import sys
from agent import run_pipeline


def main():
    if len(sys.argv) < 2:
        print("使い方: python main.py <商品ページURL>")
        print("例:     python main.py https://item.rakuten.co.jp/shop/item123/")
        sys.exit(1)

    url = sys.argv[1]
    run_pipeline(url)


if __name__ == "__main__":
    main()
