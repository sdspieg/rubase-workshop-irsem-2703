const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function verifyLLMGuide() {
    console.log('Starting LLM Selection Guide verification...');

    // Launch browser
    const browser = await chromium.launch({
        headless: false,  // Show browser for debugging
        slowMo: 1000     // Slow down for visibility
    });

    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });

    const page = await context.newPage();

    try {
        console.log('Navigating to GitHub Pages site...');
        await page.goto('https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/llm-selection-guide.html');

        // Wait for page to load
        await page.waitForTimeout(3000);

        console.log('Page loaded. Looking for slides...');

        // Function to navigate to a specific slide
        async function navigateToSlide(slideNumber) {
            console.log(`Navigating to slide ${slideNumber}...`);

            // Try different methods to navigate to slides
            // Method 1: Check for slide navigation buttons
            const nextButton = page.locator('button:has-text("Next"), .navigate-right, [data-nav="next"]').first();
            const prevButton = page.locator('button:has-text("Previous"), .navigate-left, [data-nav="prev"]').first();

            // Method 2: Check for reveal.js navigation
            const revealNext = page.locator('.navigate-right').first();
            const revealPrev = page.locator('.navigate-left').first();

            // Method 3: Try keyboard navigation
            // First, go to slide 1
            await page.keyboard.press('Home');
            await page.waitForTimeout(1000);

            // Then navigate to the target slide
            for (let i = 1; i < slideNumber; i++) {
                await page.keyboard.press('ArrowRight');
                await page.waitForTimeout(500);
            }
        }

        // Function to extract text content from current slide
        async function extractSlideContent() {
            await page.waitForTimeout(1000);

            // Try multiple selectors for slide content
            const selectors = [
                '.reveal .slides section.present',
                '.slides .present',
                '.slide.current',
                '.slide.active',
                'section[aria-hidden="false"]'
            ];

            for (const selector of selectors) {
                try {
                    const element = page.locator(selector);
                    if (await element.count() > 0) {
                        const text = await element.textContent();
                        console.log(`Found content using selector: ${selector}`);
                        return text;
                    }
                } catch (e) {
                    continue;
                }
            }

            // Fallback: get all visible text
            const bodyText = await page.textContent('body');
            return bodyText;
        }

        // Function to take screenshot
        async function takeScreenshot(slideNumber, description) {
            const filename = `slide_${slideNumber}_${description.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase()}.png`;
            const filepath = path.join(process.cwd(), filename);

            await page.screenshot({
                path: filepath,
                fullPage: false  // Just the viewport
            });

            console.log(`Screenshot saved: ${filename}`);
            return filename;
        }

        // Results object to store findings
        const results = {
            slide4: { screenshot: null, content: '', hasArena: false },
            slide5: { screenshot: null, content: '', tier1Text: '', hasNewModels: [], hasMissingOldModels: [] },
            slide6: { screenshot: null, content: '', hasRecommendations: false },
            modelsFound: {
                newModels: {
                    'GPT-5.4': false,
                    'Claude Opus 4.6': false,
                    'Gemini 3.1 Pro': false
                },
                oldModelsRemoved: {
                    'Claude 3.5 Sonnet': true, // should be removed (true = successfully removed)
                    'GPT-4o': true,
                    'Gemini 1.5 Pro': true
                }
            }
        };

        // Check Slide 4 (LMSYS Arena Rankings)
        console.log('\\n=== CHECKING SLIDE 4 ===');
        await navigateToSlide(4);
        results.slide4.content = await extractSlideContent();
        results.slide4.screenshot = await takeScreenshot(4, 'lmsys_arena_rankings');
        results.slide4.hasArena = results.slide4.content.toLowerCase().includes('arena') ||
                                 results.slide4.content.toLowerCase().includes('lmsys');

        // Check Slide 5 (Current Model Landscape)
        console.log('\\n=== CHECKING SLIDE 5 ===');
        await navigateToSlide(5);
        results.slide5.content = await extractSlideContent();
        results.slide5.screenshot = await takeScreenshot(5, 'current_model_landscape');

        // Extract Tier 1 section specifically
        const tier1Match = results.slide5.content.match(/Tier 1[^\\n]*([\\s\\S]*?)(?=Tier 2|$)/i);
        if (tier1Match) {
            results.slide5.tier1Text = tier1Match[0].trim();
        }

        // Check for new models
        const newModels = ['GPT-5.4', 'Claude Opus 4.6', 'Gemini 3.1 Pro'];
        newModels.forEach(model => {
            if (results.slide5.content.includes(model)) {
                results.modelsFound.newModels[model] = true;
                results.slide5.hasNewModels.push(model);
            }
        });

        // Check for old models that should be removed
        const oldModels = ['Claude 3.5 Sonnet', 'GPT-4o', 'Gemini 1.5 Pro'];
        oldModels.forEach(model => {
            if (results.slide5.content.includes(model)) {
                results.modelsFound.oldModelsRemoved[model] = false; // Still present
                results.slide5.hasMissingOldModels.push(model);
            }
        });

        // Check Slide 6 (Task-Specific Recommendations)
        console.log('\\n=== CHECKING SLIDE 6 ===');
        await navigateToSlide(6);
        results.slide6.content = await extractSlideContent();
        results.slide6.screenshot = await takeScreenshot(6, 'task_specific_recommendations');
        results.slide6.hasRecommendations = results.slide6.content.toLowerCase().includes('recommendation') ||
                                           results.slide6.content.toLowerCase().includes('task');

        // Also check slide 6 for model mentions
        newModels.forEach(model => {
            if (results.slide6.content.includes(model) && !results.modelsFound.newModels[model]) {
                results.modelsFound.newModels[model] = true;
                console.log(`Found ${model} in slide 6`);
            }
        });

        // Generate report
        console.log('\\n\\n=== VERIFICATION REPORT ===');
        console.log('\\nSlide 4 (LMSYS Arena Rankings):');
        console.log(`- Screenshot: ${results.slide4.screenshot}`);
        console.log(`- Contains Arena content: ${results.slide4.hasArena}`);
        console.log(`- Content preview: ${results.slide4.content.substring(0, 200)}...`);

        console.log('\\nSlide 5 (Current Model Landscape):');
        console.log(`- Screenshot: ${results.slide5.screenshot}`);
        console.log(`- Tier 1 Text: "${results.slide5.tier1Text}"`);
        console.log(`- New models found: ${results.slide5.hasNewModels.join(', ') || 'None'}`);
        console.log(`- Old models still present: ${results.slide5.hasMissingOldModels.join(', ') || 'None'}`);

        console.log('\\nSlide 6 (Task-Specific Recommendations):');
        console.log(`- Screenshot: ${results.slide6.screenshot}`);
        console.log(`- Contains recommendation content: ${results.slide6.hasRecommendations}`);
        console.log(`- Content preview: ${results.slide6.content.substring(0, 200)}...`);

        console.log('\\nModel Verification Summary:');
        console.log('New models (should be present):');
        Object.entries(results.modelsFound.newModels).forEach(([model, found]) => {
            console.log(`  - ${model}: ${found ? 'FOUND ✓' : 'MISSING ✗'}`);
        });

        console.log('Old models (should be removed):');
        Object.entries(results.modelsFound.oldModelsRemoved).forEach(([model, removed]) => {
            console.log(`  - ${model}: ${removed ? 'REMOVED ✓' : 'STILL PRESENT ✗'}`);
        });

        // Save detailed report to file
        const reportData = {
            timestamp: new Date().toISOString(),
            url: 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/llm-selection-guide.html',
            results: results
        };

        fs.writeFileSync('verification_report.json', JSON.stringify(reportData, null, 2));
        console.log('\\nDetailed report saved to: verification_report.json');

        return results;

    } catch (error) {
        console.error('Error during verification:', error);
        throw error;
    } finally {
        await browser.close();
    }
}

// Run the verification
verifyLLMGuide().catch(console.error);