# CLAUDE.md — Building Intelligence

## Project Overview

A bilingual (Chinese/English) technical book about AI engineering, delivered as single-file HTML. The book covers math foundations, systems software, AI model technology, LLM technology, and 26 paper deep dives.

## File Architecture

### Source Files (authoritative)
- `ch0_preface.html` through `ch5_partC_supplement.html` — Chinese chapter sources
- `en/ch0_preface.html` through `en/ch5_partC_supplement.html` — English chapter sources

### Merged Books (generated)
- `book.html` — Chinese merged book (generated from source files)
- `book_en.html` — English merged book (generated from en/ source files)

**Important**: Edit source files first, then rebuild merged books. Never edit only the merged books — changes will be lost on next rebuild.

## Build Pipeline

The merged books are built from source files with these transformations:
1. Extract `<main>` content from each chapter
2. Escape `<` and `>` inside `<pre><code>` blocks
3. Convert `$...$` to `<span class="math-i">` and `$$...$$` to `<span class="math-d">`
4. Fix Unicode math symbols (≈→\approx, ≤→\le, etc.) inside math spans
5. Remove spaces between Chinese and English text (Chinese edition only)
6. Fix cross-references (`ch5_partA_preview.html#p01` → `#p01`)
7. Reorder Ch 5 papers by chapter relevance and renumber P01-P26
8. Fix bare `$` signs that contain `<` (convert to `&lt;` inside math spans)
9. Fix currency `$` signs (replace with `US$` or Chinese equivalents)

## Known Gotchas

### Formula `<` Problem
Math expressions containing `<` (like `$m < n$`) will break the DOM because browsers interpret `<` as an HTML tag start. These MUST be handled specially:
- In source files: `$m < n$` is fine (browsers handle it inside `<main>`)
- In merged books: must become `<span class="math-i">m &lt; n</span>`
- The build pipeline handles this, but new formulas with `<` need the same treatment

### Currency `$` Problem
Dollar signs for currency (e.g., `$5.6M`) will be misinterpreted as math delimiters. In source files, use alternatives:
- Chinese: write `560万美元` instead of `$560万`
- English: write `US$5.6M` instead of `$5.6M`

### Paper Numbering
Papers are renumbered during merge. Source files use original IDs (p01-p26 as authored). Merged books renumber them sequentially based on chapter order:
- P01-P02: Ch 2 related (HNSW, Raft)
- P03-P11: Ch 3 related (ResNet, LSTM, BatchNorm, Adam, XGBoost, GAN, VAE, DDPM, Word2Vec)
- P12-P26: Ch 4 related (Attention, BERT/GPT, Scaling Law, RoPE, FlashAttention, LoRA, PagedAttention, MoE, Mamba, InstructGPT, DPO, CoT, DeepSeek-V3, RAG, ReAct)

### Ch 4 Source File
The Ch 4 source file (`ch4_llm_tech.html`) has Chinese content but English TOC sidebar entries were partially restored. The rebuild script extracts TOC from source, so ensure sidebar labels match the intended language.

## Tech Stack
- **Math**: KaTeX 0.16.11 (loaded via CDN, rendered with `katex.render()` on `DOMContentLoaded`)
- **Code**: highlight.js 11.9.0 + Rust language pack
- **Diagrams**: Mermaid 10
- **Fonts**: Source Serif Pro (serif), Inter (sans), JetBrains Mono (code)

## Modification Workflow (MANDATORY)

Any content change MUST follow this 4-step pipeline to keep all 4 targets in sync:

```
Chinese Source → English Source → book.html → book_en.html
     (1)              (2)            (3)           (3)
```

### Step 1: Edit Chinese source file
- Make the content change in the Chinese source (e.g., `ch3_ai_model_tech.html`)
- This is the single source of truth for content

### Step 2: Translate to English source file
- Translate the changed content to English
- Apply the translation to the corresponding English source (e.g., `en/ch3_ai_model_tech.html`)
- Verify: no grammar errors, no awkward phrasing, no remaining Chinese in the English file
- Technical terms and proper nouns stay in English in both versions

### Step 3: Rebuild both merged books
- Run the rebuild script to regenerate `book.html` (from Chinese sources) and `book_en.html` (from English sources)
- The script applies: code escaping, math span conversion, space removal, cross-ref fixing, paper renumbering
- Never hand-edit the merged books — they are generated artifacts

### Step 4: Verify consistency
- Confirm the change appears in all 4 files: Chinese source, English source, book.html, book_en.html
- Check for zero bare `$` signs in both merged books
- Commit all 4 changed files together in one git commit

### What NOT to do
- Do NOT edit only `book.html` or `book_en.html` — changes will be overwritten on next rebuild
- Do NOT edit only the English source without updating the Chinese source first
- Do NOT commit source files and merged books from different content states

## Other Editing Notes

- **CSS/cover changes**: Edit directly in `book.html` — the rebuild script preserves the `<style>` block and cover from the existing merged file
- **Adding formulas**: Use `$...$` for inline, `<div class="formula">$...$</div>` for display. Avoid `<` inside formulas — use `\lt` or write the comparison in prose
- **Adding papers**: Add to the appropriate `ch5_partX` source file, update the paper order arrays in the build script
- **References**: Edit the `<section id="refs">` directly in the merged books (not generated from source)
