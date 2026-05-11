<script setup>
import { onMounted, ref, computed } from 'vue'
import {
  fetchMeta,
  fetchRanking,
  fetchRegionStats,
  fetchTopStats
} from './api.js'
import RankingTable from './components/RankingTable.vue'
import TopChart from './components/TopChart.vue'
import RegionChart from './components/RegionChart.vue'
import ChatBot from './components/ChatBot.vue'

const meta = ref(null)
const list = ref([])
const regionStats = ref([])
const topStats = ref([])

const keyword = ref('')
const region = ref('')
const loading = ref(false)
const error = ref('')

const allRegions = computed(() => {
  const set = new Set()
  list.value.forEach((it) => it.regions.forEach((r) => set.add(r)))
  return [...set].sort()
})

const filteredList = computed(() => {
  let arr = list.value
  if (region.value) {
    arr = arr.filter((it) => it.regions.includes(region.value))
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    arr = arr.filter(
      (it) =>
        it.product.toLowerCase().includes(kw) ||
        it.company.toLowerCase().includes(kw)
    )
  }
  return arr
})

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [m, r, rs, ts] = await Promise.all([
      fetchMeta(),
      fetchRanking(),
      fetchRegionStats(),
      fetchTopStats(10)
    ])
    meta.value = m
    list.value = r.list
    regionStats.value = rs
    topStats.value = ts
  } catch (e) {
    error.value = `数据加载失败：${e.message}（请确认后端 http://localhost:8001 已启动）`
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>

<template>
  <div class="page">
    <header class="hero">
      <div class="hero-left">
        <div class="brand">DataEye</div>
        <h1>海外微短剧APP素材投放（总榜）</h1>
        <p v-if="meta" class="period">
          统计时间：{{ meta.period.start }} ~ {{ meta.period.end }} · 共
          <b>{{ meta.total }}</b> 个产品
        </p>
      </div>
      <div class="hero-decor">短剧</div>
    </header>

    <section v-if="error" class="error-card">{{ error }}</section>

    <section class="charts">
      <div class="chart-card">
        <div class="chart-title">素材投放数 TOP 10</div>
        <TopChart :data="topStats" />
      </div>
      <div class="chart-card">
        <div class="chart-title">主要投放国家/地区分布</div>
        <RegionChart :data="regionStats" />
      </div>
    </section>

    <section class="filters">
      <input
        v-model="keyword"
        type="text"
        placeholder="搜索产品名 / 公司名"
        class="search"
      />
      <select v-model="region" class="select">
        <option value="">全部国家/地区</option>
        <option v-for="r in allRegions" :key="r" :value="r">{{ r }}</option>
      </select>
      <button class="reset" @click="(keyword = ''), (region = '')">重置</button>
      <span class="count">共 {{ filteredList.length }} 条</span>
    </section>

    <section class="table-wrap">
      <RankingTable :list="filteredList" :loading="loading" />
    </section>

    <footer class="footer">
      <span>数据来源：DataEye · 海外微短剧APP素材投放榜</span>
    </footer>

    <!-- 浮动机器人 -->
    <ChatBot />
  </div>
</template>

<style scoped>
.page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 48px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #ff7a8b 0%, #ff9f7a 100%);
  border-radius: 24px;
  padding: 32px 36px;
  color: #fff;
  box-shadow: 0 18px 40px rgba(255, 122, 139, 0.25);
}

.brand {
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 18px;
  background: rgba(255, 255, 255, 0.2);
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
}

.hero h1 {
  margin-top: 14px;
  font-size: 28px;
  letter-spacing: 1px;
  line-height: 1.3;
}

.period {
  margin-top: 12px;
  font-size: 14px;
  opacity: 0.95;
}

.hero-decor {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #ffd1bd 100%);
  color: #ff5677;
  padding: 18px 22px;
  border-radius: 18px;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.error-card {
  margin-top: 20px;
  padding: 14px 18px;
  background: #fff3f3;
  color: #c0392b;
  border-radius: 12px;
  border: 1px solid #ffd0d0;
  font-size: 14px;
}

.charts {
  margin-top: 28px;
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 20px;
}

.chart-card {
  background: #fff;
  border-radius: 18px;
  padding: 18px 18px 8px;
  box-shadow: 0 10px 30px rgba(255, 122, 139, 0.08);
  min-width: 0; /* 允许在 grid 中收缩 */
}

.chart-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #d23a55;
}

.filters {
  margin-top: 28px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search {
  flex: 1;
  min-width: 220px;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid #ffc6c6;
  background: #fff;
  font-size: 14px;
  outline: none;
  transition: border 0.2s;
}
.search:focus {
  border-color: #ff7a8b;
}

.select {
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid #ffc6c6;
  background: #fff;
  font-size: 14px;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3e%3cpath fill='%23ff7a8b' d='M6 8 0 0h12z'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 34px;
}

.reset {
  padding: 10px 18px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #ff7a8b, #ff9f7a);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}

.count {
  margin-left: auto;
  color: #888;
  font-size: 13px;
}

.table-wrap {
  margin-top: 16px;
}

.footer {
  margin-top: 32px;
  text-align: center;
  color: #999;
  font-size: 13px;
  padding-bottom: 80px; /* 留给浮动机器人按钮 */
}

/* ========== 平板适配 (≤900px) ========== */
@media (max-width: 900px) {
  .charts {
    grid-template-columns: 1fr;
  }
  .hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 18px;
  }
}

/* ========== 移动端 H5 适配 (≤640px) ========== */
@media (max-width: 640px) {
  .page {
    padding: 16px 14px 24px;
  }

  .hero {
    border-radius: 18px;
    padding: 22px 20px;
    gap: 14px;
  }

  .brand {
    font-size: 13px;
    padding: 3px 10px;
  }

  .hero h1 {
    margin-top: 10px;
    font-size: 20px;
    letter-spacing: 0.5px;
  }

  .period {
    margin-top: 8px;
    font-size: 12px;
  }

  .hero-decor {
    font-size: 20px;
    padding: 12px 16px;
    border-radius: 14px;
    align-self: flex-end;
  }

  .charts {
    margin-top: 18px;
    gap: 14px;
  }

  .chart-card {
    border-radius: 14px;
    padding: 14px 12px 4px;
  }

  .chart-title {
    font-size: 14px;
  }

  .filters {
    margin-top: 18px;
    gap: 8px;
  }

  .search {
    flex: 1 1 100%;
    min-width: 0;
    font-size: 14px;
    padding: 9px 14px;
  }

  .select {
    flex: 1 1 0;
    min-width: 0;
    font-size: 14px;
    padding: 9px 30px 9px 14px;
  }

  .reset {
    padding: 9px 16px;
    font-size: 13px;
  }

  .count {
    flex-basis: 100%;
    margin-left: 0;
    text-align: right;
  }

  .footer {
    margin-top: 20px;
    font-size: 12px;
    padding-bottom: 90px;
  }
}
</style>
