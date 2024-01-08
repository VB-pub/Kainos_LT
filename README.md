# Kainos_LT
Paketas skirtas duomenų gavybai iš kainos.lt tinklalapio.

### Reikalavimai sistemai:
- Python 3.10 +
- Selenium

### Diegimas:

```
pip install selenium
```
```
pip install kainos_lt_scraper
```

### Naudojimas (command-line):
- `kainos_lt_scraper.main`
##### Argumentai:
- `--time_limit (default: 120)`
- `--thread_count (default: 2)`
- `--max_thread_count (default: 5)`

##### Pavyzdžiai:
- Inicijuojamas darbas 20 sekundžių su 2 gijomis ir gijų maksimumu 5:
  
![image](https://github.com/VB-pub/Kainos_LT/assets/60397005/9e3c061d-8428-40d4-b0df-98c353ce3dae)
```
python -m kainos_lt_scraper.main --time_limit 20
```

- Vyksta darbas:
  
![image](https://github.com/VB-pub/Kainos_LT/assets/60397005/1cc9392b-bc7b-4a3c-85c5-afd6bb023c26)

- Darbas baigiamas. Sutvarkomi naudoti resursai:
  
![image](https://github.com/VB-pub/Kainos_LT/assets/60397005/95e7c618-cc68-4603-baa9-30ef7fe73349)

- Rezultatas pasiekiamas `<python_dir>\site-packages\kainos_lt_scraper\data.json`

# Licenzija
MIT
