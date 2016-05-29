# Python_FrequencyAnalysis

**A simple script to prove Zipf's law.**

## Usage

## Step 1: Download

This will download books in plain text format (will automatically strip headers) from Project Gutenberg.

```python
python Downloader.py
```

Specify the number of passes (1 pass is around 20-50 books).
Press a key at anytime to exit (NOTE: Program will only exit once current pass is complete).

The files will be downloaded to the `temp` directory.

Requires BeautifulSoup.