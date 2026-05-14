import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '深度研究报告',
  description: '精选上市公司财务与战略深度分析',
  lang: 'zh-CN',
  cleanUrls: true,

  markdown: {
    math: true,
  },

  // Inject aside:'left' + sidebar:false for every report page at build time,
  // so the in-page heading TOC always appears on the LEFT. No code change needed
  // when adding new reports.
  transformPageData(pageData) {
    if (pageData.relativePath.startsWith('reports/')) {
      pageData.frontmatter.aside ??= 'left'
      pageData.frontmatter.sidebar ??= false
    }
  },

  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
    ],

    outline: {
      label: '本文目录',
      level: [2, 3],
    },

    docFooter: {
      prev: false,
      next: false,
    },
    footer: {
      message: '本站内容仅供学习参考，不构成投资建议。股市有风险，投资须谨慎。',
    },
    editLink: undefined,
    lastUpdated: false,
  },
})
