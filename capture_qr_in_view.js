const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    console.log('Loading mdviewer with Dropbox documentation...');
    await page.goto('https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/mdviewer/index.html?file=DROPBOX_SHARING_STRATEGY.md');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // First, let's find where the QR code section is
    const qrPosition = await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h3'));
        const qrHeading = headings.find(h => h.textContent.includes('QR Code'));
        if (qrHeading) {
            const rect = qrHeading.getBoundingClientRect();
            // Scroll to put the QR heading near the top
            window.scrollTo(0, window.scrollY + rect.top - 100);
            return { found: true, top: rect.top };
        }
        return { found: false };
    });
    
    console.log('QR section found:', qrPosition);
    await page.waitForTimeout(1500);
    
    // Take screenshot showing the QR code section
    await page.screenshot({ 
        path: '/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston/screenshots/dashboard_qr_in_view.png',
        fullPage: false
    });
    
    console.log('✅ Screenshot with QR code saved!');
    
    // Verify the QR image is visible
    const qrImageVisible = await page.evaluate(() => {
        const img = document.querySelector('img[src*="dropbox_folder_qr"]');
        if (img) {
            const rect = img.getBoundingClientRect();
            return {
                visible: rect.top >= 0 && rect.top < window.innerHeight,
                top: rect.top,
                loaded: img.complete && img.naturalHeight > 0
            };
        }
        return { visible: false };
    });
    
    console.log('QR image visibility:', qrImageVisible);
    
    await browser.close();
})();
