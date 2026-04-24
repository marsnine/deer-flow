#!/usr/bin/env node
/**
 * export_deck_stage_pdf.mjs — Single-file <deck-stage> architecture-specific PDF export
 *
 * Usage:
 *   node export_deck_stage_pdf.mjs --html <deck.html> --out <file.pdf> [--width 1920] [--height 1080]
 *
 * When should I use this script?
 * - Your deck is a **single HTML file**, all slides are `<section>`, and the outer layer is wrapped with `<deck-stage>`
 * - At this time `export_deck_pdf.mjs` (for multiple files) is not used
 *
 * Why can’t we use `page.pdf()` directly (2026-04-20 pitfall record):
 * 1. deck-stage’s shadow CSS `::slotted(section) { display: none }` makes only active slide visible
 * 2. The outer layer `!important` under print media cannot suppress the shadow DOM rules
 * 3. Result: PDF always has only 1 page (the active one)
 *
 *Solution:
 * After opening the HTML, use page.evaluate to pull all sections out of the deck-stage slot.
 * Hang to an ordinary div under the body, inline style forces position:relative + fixed size,
 * Add page-break-after: always to each section, and change the last one to auto to avoid trailing blank pages.
 *
 * Depends on: playwright
 *   npm install playwright
 *
 * Output features:
 * - text preserved vector (copyable, searchable)
 * - Visual 1:1 fidelity
 * - Fonts must be loadable by Chromium (native fonts or Google Fonts)
 */

import { chromium } from 'playwright';
import fs from 'fs/promises';
import path from 'path';

function parseArgs() {
  const args = { width: 1920, height: 1080 };
  const a = process.argv.slice(2);
  for (let i = 0; i < a.length; i += 2) {
    const k = a[i].replace(/^--/, '');
    args[k] = a[i + 1];
  }
  if (!args.html || !args.out) {
    console.error('Usage: node export_deck_stage_pdf.mjs --html <deck.html> --out <file.pdf> [--width 1920] [--height 1080]');
    process.exit(1);
  }
  args.width = parseInt(args.width);
  args.height = parseInt(args.height);
  return args;
}

async function main() {
  const { html, out, width, height } = parseArgs();
  const htmlAbs = path.resolve(html);
  const outFile = path.resolve(out);

  await fs.access(htmlAbs).catch(() => {
    console.error(`HTML file not found: ${htmlAbs}`);
    process.exit(1);
  });

  console.log(`Rendering ${path.basename(htmlAbs)} → ${path.basename(outFile)}`);

  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width, height } });
  const page = await ctx.newPage();

  await page.goto('file://' + htmlAbs, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2500);  // etc. Google Fonts + deck-stage init

  // Core fix: Pull out section from shadow DOM slot and flatten it
  const sectionCount = await page.evaluate(({ W, H }) => {
    const stage = document.querySelector('deck-stage');
    if (!stage) throw new Error('<deck-stage> not found — this script only applies to single-file deck-stage architecture');
    const sections = Array.from(stage.querySelectorAll(':scope > section'));
    if (!sections.length) throw new Error('No <section> found inside <deck-stage>');

    // Inject print styles
    const style = document.createElement('style');
    style.textContent = `
      @page { size: ${W}px ${H}px; margin: 0; }
      html, body { margin: 0 !important; padding: 0 !important; background: #fff; }
      deck-stage { display: none !important; }
    `;
    document.head.appendChild(style);

    // Spread flat under the body
    const container = document.createElement('div');
    container.id = 'print-container';
    sections.forEach(s => {
      // Inline style gets highest priority; make sure position:relative allows absolute children to be properly constrained
      s.style.cssText = `
        width: ${W}px !important;
        height: ${H}px !important;
        display: block !important;
        position: relative !important;
        overflow: hidden !important;
        page-break-after: always !important;
        break-after: page !important;
        margin: 0 !important;
        padding: 0 !important;
      `;
      container.appendChild(s);
    });
    // The last page is not paginated to avoid blank pages at the end.
    const last = sections[sections.length - 1];
    last.style.pageBreakAfter = 'auto';
    last.style.breakAfter = 'auto';
    document.body.appendChild(container);
    return sections.length;
  }, { W: width, H: height });

  await page.waitForTimeout(800);

  await page.pdf({
    path: outFile,
    width: `${width}px`,
    height: `${height}px`,
    printBackground: true,
    preferCSSPageSize: true,
  });

  await browser.close();

  const stat = await fs.stat(outFile);
  const kb = (stat.size / 1024).toFixed(0);
  console.log(`\n✓ Wrote ${outFile}  (${kb} KB, ${sectionCount} pages, vector)`);
  console.log(` Verify the number of pages: mdimport "${outFile}" && pdfinfo "${outFile}" | grep Pages`);
}

main().catch(e => { console.error(e); process.exit(1); });
