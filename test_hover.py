#!/usr/bin/env python3
"""
Headless Chrome test for hover functionality
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def test_hover_functionality():
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🚀 Starting headless Chrome test...")
        
        # Navigate to the app (replace with your Railway URL)
        url = "https://mood-tracker-production-6fa4.up.railway.app/"
        print(f"📍 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check if we need to login (look for login elements)
        try:
            login_element = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
            print("🔐 Login required - this test needs authentication")
            return
        except:
            print("✅ No login required or already authenticated")
        
        # Look for the daily chart canvas
        print("🔍 Looking for daily chart canvas...")
        try:
            canvas = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "dailyChart"))
            )
            print("✅ Found daily chart canvas")
            
            # Get canvas properties
            canvas_rect = canvas.rect
            print(f"📏 Canvas dimensions: {canvas_rect['width']}x{canvas_rect['height']}")
            print(f"📍 Canvas position: ({canvas_rect['x']}, {canvas_rect['y']})")
            
            # Check if canvas is visible
            is_displayed = canvas.is_displayed()
            print(f"👁️  Canvas visible: {is_displayed}")
            
            # Get computed styles
            pointer_events = driver.execute_script("return window.getComputedStyle(arguments[0]).pointerEvents;", canvas)
            z_index = driver.execute_script("return window.getComputedStyle(arguments[0]).zIndex;", canvas)
            print(f"🖱️  Pointer events: {pointer_events}")
            print(f"📚 Z-index: {z_index}")
            
        except Exception as e:
            print(f"❌ Canvas not found: {e}")
            return
        
        # Check console logs
        print("📝 Checking console logs...")
        logs = driver.get_log('browser')
        for log in logs:
            if log['level'] in ['SEVERE', 'WARNING']:
                print(f"⚠️  Console {log['level']}: {log['message']}")
        
        # Try to hover over the canvas center
        print("🖱️  Testing hover on canvas center...")
        actions = ActionChains(driver)
        actions.move_to_element(canvas).perform()
        
        # Wait a moment for any hover effects
        time.sleep(2)
        
        # Check for new console logs after hover
        print("📝 Checking console logs after hover...")
        new_logs = driver.get_log('browser')
        hover_logs = [log for log in new_logs if log not in logs]
        
        if hover_logs:
            for log in hover_logs:
                print(f"🎯 Hover log: {log['message']}")
        else:
            print("❌ No hover-related console logs detected")
        
        # Check if debugging functions exist
        print("🔧 Checking if debugging code is loaded...")
        canvas_debug = driver.execute_script("""
            const canvas = document.getElementById('dailyChart');
            if (!canvas) return 'Canvas not found';
            
            // Check if our debugging code ran
            const hasEventListeners = canvas.onclick !== null || canvas.onmousemove !== null;
            
            return {
                canvasExists: !!canvas,
                hasEventListeners: hasEventListeners,
                chartExists: !!window.dailyChart,
                moodPoints: window.dailyChart ? window.dailyChart.moodPoints : null
            };
        """)
        
        print(f"🔍 Debug info: {canvas_debug}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        driver.quit()
        print("🏁 Test completed")

if __name__ == "__main__":
    test_hover_functionality()
