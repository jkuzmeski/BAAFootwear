from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, render_template_string, request
from threading import Thread
import pandas as pd
import time
import os


path = "/Users/joshcohen/Downloads/chromedriver-mac-arm64/chromedriver"
service = Service(executable_path=path)

# Add options to make Chrome more stable
options = Options()
options.add_argument("--no-sandbox")  # Bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

driver = webdriver.Chrome(service=service, options=options)

app = Flask(__name__)

@app.route('/')
def index():
    bib = request.args.get('bib')
    name = request.args.get('name')
    shoes = Shoes
    runners_left = request.args.get('runners_left')
    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Select Shoe</title>
            <style>
                body {
                    background-color: #121212;
                    color: #e0e0e0;
                    font-family: Arial, sans-serif;
                }
                h1 {
                    text-align: center;
                    margin-top: 20px;
                }
                .shoe-container {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                }
                .shoe-image {
                    display: inline-block;
                    margin: 10px;
                    padding: 20px;
                    border: 1px solid #444;
                    border-radius: 10px;
                    cursor: pointer;
                    text-align: center;
                    background-color: #1e1e1e;
                    transition: transform 0.2s;
                }
                .shoe-image:hover {
                    transform: scale(1.05);
                }
                .shoe-image img {
                    max-width: 400px;
                    max-height: 400px;
                }
                .shoe-image p {
                    margin-top: 10px;
                    font-size: 1.1em;
                }
                form {
                    display: none;
                }
                .counter {
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 1.2em;
                }
            </style>
        </head>
        <body>
            <h1>Select Shoe for {{ name }} (Bib: {{ bib }})</h1>
            <div class="counter">
                Runners left: {{ runners_left }}
            </div>
            <div class="shoe-container">
                {% for shoe in shoes %}
                    <div class="shoe-image" onclick="selectShoe('{{ shoe }}')">
                        <img src="{{ url_for('static', filename=shoe_images[shoe]) }}" alt="{{ shoe }}">
                        <p>{{ shoe }}</p>
                    </div>
                {% endfor %}
            </div>
            <form id="shoeForm" method="post" action="/submit">
                <input type="hidden" name="bib" value="{{ bib }}">
                <input type="hidden" name="name" value="{{ name }}">
                <input type="hidden" name="shoe_choice" id="shoe_choice">
            </form>
            <script>
                function selectShoe(shoe) {
                    document.getElementById('shoe_choice').value = shoe;
                    document.getElementById('shoeForm').submit();
                }
            </script>
        </body>
        </html>
    ''', bib=bib, name=name, shoes=shoes, shoe_images=shoe_images, runners_left=runners_left)

@app.route('/submit', methods=['POST'])
def submit():
    bib = request.form['bib']
    name = request.form['name']
    shoe_choice = request.form['shoe_choice']
    save_shoe_choice(bib, name, shoe_choice)
    global user_has_selected_shoe
    user_has_selected_shoe = True
    return '''
        <script>
            window.close();
        </script>
        Shoe choice submitted successfully!
    '''

def save_shoe_choice(bib, name, shoe_choice):
    with open('/Users/joshcohen/Documents/BAAFootwear/data/Raw/ShoeChoices.csv', 'a') as f:
        f.write(f"{bib},{name},{shoe_choice}\n")

def show_shoe_selection_page(driver, bib, name, runners_left):
    url = f"http://127.0.0.1:5000/?bib={bib}&name={name}&runners_left={runners_left}"
    driver.get(url)

def getMarathonFoto(Bib, LastName, Url):
    # Store the original window handle
    original_window = driver.current_window_handle
    
    driver.get(Url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "search[start_no]"))
    )

    driver.find_element(By.NAME, "search[start_no]").send_keys(Bib + Keys.ENTER)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, LastName))
    )

    driver.find_element(By.PARTIAL_LINK_TEXT, value=LastName).click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Marathonfoto.com"))
    )

    driver.find_element(By.PARTIAL_LINK_TEXT, "Marathonfoto.com").click()
    
    return original_window

def close_other_tabs(driver, original_window):
    # Wait for the new tab to open and switch to it
    time.sleep(2)  # Give time for new tabs to open
    
    # Get all window handles
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            # Switch to the tab and close it
            driver.switch_to.window(window_handle)
            driver.close()
    
    # Switch back to the original tab
    driver.switch_to.window(original_window)

RaceTimeSeconds = pd.read_csv('/Users/joshcohen/Documents/BAAFootwear/data/Raw/RaceTimeSeconds.csv', encoding='latin1')

def get_processed_bibs():
    shoe_choices_path = '/Users/joshcohen/Documents/BAAFootwear/data/Raw/ShoeChoices.csv'
    if not os.path.exists(shoe_choices_path):
        return set()
    
    try:
        processed = pd.read_csv(shoe_choices_path, header=None, names=['bib', 'name', 'shoe'], encoding='latin1')
        return set(processed['bib'].astype(str))
    except pd.errors.EmptyDataError:
        return set()

#create a def that get all of the runners under a certain time
def getRunnersUnderTime(timeSeconds):
    # Get all runners under the time limit
    runners = RaceTimeSeconds[RaceTimeSeconds['Finish Net'] < timeSeconds].reset_index(drop=True)
    
    # Filter out already processed runners
    processed_bibs = get_processed_bibs()
    unprocessed_runners = runners[~runners['bib'].astype(str).isin(processed_bibs)].reset_index(drop=True)
    
    return unprocessed_runners

Runners = getRunnersUnderTime(10800)
names = Runners['name']
names = names.str.split(',')
names = names.str[0]
bib = Runners['bib']

Shoes = [
    'Adidas Adizero Adios Pro 3',
    'Adidas Adizero Adios Pro 2',  
    'Adidas Adizero Adios Pro Evo 1',
    'Nike Air Zoom Alphafly 3 Next%',
    'Nike Zoom X Alphafly 2 Next%',
    'Nike Zoom X Vaporfly Next%', 
    'Nike Zoom X Vaporfly Next% 2',
    'Nike Zoom X Vaporfly 3', 
    'Asics Metaspeed Edge Paris',
    'Puma Deviate Elite 3', 
    'Puma FastR Nitro' ,
    'Saucony Endorphin Pro 2',
    'Hoka One One Rocket X',
    'Brooks Hyperion Elite 4',
    'On Cloudboom Strike LS',
    'New Balance FuelCell RC Elite', 
    'Under Armour Flow Velociti Elite 2',
    'Xtep 160X 5.0',
    'Li-Ning Fei X 5.0',
    'Question Mark',
    
]

shoe_images = {
    'Adidas Adizero Adios Pro 3': 'adidas_adizero_adios_pro_3.jpg',
    'Adidas Adizero Adios Pro 2': 'adidas_adizero_adios_pro_2.jpg',
    'Adidas Adizero Adios Pro Evo 1': 'adidas_adizero_adios_pro_evo_1.jpg',
    'Nike Air Zoom Alphafly 3 Next%': 'nike_air_zoom_alphafly_next.jpg',
    'Nike Zoom X Alphafly 2 Next%': 'nike_alphafly_2.jpg',
    'Nike Zoom X Vaporfly Next%': 'nike_zoom_x_vaporfly_next.jpg',
    'Nike Zoom X Vaporfly Next% 2': 'nike_zoom_x_vaporfly_next_2.jpg',
    'Nike Zoom X Vaporfly 3': 'nike_zoom_x_vaporfly_3.jpg',
    'Asics Metaspeed Edge Paris': 'asics_metaspeed_edge_paris.jpg',
    'Brooks Hyperion Elite 4': 'brooks_hyperion_elite_4.jpg',
    'Hoka One One Rocket X': 'hoka_one_one_rocket_x.jpg',
    'New Balance FuelCell RC Elite': 'new_balance_fuelcell_rc_elite.jpg',
    'On Cloudboom Strike LS': 'on_cloudboom_strike_ls.jpg',
    'Saucony Endorphin Pro 2': 'saucony_endorphin_pro_2.jpg',
    'Xtep 160X 5.0': 'xtep_160x_5.0.jpg',
    'Puma Deviate Elite 3': 'puma_deviate_elite_3.jpg',
    'Puma FastR Nitro': 'puma_fastr_nitro.jpg',
    'Li-Ning Fei X 5.0': 'li-ning.jpg',
    'Under Armour Flow Velociti Elite 2': 'under_armour_velociti.jpg',
    'Question Mark': 'question_mark.jpg'
}
    
if __name__ == '__main__':
    # Run the Flask app in a separate thread
    flask_thread = Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False})
    flask_thread.start()
    
    # Open a new browser tab once
    selection_driver = webdriver.Chrome(service=service, options=options)
    # for each runner, get their marathonfoto
    for i in range(len(names)):
        user_has_selected_shoe = False
        runners_left = len(names) - i
        show_shoe_selection_page(selection_driver, bib[i], names[i], runners_left)
        original_window = getMarathonFoto(bib[i], names[i], "https://results.baa.org/2024/")
        
        while not user_has_selected_shoe:
            time.sleep(1)
        
        # Close any additional tabs that were opened
        close_other_tabs(driver, original_window)
    
    # Close the browser tab after all selections are done
    selection_driver.quit()
    driver.quit()




