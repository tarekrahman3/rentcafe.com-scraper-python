import time
import random
import subprocess
import re
import sys
import json
import traceback
from datetime import datetime
import pyautogui
import cv2
import numpy as np
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def focus_on_chrome_window():
    # Use xdotool to search for the Chrome window name ending with " - Google Chrome"
    command = 'xdotool search --name ".* - Google Chrome$"'
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Extract the window ID from the output
    window_id = stdout.strip().decode()
    command = f'xdotool windowfocus {window_id}'
    subprocess.run(command, shell=True)
    # if window_id:
    #     # Use xdotool to check if the window is visible
    #     command = f'xdotool getwindowgeometry --shell {window_id}'
    #     process = subprocess.Popen(
    #         command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     stdout, stderr = process.communicate()

    #     # Extract the window visibility from the output
    #     visibility = stdout.strip().decode()
    #     visibility = dict(item.split('=') for item in visibility.split('\n'))

    #     if visibility['MAP_STATE'] == 'IsViewable':
    #         # The window is already visible, so just focus on it
    #         command = f'xdotool windowfocus {window_id}'
    #         subprocess.run(command, shell=True)
    #         print("Focused on Chrome browser window")
    #     else:
    #         # The window is not visible, so bring it to the front
    #         command = f'xdotool windowactivate {window_id}'
    #         subprocess.run(command, shell=True)
    #         print("Chrome browser window brought to the front")
    # else:
    #     print("Chrome browser window not found")


def find_image_on_screen(img_path):
    template = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    template_height, template_width = template.shape[:2]
    init = datetime.now()
    while True:
        try:
            screenshot = pyautogui.screenshot()
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            result = cv2.matchTemplate(
                screenshot, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            locations = np.where(result >= threshold)
            center_coordinates = []
            for point in zip(*locations[::-1]):
                center_x = point[0] + template_width // 2
                center_y = point[1] + template_height // 2
                center_coordinates.append((center_x, center_y))
            return center_coordinates[0]
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            if (datetime.now()-init).seconds > 20:
                print('input_box not found')
                raise Exception


def interpolate(start, end, steps):
    # Calculate the increment for each step
    dx = (end[0] - start[0]) / steps
    dy = (end[1] - start[1]) / steps
    # Generate intermediate points
    points = [(start[0] + i * dx, start[1] + i * dy) for i in range(steps)]
    return points


def simulate_random_mouse_movement():
    # Generate random coordinates for mouse movement
    start_x = random.randint(0, 800)
    start_y = random.randint(0, 600)
    end_x = random.randint(0, 800)
    end_y = random.randint(0, 600)
    # Calculate intermediate points
    steps = 50  # Adjust the number of steps for smoother or faster movement
    points = interpolate((start_x, start_y), (end_x, end_y), steps)
    # Simulate mouse movement using xdotool
    for point in points:
        subprocess.call(['xdotool', 'mousemove', str(
            int(point[0])), str(int(point[1]))])
        # Adjust the sleep time for smoother or faster movement
        time.sleep(0.01)
    # Generate random delay between 1 and 5 seconds
    delay = random.uniform(1, 5)
    time.sleep(delay)


def is_cloudflare_page(driver):
    print('Checking if Cloudflare page...')
    page_title = driver.title
    if page_title == "Just a moment...":
        return True
    return False


def is_rentcafe_page(driver):
    page_title = driver.title
    if page_title == 'RentCafe - RentCafe':
        return True
    return False


def passCloudflareCheck(driver):
    while not is_rentcafe_page(driver):
        if is_cloudflare_page(driver):
            print('Handling Cloudflare browser check...')
            time.sleep(2)
            try:
                # try:
                #     focus_on_chrome_window()
                # except:
                #     print('error occured while focusing on chrome window')
                # try:
                #     WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type=checkbox]')))
                # except:
                #     print('verify box not loaded after 25 sec')
                #     driver.save_screenshot('/app/screenshot.png')
                #     driver.maximize_window()
                #     driver.refresh()
                #     continue
                try:
                    x, y = find_image_on_screen('input_box.png')
                except:
                    s = str(driver.page_source)
                    with open ("c.html",'w', encoding='utf-8') as f:
                        f.write(s)
                    x, y = find_image_on_screen('input_box2.png')
                if x != None:
                    simulate_random_mouse_movement()
                    current_mouse_pos = pyautogui.position()
                    points = interpolate(
                        (current_mouse_pos.x, x), (current_mouse_pos.y, y), 50)
                    for point in points:
                        subprocess.call(['xdotool', 'mousemove', str(
                            int(point[0])), str(int(point[1]))])
                        # Adjust the sleep time for smoother or faster movement
                        time.sleep(0.01)
                    delay = random.uniform(3, 5)
                    time.sleep(delay)
                    subprocess.call(['xdotool', 'click', str(1)])
                    delay = random.uniform(3, 5)
                    time.sleep(delay)
                    return
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                driver.refresh()


def read_file(file_path):
    lines = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                lines.append(line.strip())
    except FileNotFoundError:
        print("File not found.")
    return lines


def create_json_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


if __name__ == "__main__":
    try:
        file_path = sys.argv[1]
    except IndexError:
        file_path = 'atlanta-property-links-may-20.txt'
    try:
        export_file_name = sys.argv[2]
    except IndexError:
        export_file_name = f'export {int(time.time())}.json'

    input_links = read_file(file_path)[:5]
    print('Input Links:', input_links)
    links = []
    try:
        chrome_options = uc.ChromeOptions()
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--enable-gpu")
        driver = uc.Chrome(options=chrome_options)
    except Exception as e:
        print('failed to start browser')
        print("error:", str(e))
        print(traceback.format_exc())
        exit()
    print('Browser started successfully')

    for i, input_link in enumerate(input_links):
        print('visiting', i, input_link)
        driver.get(input_link)
        time.sleep(6)
        print("page title:", driver.title)
        
        passCloudflareCheck(driver)

        elements = driver.find_elements(
            By.XPATH, '//button[starts-with(@onclick,"location.href =")]')
        for element in elements:
            value = element.get_attribute('onclick').replace(
                "location.href = '", '').replace("'", "")
            print(len(links), value)
            links.append(
                'https://www.rentcafe.com/onlineleasing/apartmentsforrent/' + value)
    create_json_file(links, export_file_name)
    print(links)
    driver.quit()