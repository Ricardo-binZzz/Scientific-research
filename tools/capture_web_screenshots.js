#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

function loadPlaywright() {
  try {
    return require("playwright");
  } catch (error) {
    console.error("Cannot load playwright. Install it with `npm install --save-dev playwright` or set NODE_PATH to a directory that contains playwright.");
    console.error(error.message);
    process.exit(1);
  }
}

const { chromium } = loadPlaywright();

const repoRoot = path.resolve(__dirname, "..");
const outputDir = path.join(repoRoot, "docs", "screenshots");
const demoProjectRoot = path.join(repoRoot, "examples", "demo-project");
const pythonExecutable = process.env.PYTHON || "python";

function waitForServerUrl(server) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error("Timed out waiting for workflow.web_app to print its URL.")), 15000);
    server.stdout.on("data", (chunk) => {
      const text = chunk.toString("utf8");
      const match = text.match(/Open\s+(http:\/\/127\.0\.0\.1:\d+)/);
      if (match) {
        clearTimeout(timeout);
        resolve(match[1]);
      }
    });
    server.stderr.on("data", (chunk) => process.stderr.write(chunk));
    server.on("exit", (code) => {
      clearTimeout(timeout);
      reject(new Error(`workflow.web_app exited before startup, code ${code}.`));
    });
  });
}

async function waitForAction(page) {
  await page.waitForFunction(() => {
    const output = document.querySelector("#output");
    const panel = document.querySelector("#insightPanel");
    return output && !output.textContent.includes("运行中") && panel && panel.hidden === false;
  }, null, { timeout: 15000 });
}

async function capture(page, fileName) {
  const target = path.join(outputDir, fileName);
  await page.screenshot({ path: target, fullPage: false });
  console.log(`Captured ${path.relative(repoRoot, target)}`);
}

async function redactDemoPath(page) {
  await page.evaluate((actualPath) => {
    const replacement = "examples/demo-project";
    const replaceText = (value) => String(value || "").split(actualPath).join(replacement);
    document.querySelectorAll("input, textarea").forEach((element) => {
      element.value = replaceText(element.value);
    });
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    textNodes.forEach((node) => {
      node.textContent = replaceText(node.textContent);
    });
  }, demoProjectRoot);
}

async function main() {
  fs.mkdirSync(outputDir, { recursive: true });
  const server = spawn(
    pythonExecutable,
    ["-m", "workflow.web_app", "--host", "127.0.0.1", "--port", "8000", "--project-root", demoProjectRoot],
    { cwd: repoRoot, stdio: ["ignore", "pipe", "pipe"] }
  );

  let browser;
  try {
    const url = await waitForServerUrl(server);
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 980 }, deviceScaleFactor: 1 });
    await page.goto(url, { waitUntil: "networkidle" });
    await page.click("#loadDemoProject");
    await page.evaluate(() => window.scrollTo(0, 0));
    await redactDemoPath(page);
    await capture(page, "web-workbench-home.png");

    await page.locator('button[data-action="workflow_status"]').first().click();
    await waitForAction(page);
    await page.evaluate(() => document.querySelector("#resultPanel").scrollIntoView({ block: "center" }));
    await redactDemoPath(page);
    await capture(page, "workflow-status.png");

    await page.locator('button[data-action="project_check"]').first().click();
    await waitForAction(page);
    await page.evaluate(() => document.querySelector("#resultPanel").scrollIntoView({ block: "center" }));
    await redactDemoPath(page);
    await capture(page, "project-check.png");
  } finally {
    if (browser) await browser.close();
    server.kill();
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
