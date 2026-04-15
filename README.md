# Building Intelligence

**The Complete AI Engineer's Knowledge Map**

From calculus gradients to Agent tool calls — one book covering everything an AI engineer needs to know.

[Chinese Edition](book.html) | [English Edition](book_en.html)

## What Is This

A comprehensive technical book covering the full AI engineering stack in 5 chapters + 26 paper deep dives. Written for AI engineers, systems engineers transitioning to AI, and CS students building a complete mental model of the field.

**Scope**: Math foundations, systems software, classical ML/DL, LLM technology (Transformer to Agent), and curated paper analyses — all in one unified system, at the density of "what a senior colleague could explain in 30 minutes."

## Structure

| Chapter | Topic | Sections | Highlights |
|---------|-------|----------|------------|
| Ch 1 | Mathematical Foundations | 7 parts, 29 sections | Calculus, linear algebra, probability, information theory, numerical methods |
| Ch 2 | Systems Software | 6 parts, 28 sections | CPU/GPU, OS internals, compilers, databases, DPDK/VPP |
| Ch 3 | AI Model Technology | 7 parts, 36 sections | Traditional ML, neural operators, CNN/RNN/GAN/VAE/Diffusion, training optimization, FlashAttention |
| Ch 4 | LLM Technology | 12 parts, 39 sections | Transformer, RoPE, MoE, distributed training, inference engines, RAG, Agent frameworks, Coding Agents |
| Ch 5 | Paper Deep Dives | 26 papers | HNSW, Raft, ResNet, LSTM, Attention, BERT/GPT, FlashAttention, LoRA, DPO, DeepSeek-V3, Mamba, RAG, ReAct |
| Refs | References | 30 entries | Core papers P01-P26 + additional references |

Papers in Ch 5 are ordered by chapter relevance: Ch 2 systems papers first, then Ch 3 ML/DL papers, then Ch 4 LLM papers.

## Technical Details

- **Format**: Single-file HTML with embedded CSS, KaTeX math rendering, highlight.js code blocks, Mermaid diagrams
- **Math**: 1400+ formulas rendered via KaTeX (`<span class="math-d">` for display, `<span class="math-i">` for inline)
- **Size**: ~640KB (Chinese), ~760KB (English)
- **Updated**: April 2026, covering DeepSeek V4/R2, Qwen3.6-Plus, Claude Mythos, GPT-5, Gemini 3, Mamba-3, FlashAttention-4

## File Structure

```
building-intelligence/
├── book.html                    # Chinese merged book (open in browser)
├── book_en.html                 # English merged book (open in browser)
├── ch0_preface.html             # Chinese source: Preface
├── ch1_math_foundations.html    # Chinese source: Math
├── ch2_systems_software.html    # Chinese source: Systems
├── ch3_ai_model_tech.html       # Chinese source: AI Models
├── ch4_llm_tech.html            # Chinese source: LLM
├── ch5_partA_preview.html       # Chinese source: Papers P01-P09
├── ch5_partB_preview.html       # Chinese source: Papers P10-P17
├── ch5_partC_supplement.html    # Chinese source: Papers P18-P26
└── en/                          # English source files (same structure)
```

The `book.html` and `book_en.html` files are merged from the individual chapter sources with:
- Paper reordering (by chapter relevance) and renumbering (P01-P26)
- Code block escaping (`<` → `&lt;` inside `<pre><code>`)
- Math conversion to KaTeX spans
- Chinese-English space removal (Chinese edition)
- Cross-reference link fixing

## How to Read

Open `book.html` (Chinese) or `book_en.html` (English) in any modern browser. No server needed — everything is self-contained in a single HTML file.

The sidebar provides full navigation. The cover page suggests four reading paths depending on your background.

## Credits

Written with the assistance of Claude (Anthropic). Cover features the Claude logo.

## License

Internal study material. All rights reserved.
