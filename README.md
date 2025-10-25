# 🐵 MOJO the Scraper 😁

<p align="center">
  <img src="https://i.imgur.com/9xZx5Xp.gif" width="300" alt="Mojo Jojo">
</p>

<h1 align="center">🐵 MOJO the Scraper 😁</h1>

<p align="center">
  <i>"The great MOJO cannot be stopped! He will collect ALL THE DATA! Hahaha!"</i><br>
  — <b>Not actually Mojo Jojo... but still!</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.28+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## 🍌 Introducing the Evil Genius Himself

**MOJO the Scraper** is your **banana-powered**, **villainously-simple** web scraping app that turns any web page into tidy, exportable tables.

💻 Built with **Streamlit**, powered by **pandas**, and sprinkled with Mojo Jojo's *mad genius energy*, this tool makes data scraping fun, fast, and slightly evil.

---

## 🎩 Features of MOJO, King of Scraping

| Feature | Description |
|---------|-------------|
| 🐒 **URL to Data** | Paste any website URL and get tabular data as CSV or Excel |
| 😁 **JavaScript Support** | Handles JS pages via Selenium/Playwright like a true mastermind |
| 📚 **Multiple Extractors** | Extract text, links, images, tables—no data is safe! |
| 🔥 **Scheduling** | Schedule recurring scrapes ("Today, Townsville! Tomorrow, the WORLD!") |
| 🚦 **Data Cleanup** | Built-in cleanup removes pesky `\n` and garbage columns |
| 📊 **Analysis Tools** | Data preview, stats, and visualizations for evil planning |

<p align="center">
  <img src="https://media1.tenor.com/m/B3YBZaPjz6gAAAAC/mojo-jojo.gif" width="280" alt="Mojo Jojo Laughing">
</p>

---

## 🛠️ Dependencies

> "Mojo Jojo needs his tools! So too does this scraper!"

Required libraries:

```
streamlit
pandas
beautifulsoup4
requests
openpyxl
lxml
selenium
playwright
apscheduler
plotly
```

### 📦 Install Everything at Once

```bash
pip install streamlit pandas beautifulsoup4 requests openpyxl lxml selenium playwright apscheduler plotly
playwright install chromium
```

---

## ⚡ How to Summon MOJO

After installing dependencies, unleash Mojo with:

```bash
streamlit run mojo.py
```

Then open your browser to:  
**👉 [http://localhost:8501](http://localhost:8501)**

Witness the **glory of MOJO the Scraper** in all his data-hoarding madness!

<p align="center">
  <img src="https://media1.tenor.com/m/v8d0cdF5z2QAAAAC/mojo-jojo.gif" width="250" alt="Mojo Jojo Working">
</p>

---

## 🧠 Tips for Evil Data Scientists (and Would-Be Villains)

- ☠️ **Want ALL the tables?** Use "Auto-detect Tables" — *Mojo approves!*  
- 🧠 **Need JavaScript pages?** Enable "JS Rendering" for advanced mischief  
- 📅 **Scheduling evil deeds?** Automate scrapes in the "Schedule" tab  
- 🎩 **Export All The Things:** CSV, Excel, or JSON — no minions required  
- 🔍 **Custom Selectors:** Use CSS selectors for surgical data extraction  

---

## 📸 Screenshots

### Main Interface
<p align="center">
  <img src="screenshots/main-interface.png" width="600" alt="Main Interface">
  <br><i>The command center for your data conquest!</i>
</p>

### Data Analysis
<p align="center">
  <img src="screenshots/data-analysis.png" width="600" alt="Data Analysis">
  <br><i>Analyze your spoils with charts and metrics!</i>
</p>

---

## 🎯 Quick Start Guide

1. **Clone the repo**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mojo-the-scraper.git
   cd mojo-the-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Run MOJO**
   ```bash
   streamlit run mojo.py
   ```

4. **Start scraping!**
   - Enter a URL (try: `https://en.wikipedia.org/wiki/List_of_countries_by_population`)
   - Choose extraction method
   - Click "Start Scraping"
   - Download your data!

---

## 🤓 Project Structure

```
mojo-the-scraper/
├── mojo.py                 # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file!
├── .gitignore             # Git ignore rules
└── screenshots/           # App screenshots (optional)
```

---

## 🔧 Advanced Features

### Custom CSS Selectors
Extract specific elements using CSS selectors:
```
Selector: div.product-card
Attributes: text, href, class
```

### Scheduled Scraping
Set up recurring scrapes:
- Choose interval (minutes/hours)
- Select export format
- Let MOJO work in the background!

### Data Analysis
Built-in visualization tools:
- Statistical summaries
- Distribution charts
- Missing value analysis
- Data quality scores

---

## ⚖️ Legal & Ethical Disclaimer

> "With great scraping power comes great responsibility!"

- ✅ Always check `robots.txt` before scraping
- ✅ Respect website terms of service
- ✅ Use rate limiting (delays between requests)
- ✅ Don't overload servers
- ❌ Never scrape personal/private data without permission
- ❌ Respect copyright and data ownership

**MOJO the Scraper is for educational and ethical use only!**

---

## 🐛 Troubleshooting

### Issue: Excel export fails
**Solution:** Update the `export_to_excel` method to flatten MultiIndex columns

### Issue: JavaScript pages not loading
**Solution:** Enable "JS Rendering" checkbox and ensure Playwright is installed

### Issue: `\n` in exported data
**Solution:** The `clean_dataframe` method should remove these automatically

### Issue: Port already in use
**Solution:** Run with different port:
```bash
streamlit run mojo.py --server.port 8502
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests
- 📖 Improve documentation

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Streamlit** for the amazing framework
- **pandas** for powerful data manipulation
- **BeautifulSoup** for HTML parsing magic
- **Cartoon Network** for creating Mojo Jojo (we're just fans!)

---

## 😂 Funny Footer

<p align="center">
  <img src="https://media1.tenor.com/m/B3YBZaPjz6gAAAAC/mojo-jojo.gif" width="200" alt="Mojo Jojo Victory">
</p>

<h3 align="center">
  <i>"If MOJO cannot scrape it... it is not worth scraping!"</i><br>
  — Probably Mojo Jojo again, probably
</h3>

---

<h2 align="center">🐵 Enjoy Scraping, You Glorious Villain! 😁</h2>

<p align="center">
  <i>"MOJO! Mojo Jojo says: Go forth and scrape wisely!"</i>
</p>

---

<p align="center">
  Made with 💚 (and a touch of villainy) by aspiring data scientists everywhere
</p>

<p align="center">
  <img src="https://forthebadge.com/images/badges/built-with-love.svg" alt="Built with Love">
  <img src="https://forthebadge.com/images/badges/powered-by-coffee.svg" alt="Powered by Coffee">
</p>
