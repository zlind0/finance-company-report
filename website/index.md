---
layout: page
title: 深度研究报告
---

<script setup>
import { data as reports } from './reports.data.js'
</script>

<div class="home-hero">
  <h1>📊 深度研究报告</h1>
  <p>精选上市公司财务与战略深度分析</p>
</div>

<div class="reports-grid">
  <a
    v-for="report in reports"
    :key="report.url"
    :href="report.url"
    class="report-card"
  >
    <div class="card-ticker">{{ report.ticker || '📄' }}</div>
    <div v-if="report.company" class="card-company">{{ report.company }}</div>
    <div class="card-title">{{ report.title }}</div>
    <div v-if="report.description" class="card-description">{{ report.description }}</div>
    <div class="card-meta">
      <span v-for="tag in report.tags" :key="tag" class="card-tag">{{ tag }}</span>
      <span v-if="report.date" class="card-date">{{ report.date }}</span>
    </div>
    <div class="card-arrow">阅读报告 →</div>
  </a>
</div>
