#!/usr/bin/env node
/**
 * Generate a PDF from the merged book HTML.
 *
 * Usage:
 *   node gen_pdf.js                  # English book (default)
 *   node gen_pdf.js en               # English book
 *   node gen_pdf.js zh               # Chinese book
 *   node gen_pdf.js book_en.html     # Explicit file
 *
 * Output lands next to the HTML file with a .pdf extension.
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  const arg = process.argv[2] || 'en';
  let htmlFile;
  if (arg === 'en') htmlFile = 'book_en.html';
  else if (arg === 'zh') htmlFile = 'book.html';
  else htmlFile = arg;

  const htmlPath = path.resolve(__dirname, htmlFile);
  if (!fs.existsSync(htmlPath)) {
    console.error(`File not found: ${htmlPath}`);
    process.exit(1);
  }

  const pdfPath = htmlPath.replace(/\.html$/, '.pdf');
  console.log(`Input:  ${htmlPath}`);
  console.log(`Output: ${pdfPath}`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();

  await page.goto(`file://${htmlPath}`, {
    waitUntil: 'networkidle0',
    timeout: 120000,
  });

  // Wait for KaTeX rendering
  await page.evaluate(() => new Promise(r => {
    if (document.readyState === 'complete') r();
    else window.addEventListener('load', r);
  }));
  await new Promise(r => setTimeout(r, 3000));

  // Hide sidebar and back-to-top for print; center content
  await page.addStyleTag({
    content: `
      aside.toc { display: none !important; }
      .back-top  { display: none !important; }
      body { display: block !important; }
      main {
        max-width: 100% !important;
        margin: 0 !important;
        padding: 40px 60px 60px 60px !important;
      }
      .book-cover { min-height: auto !important; }
      .chapter-divider { page-break-before: always; }
      pre { white-space: pre-wrap !important; word-wrap: break-word !important; }
    `,
  });

  await page.pdf({
    path: pdfPath,
    format: 'A4',
    printBackground: true,
    margin: { top: '20mm', bottom: '20mm', left: '18mm', right: '18mm' },
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `
      <div style="width:100%;text-align:center;font-size:9px;color:#999;padding:0 20mm;">
        <span class="pageNumber"></span> / <span class="totalPages"></span>
      </div>`,
    timeout: 300000,
  });

  await browser.close();
  const sizeMB = (fs.statSync(pdfPath).size / 1024 / 1024).toFixed(1);
  console.log(`Done! ${sizeMB} MB`);
})();
