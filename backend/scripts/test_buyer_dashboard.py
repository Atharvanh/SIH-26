import asyncio
from playwright.async_api import async_playwright

async def run_e2e():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()
        
        print("Navigating to Buyer Dashboard page...")
        await page.goto("http://localhost:5173/buyer/dashboard")
        
        print("Waiting for offers to load...")
        # wait for either the offer card or the empty state
        await page.wait_for_selector(".offer-card, .empty-state", state="visible", timeout=10000)
        
        # Take screenshot of buyer dashboard
        await page.screenshot(path=r"C:\Users\ADMIN\.gemini\antigravity\brain\84b366ea-0ba6-4c1c-87c6-abc34f50134e\buyer_dashboard.png", full_page=True)
        print("Screenshot saved (Buyer Dashboard).")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_e2e())
