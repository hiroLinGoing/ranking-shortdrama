<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DatasetComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, TitleComponent, DatasetComponent])

const props = defineProps({
  data: { type: Array, required: true }
})

const option = computed(() => {
  const sorted = [...props.data].sort((a, b) => a.materials - b.materials)
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<br/>素材数：<b>${p.value.toLocaleString()}</b>`
      }
    },
    grid: { left: 90, right: 30, top: 10, bottom: 30, containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: (v) => (v >= 10000 ? v / 10000 + 'w' : v)
      }
    },
    yAxis: {
      type: 'category',
      data: sorted.map((d) => d.product),
      axisLabel: { fontSize: 12 }
    },
    series: [
      {
        type: 'bar',
        data: sorted.map((d) => d.materials),
        barMaxWidth: 18,
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#ffb347' },
              { offset: 1, color: '#ff5677' }
            ]
          }
        },
        label: {
          show: true,
          position: 'right',
          formatter: (p) =>
            p.value >= 10000 ? (p.value / 10000).toFixed(1) + 'w' : p.value,
          color: '#d23a55',
          fontWeight: 700
        }
      }
    ]
  }
})
</script>

<template>
  <v-chart class="chart" :option="option" autoresize />
</template>

<style scoped>
.chart {
  width: 100%;
  height: 380px;
}

@media (max-width: 640px) {
  .chart {
    height: 320px;
  }
}
</style>
