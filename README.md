# Python_FrequencyAnalysis

**A simple script to prove Zipf's law.**

## Usage

### Step 1: Setup

Clone this repository and create two directories inside the `src` folder called `books` and `temp` respectively.

### Step 2: Download

This will download books in plain text format (will automatically strip headers) from Project Gutenberg.

```python
python Downloader.py
```

Specify the number of passes (1 pass is around 20-50 books).

Press a key at anytime to exit (NOTE: Program will only exit once current pass is complete).

The files will be downloaded to the `temp` directory.

*Requires BeautifulSoup.*

#### Options

You may edit the offset for Project Gutenberg in the `Downloader_Config.ini` (This value is auto updated).

### Step 3: Analyze

This will generate a set of confidence intervals.

```python
python Analyze_Multicore.py
```

Make sure specified books are in the `books` directory.

Output will be saved to `conf.txt`.

#### Options

```python
'''
Number of books to sample for one confidence interval.
Make sure value is lower than number of books in the directory.
'''
NUM_OF_SAMPLES = 300

'''
Number of words to include in the data set for generating the regression line.
Set to -1 to use all words (not recommended), 1000 works best.
'''
NUM_TOP_WORDS = 1000

'''
Number of confidence intervals to generate.
'''
NUM_INTERVALS = 100

'''
Number of processes.
'''
NUM_PROCESSES = 8

'''
Alpha value for confidence interval.
0.05 = 95% confidence
'''
ALPHA_VALUE = 0.05
```

*Requires statsmodels.api, numpy, matplotlib.*