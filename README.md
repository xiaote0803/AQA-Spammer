# AQA Spammer

A Python tool to spam [AQA.link](https://aqa.link/) messages with proxies

## Support

Join our Discord server for support and updates: [Discord Link](https://discord.gg/R7ybdvBSuM)

## Features

- Concurrent multi-threading
- Rate-limit bypass
- Proxy-based requests
- Dynamic device ID
- Rotating User-Agent

## Installation

```bash
pip install requests urllib3
```

## Usage

```bash
python main.py
```

## Configuration

- **`message.txt`**: Each line contains one message to send
- **`proxy.txt`**: Each line contains a proxy in `ip:port` format
- **`toUserId`**: You need send a request yourself and check its headers to find the toUserId. Enter it when the script asks.

## Proxy Collection

You can use [Proxy-Scraper-And-Checker](https://github.com/xiaote0803/Proxy-Scraper-and-Checker) to fetch proxies for `proxy.txt`

## Disclaimer

This project is for educational purposes only. Use at your own risk. Users are responsible for complying with all applicable laws and terms of service.

