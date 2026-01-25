import { chromium } from 'playwright';

const BASE_URL = 'http://localhost:5174';

async function testClarificationFlow() {
  console.log('Starting Playwright test for clarification flow...\n');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Step 1: Go to home page
    console.log('1. Navigating to home page...');
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    console.log('   OK - Home page loaded\n');

    // Step 2: Create a new session
    console.log('2. Creating new session...');
    const startButton = page.locator('button:has-text("Start New Project")');
    await startButton.waitFor({ state: 'visible', timeout: 5000 });
    await startButton.click();
    await page.waitForURL(/\/session\/.*\/idea/);
    console.log('   OK - Session created, on idea page\n');

    // Step 3: Submit project idea
    console.log('3. Submitting project idea...');
    const ideaTextarea = page.locator('textarea');
    await ideaTextarea.fill('A mobile app for tracking daily water intake with smart reminders and health insights');
    const submitIdeaButton = page.locator('button:has-text("Continue")');
    await submitIdeaButton.click();
    await page.waitForURL(/\/configure/);
    console.log('   OK - Idea submitted, on configure page\n');

    // Step 4: Configure session (use defaults)
    console.log('4. Configuring session...');
    const startDebateButton = page.locator('button:has-text("Start")');
    await startDebateButton.waitFor({ state: 'visible', timeout: 5000 });
    await startDebateButton.click();
    await page.waitForURL(/\/questions/);
    console.log('   OK - Configuration done, on questions page\n');

    // Step 5: Wait for clarification questions to load
    console.log('5. Waiting for clarification questions...');
    await page.waitForSelector('h3:has-text("Q1:")', { timeout: 60000 });
    console.log('   OK - Questions loaded\n');

    // Step 6: Verify multiple choice options are displayed
    console.log('6. Verifying multiple choice options...');
    const radioButtons = page.locator('input[type="radio"]');
    const radioCount = await radioButtons.count();
    console.log(`   Found ${radioCount} radio buttons`);

    if (radioCount < 4) {
      throw new Error('Expected at least 4 radio buttons for multiple choice options');
    }
    console.log('   OK - Multiple choice options displayed\n');

    // Step 7: Verify "Type your own answer" option exists
    console.log('7. Checking for "Type your own answer" option...');
    const customOption = page.locator('text=Type your own answer');
    const customCount = await customOption.count();
    console.log(`   Found ${customCount} "Type your own answer" options`);

    if (customCount === 0) {
      throw new Error('Expected "Type your own answer" option');
    }
    console.log('   OK - Custom answer option available\n');

    // Step 8: Select answers for each question
    console.log('8. Selecting answers...');
    const questions = page.locator('.card:has(h3:has-text("Q"))');
    const questionCount = await questions.count();
    console.log(`   Found ${questionCount} questions`);

    for (let i = 0; i < questionCount; i++) {
      const question = questions.nth(i);
      // Select the first option (A) for each question
      const firstOption = question.locator('input[type="radio"]').first();
      await firstOption.click();
      console.log(`   Selected option for Q${i + 1}`);
    }
    console.log('   OK - All questions answered\n');

    // Step 9: Verify submit button is enabled
    console.log('9. Checking submit button state...');
    const submitButton = page.locator('button:has-text("Submit Answers")');
    const isDisabled = await submitButton.isDisabled();

    if (isDisabled) {
      throw new Error('Submit button should be enabled after answering all questions');
    }
    console.log('   OK - Submit button is enabled\n');

    // Step 10: Submit answers
    console.log('10. Submitting answers...');
    await submitButton.click();

    // Wait for either next round of questions or completion
    console.log('    Waiting for response...');
    await page.waitForSelector('h3:has-text("Q1:"), text=Clarification Complete', { timeout: 60000 });

    const isComplete = await page.locator('text=Clarification Complete').count() > 0;
    if (isComplete) {
      console.log('    OK - Clarification marked as complete\n');
    } else {
      console.log('    OK - Next round of questions received\n');

      // Verify it's round 2
      const roundText = await page.locator('text=Round').textContent();
      console.log(`    Current: ${roundText}`);
    }

    // Step 11: Test custom answer option
    console.log('11. Testing custom answer option...');
    if (!isComplete) {
      const firstQuestion = questions.first();
      const customRadio = firstQuestion.locator('input[type="radio"][value="custom"]');
      await customRadio.click();

      // Check that textarea appears
      const textarea = firstQuestion.locator('textarea');
      await textarea.waitFor({ state: 'visible', timeout: 3000 });
      await textarea.fill('This is my custom answer for testing');
      console.log('    OK - Custom answer textarea works\n');
    }

    console.log('='.repeat(50));
    console.log('ALL TESTS PASSED!');
    console.log('='.repeat(50));

  } catch (error) {
    console.error('\nTEST FAILED:', error.message);

    // Take screenshot on failure
    await page.screenshot({ path: '/tmp/test-failure.png' });
    console.log('Screenshot saved to /tmp/test-failure.png');

    process.exit(1);
  } finally {
    await browser.close();
  }
}

testClarificationFlow();
