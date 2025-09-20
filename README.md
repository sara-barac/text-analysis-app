# 📊 Text Analysis App

Ovaj projekat je deo ispitnog zadatka na predmetu Programiranje za lingviste na masterskom programu 
Računarstvo u društvenim naukama na Univerzitetu u Beogradu. 

📊 Text Analysis App: CLI aplikacija koja iz .xlsx fajlova određene* strukture: 
1) ekstrahuje tekstove
2) dodeljuje im odgovarajuće naslove
3) vrši analizu tih tekstova korištenjem **SpaCy** biblioteke 


- ✅ Token and POS analysis per topic  
- ✅ Type-Token Ratio (TTR)  
- ✅ Named Entity Recognition (NER)  
- ✅ Text similarity matrix between topics

*relevantni deo izgleda .xlsx fajlova u kome je sadržan tekst
![.xlsx fajl](C:\Users\PC\OneDrive\Desktop\materijali za README\izgled_xslx_fajla) 
---

## ⚡ Quick Start

```bash
# Clone the repository  
git clone https://github.com/YOUR-USERNAME/text-analysis-app.git
cd text-analysis-app

# Create and activate a virtual environment
python -m venv .venv
# Windows PowerShell
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run the CLI
textan 

