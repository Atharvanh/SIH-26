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
        
        print("Navigating to Create Lot page...")
        await page.goto("http://localhost:5173/farmer/create-lot")
        
        print("Clicking Find Best Buyers...")
        await page.wait_for_selector("button[type='submit']")
        await page.click("button[type='submit']")
        
        print("Waiting for results and clicking Accept on #1 buyer...")
        await page.wait_for_selector(".buyer-card--top .accept-btn", state="visible", timeout=15000)
        
        # Add a tiny delay for animation
        await page.wait_for_timeout(1000)
        
        await page.click(".buyer-card--top .accept-btn")
        
        print("Waiting for Order Status page...")
        await page.wait_for_selector(".order-status-page", state="visible", timeout=10000)
        
        # We are at REQUESTED. Advance twice to get to IN_TRANSIT.
        print("Advancing stage 1 (to SCHEDULED)...")
        await page.wait_for_selector(".advance-btn", state="visible")
        await page.click(".advance-btn")
        await page.wait_for_timeout(1500) # wait for refresh
        
        print("Advancing stage 2 (to IN_TRANSIT)...")
        await page.click(".advance-btn")
        await page.wait_for_timeout(1500) # wait for refresh
        
        # Take screenshot of mid-flow
        await page.screenshot(path=r"C:\Users\ADMIN\.gemini\antigravity\brain\84b366ea-0ba6-4c1c-87c6-abc34f50134e\order_in_transit.png", full_page=True)
        print("Screenshot 1 saved (In Transit).")
        
        # Raise dispute
        print("Raising dispute...")
        await page.click("button.btn-secondary:has-text('Raise a Dispute')")
        await page.wait_for_selector(".dispute-form", state="visible")
        await page.fill(".dispute-form textarea", "The truck arrived 6 hours late, causing partial spoilage.")
        await page.click(".dispute-form-actions .btn-danger")
        
        print("Waiting for dispute to register...")
        await page.wait_for_selector(".active-dispute", state="visible", timeout=10000)
        await page.wait_for_timeout(1000)
        
        # Take screenshot of dispute raised state
        await page.screenshot(path=r"C:\Users\ADMIN\.gemini\antigravity\brain\84b366ea-0ba6-4c1c-87c6-abc34f50134e\order_dispute.png", full_page=True)
        print("Screenshot 2 saved (Dispute Raised).")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_e2e())
