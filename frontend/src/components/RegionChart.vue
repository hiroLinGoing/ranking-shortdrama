<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import {
  TooltipComponent,
  LegendComponent,
  TitleComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent, TitleComponent])

const props = defineProps({
  data: { type: Array, required: true }
})

const palette = [
  '#ff5677', '#ff7a8b', '#ff9f7a', '#ffb347', '#ffd166',
  '#f9844a', '#ee6c4d', '#e63946', '#d62828', '#f4a261',
  '#e76f51', '#fcbf49'
]

const option = computed(() => ({
  color: palette,
  tooltip: {
    trigger: 'item',
    formatter: '{b}<br/>出现次数：<b>{c}</b> ({d}%)'
  },
  legend: {
    type: 'scroll',
    bottom: 0,
    textStyle: { fontSize: 12 }
  },
  series: [
    {
      name: '国家/地区',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '46%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        formatter: '{b}\n{d}%',
        fontSize: 11
      },
      data: props.data.map((d) => ({ name: d.region, value: d.count }))
    }
  ]
}))
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
    height: 340px;
  }
}
</style>
