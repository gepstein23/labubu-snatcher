# 🧸 Pop-Now Box Watcher (Selenium) — `main.py`

A tiny automation buddy that keeps an eye on a Pop-Now set page, flips through boxes, and pounces the moment it spots an “unlocked” container — then tries to click **ADD TO BAG**. 🛒✨

> **Important / Read This First (please):**  
> This script **eventually resulted in a ban** after running for a period of time (likely due to automation detection / unusual traffic patterns). Also, the Popmart website/app changes often, so this script **may no longer be compatible** with the current UI, class names, flows, or anti-bot protections.

---

## 🎯 What it does

- Opens a Pop-Now “set” page for a given **set ID**
- Accepts the privacy policy pop-up if it appears
- Scans the visible container images for a “special” `src` that indicates an unlocked container:
  - Looks for `"box_pic_with_shadow"` in the image URL  
- If it finds one:
  - Scrolls it into view
  - Clicks it
  - Waits for a redirect
  - Clicks **ADD TO BAG**
  - (One-time) opens a celebratory song in YouTube 🎶
- If it doesn’t find one:
  - Prints the current box number
  - Clicks the “Next Box” arrow
  - Repeats forever (until it can’t continue)

---

## 🧩 Files

- `main.py` — the whole script lives here.

---

## ✅ Requirements

- Python 3.9+ (recommended)
- Google Chrome installed
- A Chrome profile directory you can point Selenium at (for cookies/session persistence)
- Python packages:
  - `selenium`
  - `webdriver-manager`

Install dependencies:

```bash
pip install selenium webdriver-manager
```
## 🔐 About login (and a small gotcha)

The CLI requires:

- `--email`
- `--password`

…but the current script **does not actually use these values** to type into login fields. Instead, it relies on your provided Chrome profile (`--user-data-dir`) to already be logged in (or to handle login manually when Chrome opens).

✅ Best practice: log in once in that Chrome profile, then keep reusing the same profile folder.

---

## 🚀 Usage

Run from the directory containing `main.py`:

```bash
python main.py \
  --email "you@example.com" \
  --password "your_password" \
  --user-data-dir "/path/to/your/chrome/user/data" \
  --set-id "123456"
```
### Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--email` | ✅ | Login email (**currently not used** in automation steps) |
| `--password` | ✅ | Login password (**currently not used** in automation steps) |
| `--user-data-dir` | ✅ | Path to Chrome user data directory (keeps cookies/session) |
| `--set-id` | ✅ | The Pop-Now **Set ID** (from the URL) |

---

## 🛠 How “unlocked” detection works

The script grabs all visible container image elements:

- CSS selector: `[class^='index_showBoxItem__']`

Then treats a container as “unlocked” if its image `src` contains:

- `box_pic_with_shadow`

If Popmart changes their DOM, hashed class names, or image naming/CDN paths, you’ll need to update:
- the selector used to find containers
- the condition used to detect “unlocked” containers

---

## 🔁 How the loop behaves

On each cycle:

1. Waits for the box containers to load
2. Scans every container image for an “unlocked” match
3. If found:
   - scrolls + clicks
   - waits for URL to change
   - clicks **ADD TO BAG**
   - returns to the set page and keeps searching
4. If not found:
   - prints the current box number (if available)
   - clicks the visible “Next Box” arrow
   - repeats

The loop stops if:
- containers never load
- the “Next Box” arrow can’t be found/clicked
- the page structure changes and selectors no longer match

---

## ⚠️ Limitations, risks, and compatibility notes

- **Ban risk (real):** This script **did** lead to an account ban after running for some amount of time. Use at your own risk.
- **Likely to break:** The script depends on CSS class names like:
  - `index_showBoxItem__...`
  - `index_boxNumber__...`
  - `index_nextImg__...`
  These are often hashed/auto-generated and can change without warning.
- **Email/password not wired in:** Credentials are accepted via CLI but not used in the browser flow.
- **Endless loop:** This runs continuously until something fails (or you stop it).
- **Popmart changes fast:** It may be **no longer compatible** with the current Popmart web/app experience.

---

## 🧯 Troubleshooting

- **It opens Chrome but isn’t logged in**
  - Make sure `--user-data-dir` points to a Chrome profile where you’ve already logged into Popmart.
  - (Tip) Close all other Chrome windows using that profile before running the script.

- **It can’t find containers / next arrow**
  - Popmart likely changed class names or DOM structure.
  - Update the selectors in `main.py` to match the current site.

- **“ADD TO BAG” never clicks**
  - The button text may differ, or it may be disabled/hidden behind a modal.
  - Update the XPath:
    - `//button[contains(text(), 'ADD TO BAG')]`

- **It clicks but doesn’t redirect**
  - The click target may no longer be the correct element.
  - Try selecting a parent element or using a different locator strategy.

---

## 🏁 Exiting

When the script stops, it will print:

```text
🚪 Exiting script.
Press Enter to close...
