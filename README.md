# ReadSiteUpdates

**ReadSiteUpdates** is a lightweight Python script that monitors websites and sends email notifications whenever they are updated.

## Installation

Install the required Python packages using [pip](https://pypi.org/project/pip/):

```bash
pip install -r requirements.txt
```

## Usage

### Create a parser file

Create a parser file in [`src/parsers.py`](src/parsers.py) with this structure:

```python
from bs4 import BeautifulSoup

def parse_html_example(html):
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    results = []

    for item in soup.select("div"):  # Generic selector
        try:
            title_tag = item.find("h1")
            link_tag = item.find("a", href=True)
            results.append({
                "title": title_tag.get_text(strip=True) if title_tag else "",
                "link": link_tag["href"] if link_tag else ""
            })
        except Exception as e:
            print(f"Error parsing item: {e}")
            continue

    return results

urls_and_parsers = [
    ("https://example.com", parse_html_example, "div")
]
```

Where:

- `"https://example.com"` — the URL to monitor.
- `parse_html_example` — the parsing function.
- `"div"` — the element that signals the page is fully loaded.

### Configure your environment

Create a [`.env`](.env) file based on [`.env.example`](.env.example) and add a:

- Receiver email
- Sender email
- Sender email password

> [!TIP]  
> You can add multiple emails by separating emails with commas (,) **without a space**

### Compiling

1. **Install Nuitka**

```bash
python -m pip install -U Nuitka
```

2. **Compile the script**

    - **On Windows:**

    ```bash
    python -m nuitka --onefile --windows-console-mode=disable --enable-plugin=tk-inter --output-dir=dist ./src/main.py
    ```

    - **On other OSes (macOS/Linux):**

   ```bash
    python -m nuitka --onefile --enable-plugin=tk-inter --output-dir=dist ./src/main.py
    ```

You can change those settings if needed.

### Scheduling

> [!WARNING]  
> By default, and by recommendation, compile the script (see [Compiling](#compiling)) and move it to another folder to schedule. To skip this, change `script_to_execute` in [`settings.ini`](settings.ini)

#### Initializing

- **Windows**

> Run [`scripts/init.bat`](scripts/init.bat) to schedule the script in **Windows Task Scheduler**.

- **Other OSes (macOS/Linux)**

> Change `script_to_execute` in [`settings.ini`](settings.ini) and run [`scripts/init.sh`](scripts/init.sh) to schedule the script in **cron**.

You can adjust `start_time` and `interval` in [`settings.ini`](settings.ini).

> [!IMPORTANT]  
> Changes require rerunning the init script to take effect.

#### Removing

- **Windows**

> Run [`scripts/remove.bat`](scripts/remove.bat) to remove the scheduled task.

- **Other OSes (macOS/Linux)**

> Run [`scripts/remove.sh`](scripts/remove.sh) to remove the scheduled task.

You can also run [`src/main.py`](src/main.py) (or the compiled executable) manually to test changes.

## Usage Example


### CSV Output

Filename: `results_https_www_example_com.csv`

| id | name     | price | stock |
|----|---------|-------|-------|
| 1  | Widget A | 19.99 | 25    |
| 2  | Widget B | 24.50 | 10    |
| 4  | Widget D | 29.99 | 15    |

---

### Email Output

> [!NOTE]
> In the actual email, this content is formatted and rendered (e.g., colored +s and -s, better spacing, headings for sections).

URL: https://example.com/

`+`
- **id**: 4
- **name**: Widget D
- **price**: 29.99
- **stock**: 15

`-`
- **id**: 3
- **name**: Widget C
- **price**: 12.00
- **stock**: 0

\----

URL: https://example.net/

`+`
- **id**: 101
- **title**: Item X
- **status**: Available

## Customization

You can change how the program works by editing the [`settings.ini`](settings.ini) file.

### Scheduler

- `start_time` — when the script should run every interval (format: `HH:MM` in 24-hour format, default: `09:00`).
- `interval` — how often to check for updates (format: `[number][unit]`, default: every 24 hours).
- `script_to_execute` — file for the scheduler to run (default: `main.exe`).

### Prompts

- `enable_error_prompts` — shows error messages if `true` (default: `true`).
- `enable_info_prompts` — shows informational prompts if `true` (default: `false`).

### Sites

- `disabled_sites` — list of URLs to skip monitoring (format: `[URL, URL, URL]`, default: empty)

### Email

- `direction` — text direction for email content (`ltr` = left-to-right, `rtl` = right-to-left, default: `ltr`).

## Licensing

This project is licensed under the [MIT license](LICENSE).
