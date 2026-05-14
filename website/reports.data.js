import { createContentLoader } from 'vitepress'

/**
 * Dynamically discovers all .md files in reports/.
 * Adding a new company report is as simple as dropping a new .md file there.
 *
 * Each report should have frontmatter like:
 *   ---
 *   ticker: AMD
 *   company: Advanced Micro Devices, Inc.
 *   tags: [半导体, AI芯片]
 *   date: 2026年5月
 *   description: 简短描述
 *   ---
 *
 * If frontmatter is missing, title is extracted from the first H1.
 */
export default createContentLoader('reports/*.md', {
  includeSrc: true,
  transform(rawData) {
    return rawData
      .map((page) => {
        // Extract H1 title from source as fallback
        const h1Match = page.src?.match(/^#\s+(.+)$/m)
        const title =
          page.frontmatter.title ||
          (h1Match ? h1Match[1].trim() : page.url.split('/').pop() || '未命名报告')

        // Try to infer ticker from filename if not in frontmatter
        const filename = page.url.split('/').pop() || ''
        const tickerMatch = filename.match(/^([A-Z]+)/)
        const ticker = page.frontmatter.ticker || (tickerMatch ? tickerMatch[1] : '')

        return {
          title,
          url: page.url,
          ticker,
          company: page.frontmatter.company || '',
          tags: page.frontmatter.tags || [],
          date: page.frontmatter.date || '',
          description: page.frontmatter.description || '',
        }
      })
      // Sort by date descending (lexicographic works for YYYY年MM月 format)
      .sort((a, b) => (b.date > a.date ? 1 : -1))
  },
})
