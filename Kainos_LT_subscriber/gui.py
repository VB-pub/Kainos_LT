from scraper import Scraper
import tkinter as tk

def click_category_button(cat):
    scraper.category_click(cat)
    update_buttons()

def update_buttons():
    for widget in button_frame.winfo_children():
        widget.destroy()

    for category in scraper.categories:
        button = tk.Button(button_frame, text=category.text, 
                           command=lambda cat=category: click_category_button(cat))
        button.pack()

def on_search_click():
    global filters
    
    q = search_entry.get()
    scraper.item_search(q)
    filters = scraper.categories_load()
    
    update_buttons()

root = tk.Tk()
scraper = Scraper()
scraper.load_page()
scraper.cookie_trust_handle()

screen_width = root.winfo_screenwidth() // 2
screen_height = root.winfo_screenheight() - (root.winfo_screenheight() // 8)
root.geometry(f"{screen_width}x{screen_height}")
root.title("Kainos_LT")

search_entry = tk.Entry(root, width=(screen_width // 8))
search_entry.pack()

search_button = tk.Button(root, text="Prekių paieška", command=on_search_click)
search_button.pack()

button_frame = tk.Frame(root)
button_frame.pack()

root.mainloop()