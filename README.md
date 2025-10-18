# ReadSiteUpdates

**ReadSiteUpdates** is a lightweight Python script that monitors websites and sends email notifications whenever they are updated.

## Installation

Install the required Python packages using [pip](https://pypi.org/project/pip/):

```bash
pip install -r requirements.txt
```

## Usage

1. **Create a parser file ([`src/parsers.py`](src/parsers.py))**

Your parser functions should follow this structure:

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
                "link": full_link
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

- `"https://example.com"` is the URL the code fetches.
- `parse_html_example` is the parsing function.
- And `"div"` is the element that signals the page is fully loaded.

2. **Configure your environment**

Create a [`.env`](.env) file based on [`.env.example`](.env.example) and add a:

- Receiver email
- Sender email
- Sender email password

> [!TIP]  
> You can add multiple emails by separating emails with commas (,) **without a space**.

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
> By default, and it’s also better to compile the script (see [Compiling](#compiling)) and move it to another folder to schedule. To skip this, change `script_to_execute` in [`settings.ini`](settings.ini).

- Run [`scripts/init.bat`](scripts/init.bat) to schedule the script in the **Windows Task Scheduler** in the [`scripts/`](scripts/) folder.
- You can adjust `start_time` and `interval` in [`settings.ini`](settings.ini).
> [!IMPORTANT]  
> Changes require rerunning the init script to take effect.
- Run [`scripts/remove.bat`](scripts/remove.bat) to remove the scheduled task in the [`scripts/`](scripts/) folder.
- You can also run [`src/main.py`](src/main.py) (or the file you get after compiling) manually to test changes explicitly.

> Non-Windows scheduling is under development.

## Customization

You can change how the program works by changing the [`settings.ini`](settings.ini) file.

## Licensing

This project is licensed under the [MIT license](LICENSE).
