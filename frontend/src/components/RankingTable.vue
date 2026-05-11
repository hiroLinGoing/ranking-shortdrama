<script setup>
defineProps({
  list: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})

function rankClass(rank) {
  if (rank === 1) return 'rank rank-1'
  if (rank === 2) return 'rank rank-2'
  if (rank === 3) return 'rank rank-3'
  return 'rank'
}

function rankLabel(rank) {
  const map = { 1: '🥇', 2: '🥈', 3: '🥉' }
  return map[rank] || rank
}
</script>

<template>
  <div class="card">
    <div v-if="loading" class="empty">加载中...</div>
    <div v-else-if="list.length === 0" class="empty">暂无数据</div>

    <!-- 桌面端：表格 -->
    <table v-else class="ranking desktop-only">
      <thead>
        <tr>
          <th style="width: 90px">排名</th>
          <th>产品名</th>
          <th>公司名</th>
          <th>主要投放国家/地区</th>
          <th class="num">投放素材数</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in list" :key="item.rank">
          <td>
            <span :class="rankClass(item.rank)">{{ rankLabel(item.rank) }}</span>
          </td>
          <td class="product">{{ item.product }}</td>
          <td class="company">{{ item.company }}</td>
          <td>
            <span v-for="r in item.regions" :key="r" class="region-tag">{{ r }}</span>
          </td>
          <td class="num materials">{{ item.materials_text }}</td>
        </tr>
      </tbody>
    </table>

    <!-- 移动端：卡片列表 -->
    <ul v-if="!loading && list.length > 0" class="ranking-mobile mobile-only">
      <li v-for="item in list" :key="item.rank" class="m-row">
        <div class="m-rank-col">
          <span :class="rankClass(item.rank)">{{ rankLabel(item.rank) }}</span>
        </div>
        <div class="m-main">
          <div class="m-line">
            <span class="m-product">{{ item.product }}</span>
            <span class="m-materials">{{ item.materials_text }}</span>
          </div>
          <div class="m-company">{{ item.company }}</div>
          <div class="m-regions">
            <span v-for="r in item.regions" :key="r" class="region-tag">{{ r }}</span>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(255, 122, 139, 0.08);
}

.empty {
  padding: 40px;
  text-align: center;
  color: #999;
}

.ranking {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.ranking thead {
  background: linear-gradient(135deg, #ffe1e6, #ffeadc);
}

.ranking th {
  text-align: left;
  padding: 14px 16px;
  font-weight: 700;
  color: #c2385a;
}

.ranking td {
  padding: 12px 16px;
  border-bottom: 1px solid #fff0f0;
  vertical-align: middle;
}

.ranking tbody tr:hover {
  background: #fff7f5;
}

.num {
  text-align: right;
}

.product {
  font-weight: 700;
  color: #2d1b22;
}

.company {
  color: #666;
}

.materials {
  font-weight: 700;
  color: #ff5677;
}

.rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 30px;
  height: 30px;
  border-radius: 8px;
  background: #fff0f0;
  color: #c2385a;
  font-weight: 700;
}

.rank-1 { background: linear-gradient(135deg, #ffe27a, #ffb347); color: #fff; }
.rank-2 { background: linear-gradient(135deg, #d8d8d8, #b0b0b0); color: #fff; }
.rank-3 { background: linear-gradient(135deg, #f3a47a, #c97744); color: #fff; }

.region-tag {
  display: inline-block;
  margin: 2px 6px 2px 0;
  padding: 3px 10px;
  background: #fff0f0;
  color: #d23a55;
  font-size: 12px;
  border-radius: 999px;
}

/* ========== 显示切换 ========== */
.mobile-only { display: none; }
.desktop-only { display: table; }

/* ========== 移动端卡片列表 ========== */
.ranking-mobile {
  list-style: none;
  padding: 6px 0;
  margin: 0;
}

.m-row {
  display: flex;
  gap: 12px;
  padding: 12px 14px;
  border-bottom: 1px solid #fff0f0;
}
.m-row:last-child {
  border-bottom: none;
}

.m-rank-col {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.m-main {
  flex: 1;
  min-width: 0;
}

.m-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.m-product {
  font-weight: 700;
  color: #2d1b22;
  font-size: 15px;
  word-break: break-word;
  flex: 1;
  min-width: 0;
}

.m-materials {
  font-weight: 700;
  color: #ff5677;
  font-size: 14px;
  flex-shrink: 0;
}

.m-company {
  color: #888;
  font-size: 12.5px;
  margin-top: 4px;
  word-break: break-word;
}

.m-regions {
  margin-top: 6px;
}

@media (max-width: 640px) {
  .desktop-only { display: none !important; }
  .mobile-only { display: block !important; }

  .rank {
    min-width: 28px;
    height: 28px;
    font-size: 12px;
    border-radius: 7px;
  }

  .region-tag {
    font-size: 11px;
    padding: 2px 8px;
    margin: 2px 4px 2px 0;
  }
}
</style>
