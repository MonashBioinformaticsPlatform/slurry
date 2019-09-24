<template>
  <div class="home">
    <datetime :datetime="dt"/>
    <h1>Queue</h1>
    Max : {{maxPrio}}
    <slim-grid ref='slimgrid'
               :data="queue"
               :column-options="columns"
               :downloadable="false"
               @data-view-update='dataViewUpdate'
               @after-init='afterInit'
               @mouse-enter='mouseEnter'
               @mouse-leave='mouseLeave'
               ></slim-grid>
  </div>
</template>

<script lang="js">
import { Component, Vue, Watch } from 'vue-property-decorator';
import SlimGrid from 'vue-slimgrid';
import * as d3 from "d3";

import datetime from '@/components/datetime.vue';

@Component({
  components: {
    SlimGrid,datetime
  },
})
export default class Queue extends Vue {
  maxPrio = 0
  columns = {}
  weights = [["PriorityWeightAge","sprio.AGE"],
             ["PriorityWeightFairShare","sprio.FAIRSHARE"],
             ["PriorityWeightJobSize","sprio.JOBSIZE"],
             ["PriorityWeightPartition","sprio.PARTITION"],
             ["PriorityWeightQOS","sprio.QOS"],
             ["PriorityWeightTRES","sprio.TRES"]]

  makeColumns() {
    let self = this
    let colourScale = d3.scaleOrdinal(d3.schemeAccent)

    return {
      'JOBID': {
        width: 100,
        order: 0,
      },
      'USER': {
        width: 100,
        order: 1,
      },
      'CPUS': {
        width: 50,
        order: 2,
        cssClass: 'right'
      },
      'NODES': {
        width: 60,
        order: 3,
        cssClass: 'right'
      },
      'PRIORITY': {
        width: 100,
        order: 4,
        cssClass: 'right',
        formatter(row, cell, value, cd, dc) {
          if (self.maxPrio>0) {
            let str = `<rect height=20 width=${1.0*value/self.maxPrio * 100} fill='#f99' />`
            let xpos = 0
            if (dc['sprio.JOBID']) {
              for (let w of self.weights) {
                //let v = +self.configAsDict[w[0]] * dc[w[1]]
                let v = dc[w[1]]
                let width = 1.0*v/self.maxPrio * 100
                str += `<rect x=${xpos} height=20 width=${width} fill='${colourScale(w[0])}' />`
                xpos += width
              }
            }
            return `<svg>${str}</svg><div class='priority'>${value}</div>`
          }
        }
      },
      'PARTITION': {
        width: 100,
        order: 5,
        },
      'STATE' : {
        width: 100,
        order: 6,
      },
      'NAME': { width: 150, order: 7 },
      'NODELIST(REASON)': { width: 150, order: 8 },
      'TIME': {width: 100, order: 9 },
      'TIME_LIMIT': {width: 100, order: 10 },
      'sprio.AGE': {width: 100, order: 11},
      'sprio.FAIRSHARE': {width: 100, order: 12},
      'sprio.JOBSIZE': {width: 100, order: 13},
      'sprio.PARTITION': {width: 100, order: 14},
      'sprio.QOS': {width: 100, order: 15},
      'sprio.JOBID': {hidden: true},
      'sprio.PRIORITY': {hidden: true},
      'sprio.TRES': {hidden: true},
      '*' : { }
    }
  }

  get config() {
    return this.$global.config.data
  }

  get configAsDict() {
    return Object.fromEntries(this.config.map(x => [x.key,x.value]))
  }

  get queue () {
    return this.$global.queue.data
  }
  get dt () {
    return new Date(this.$global.queue.updated)
  }

  setMaxPriority(lst) {
    this.maxPrio = Math.max(... lst.map(x => x.PRIORITY))
  }
  dataViewUpdate(args) {
    this.setMaxPriority(Array(args.grid.getDataLength()).fill(10).map((_,idx) => args.grid.getDataItem(idx)))
    args.grid.invalidate()
  }

  afterInit(args) {
    this.$refs.slimgrid.filters["PARTITION"]="comp"
    this.$refs.slimgrid.filters["STATE"]="pending"

    // Get slimgrid to do the sorting
    let sortCol = 'PRIORITY'
    this.$refs.slimgrid.sort(null, {command: 'sort-desc', grid: args.grid, sortCols: [{field: sortCol}]})
    // And this just sets the glyph
    args.grid.setSortColumn(sortCol, false)
  }

  mouseEnter(e,args) {
    //console.log("mouse-in",e,args)
  }
  mouseLeave(e,args) {
    //console.log("mouse-out",args)
  }

  mounted() {
    this.columns = this.makeColumns()
  }
}
</script>

<style src="vue-slimgrid/dist/slimgrid.css"></style>
<style scoped>
div >>> .right {
  text-align: right;
}
div >>> .priority {
  position: absolute;
  top: 0;
  right: 10px;
  color: black;
}
</style>
