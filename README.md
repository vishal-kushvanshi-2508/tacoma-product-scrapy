# Tacoma Product Scraper Using Scrapy

## 📖 Overview

This project is a Python-based web scraping solution developed using Scrapy to extract product information from the Tacoma website. The scraper collects structured product data efficiently and exports it for further analysis and processing.

The project demonstrates practical experience in web scraping, data extraction, XPath parsing, and scalable Scrapy development.

---

## 🚀 Features

* Product data extraction
* Scrapy spider implementation
* Automated data collection
* Structured JSON output
* XPath-based extraction
* Error handling and logging
* Scalable scraping workflow

---

## 🛠️ Technologies Used

* Python
* Scrapy
* XPath
* JSON
* Logging

---

## 📊 Extracted Data

* Product Name
* Product URL
* Product Category
* Product Description
* Product Specifications
* Product Images
* Additional Product Details

---

## 📁 Project Structure

```text
tacoma-product-scrapy/
│
├── scrapy.cfg
├── requirements.txt
├── README.md
│
└── tacoma_product/
    │
    ├── __init__.py
    ├── items.py
    ├── pipelines.py
    ├── settings.py
    │
    └── spiders/
        │
        ├── __init__.py
        └── tacoma_product.py
```

---

## ⚡ Installation

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Spider

```bash
scrapy crawl tacoma_product
```

---

## 📂 Export Output

```bash
scrapy crawl tacoma_product -o products.json
```

---

## 🎯 Learning Outcomes

* Scrapy Framework
* XPath Data Extraction
* Product Data Collection
* JSON Data Processing
* Spider Development
* Error Handling and Logging
* Clean Project Architecture

---

### 🔗 GitHub Profiles

💼 Professional Work:
https://github.com/vishal-kushvanshi-2508

📚 Practice Projects & Learning:
https://github.com/vishal-2508
