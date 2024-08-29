import asyncio
import random
import time
from playwright.async_api import async_playwright, expect
from playwright_stealth import stealth_async, StealthConfig
from tiktok_captcha_solver import AsyncPlaywrightSolver
import json
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

executed_tasks = 0
passed_the_test_accounts = []

async def setup_browser_context(playwright, proxy_dict):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    ]

    user_agent = random.choice(user_agents)
    print(f'USER-AGENT selected: {user_agent}')

    browser = await playwright.firefox.launch(
        headless=False,
        slow_mo=750,  # Adding a slight delay to mimic human interaction
        proxy={
            "server": f"http://{proxy_dict['proxyaddr']}:{proxy_dict['proxyport']}",
            "username": proxy_dict['proxylogin'],
            "password": proxy_dict['proxypswd']
        },
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            # '--disable-blink-features=AutomationControlled',
            # '--start-maximized',
            '--disable-extensions',
            '--disable-infobars',
            # '--lang=en-US,en;q=0.9',
            '--disable-backgrounding-occluded-windows',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--ignore-certificate-errors',
            '--disable-popup-blocking',
            '--disable-notifications',
            '--disable-browser-side-navigation',
            # '--disable-features=IsolateOrigins,site-per-process',
        ]
    )

    context = await browser.new_context(
        locale='en-US',
        user_agent=user_agent,
        no_viewport=True,  # Set to your desired window size
        ignore_https_errors=True,  # Ignore certificate errors
    )

    # Adding experimental features similar to Selenium's options
    await context.add_init_script("""
        delete window.__proto__.webdriver;
    """)

    # Disable `navigator.webdriver` (mimic undetectable-chromedriver behavior)
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    return browser, context


async def press_like_tiktok_logic(playwright, passed_tuple):
    intervals = [1000, 1500, 2250, 4000, 7000, 999]
    logger.info('Starting press_like_tiktok_logic')
    account, proxy, username, post_link, likes, acc_data, prox_data = passed_tuple
    account_dict = acc_data[f'{account}']
    proxy_dict = prox_data[f"{proxy['id']}"]

    api_key = "be6caebf30ef75cfac9b3fc0da976136"

    browser, context = await setup_browser_context(playwright, proxy_dict)
    page = await context.new_page()
    config = StealthConfig(navigator_languages=False, navigator_vendor=False, navigator_user_agent=False)
    await stealth_async(page, config)

    try:
        sadcaptcha = AsyncPlaywrightSolver(page, api_key)

        logger.info("Attempting to visit whatismyip.com to verify proxy...")
        await page.goto("https://2ip.io/")  # 30 seconds timeout
        time.sleep(2)





        logger.info("Waiting for 10 seconds before proceeding to TikTok...")
        await page.wait_for_timeout(2000)  # 10 seconds wait

        logger.info("Navigating to TikTok login page...")
        await page.goto("https://www.tiktok.com/login")
        logger.info("TikTok website opened successfully.")
        await page.wait_for_timeout(500)

        logger.info("waiting for the useemailbtn to to_be_visible")
        # for interval in intervals:
        #     if interval == 999:
        #         raise Exception("Max retries have been achieved. ending the exec.")
        #     try:
        #         use_phone_email_button = page.get_by_text("username")
        #         await expect(use_phone_email_button).to_be_visible(timeout=3000)
        #         logger.info("dozhdalsya, clickau")
        #         await use_phone_email_button.hover().click()
        #         time.sleep(100)
        #         await expect(page.locator('a')).to_have_text("Log in with email or username")
        #         break
        #     except Exception as e:
        #         print('error with proceding on the tiktok page - retrying..')
        #         await page.wait_for_timeout(interval)
        await page.get_by_text("username").click()
        logger.info("clicknul")
        await page.get_by_role("link", name="Log in with email or username").click()
        await page.get_by_placeholder("Email or username").click()
        await page.get_by_placeholder("Email or username").fill(account_dict['ttlogin'])
        await page.get_by_placeholder("Password").click()
        await page.get_by_placeholder("Password").fill(account_dict['ttpswd'])
        await page.get_by_role("button", name="Log in").click()
        locator_verify = page.get_by_text("Verify it\'s really you")
        locator_tryagainlater = page.get_by_text("Try again later")
        logger.info('151')
        try:
            await expect(locator_verify).not_to_be_visible()
            logger.info('154')
            await expect(locator_tryagainlater).not_to_be_visible()
            logger.info('156')
        except Exception as e:
            logger.error('Pered CAPTCHA UVY VERIFY')
            logger.info(f"kod oshibki verify: {e}")
            logger.info(f">>>NIESTETY MAMY VERIFY ITS YOU... accid: {account}")
            await browser.close()
        await sadcaptcha.solve_captcha_if_present(retries=3, captcha_detect_timeout=4)
        await page.wait_for_timeout(2015)
        try:
            await expect(locator_verify).not_to_be_visible()
            await expect(locator_tryagainlater).not_to_be_visible()
        except Exception as e:
            logger.error('Pered CAPTCHA UVY VERIFY')
            logger.info(f"kod oshibki verify: {e}")
            logger.info(f">>>NIESTETY MAMY VERIFY ITS YOU... accid: {account}")
            await browser.close()
        logger.info('Going to the post link')
        await page.goto(post_link)
        logger.info('succeeded going to the post link')
        await page.wait_for_timeout(730)
        logger.info(f"GOTOWO: acc. no: {account}")
        passed_the_test_accounts.append(account)

         # this is a temp solution, since i haven't tested the sadcaptcha on playwright


    except Exception as e:
        logger.error(f"An error occurred during proxy check or TikTok navigation: {str(e)}")
        raise

    finally:
        await browser.close()


async def run_tasks(list_to_pass_exec, max_concurrent_browsers=1):
    semaphore = asyncio.Semaphore(max_concurrent_browsers)

    async with async_playwright() as playwright:
        await asyncio.gather(
            *[limited_press_like_tiktok_logic(playwright, tuple_to_pass, semaphore) for tuple_to_pass in
              list_to_pass_exec]
        )


async def limited_press_like_tiktok_logic(playwright, passed_tuple, semaphore):
    async with semaphore:
        try:
            await press_like_tiktok_logic(playwright, passed_tuple)
        except Exception as e:
            logger.error(f"Task failed for {passed_tuple[0]}: {str(e)}")


def main(accounts, proxies, username, post_link, likes):
    with open('accounts_cache.json', 'r', encoding='utf-8') as file:
        acc_data = json.load(file)
    with open('proxies_cache.json', 'r', encoding='utf-8') as file:
        prox_data = json.load(file)

    global executed_tasks
    executed_tasks = 0

    list_to_pass_exec = [
        (accounts[i], proxies[i], username, post_link, likes, acc_data, prox_data)
        for i in range(len(accounts))
    ]

    logger.info(f'Prepared data for execution: {list_to_pass_exec}')

    asyncio.run(run_tasks(list_to_pass_exec))

    logger.info(f'All tasks completed. Total executed tasks: {executed_tasks}')
    logger.info(f'Accs that passed the test: {passed_the_test_accounts}')
    with open('passedtestaccs.json', 'w', encoding='utf-8') as file:
        json.dump(passed_the_test_accounts, file)
