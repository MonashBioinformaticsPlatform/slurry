<template>
  <div class="home">
    <datetime :datetime="dt"/>
    <h1>Queue</h1>
    Max Priority : {{maxPrio}}
    <slim-grid ref='slimgrid'
               :data="queue"
               :explicit-columns="explicitColumns"
               :column-options="columns"
               :row-formatter="rowFormatter"
               :downloadable="false"
               :forceSyncScrolling="true"
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
import * as Prio from '@/assets/prio-weights'

@Component({
  components: {
    SlimGrid,datetime
  },
})
export default class Queue extends Vue {
  maxPrio = 0
  columns = {}
  explicitColumns=[]

  makeColumns() {
    let self = this

    return {
      'rank': {
        width: 50,
        order: 0,
        cssClass: 'right constant',
        headerInput: false,
        headerFilter: false,
        sortable: false,
        formatter(row, cell, value, cd, dc) {
          return row+1
        }
      },
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
            let str = `<rect height=20 width=${1.0*value/self.maxPrio * 100} fill='${Prio.colourScale("Unknown")}' />`
            let xpos = 0
            if (dc['sprio.JOBID']) {
              for (let w of Prio.weights) {
                //let v = +self.configAsDict[w[0]] * dc[w[1]]
                let v = dc[w[1]]
                let width = 1.0*v/self.maxPrio * 100
                str += `<rect x=${xpos} height=20 width=${width} fill='${Prio.colourScale(w[1])}' />`
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
      'JobName': { width: 150, order: 7 },

      'NodeList(Reason)': {
        width: 150,
        order: 8,
      },
      'RunTime': {width: 100, order: 9 },
      'TimeLimit': {width: 100, order: 10 },
      'SubmitTime': {width: 150, order: 10, cssClass: 'monospace right' },
      'StartTime': {width: 150, order: 10, cssClass: 'monospace right' },
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

  rowFormatter(row) {
    if (this.$global.myUser && row.USER.includes(this.$global.myUser)) {
      return {cssClasses: 'highlight'}
    } else {
      return null
    }
  }

  @Watch('globalMyUser')
  onUserChange() {
    this.$refs.slimgrid.slickGrid.invalidateAllRows()
    this.$refs.slimgrid.slickGrid.render()
  }

  get globalMyUser() {
    return this.$global.myUser
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

  created() {
    this.columns = this.makeColumns()
    this.explicitColumns = Object.keys(this.columns).filter(x => x!="*")
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

div >>> .highlight {
  background: #bbb;
}

div >>> .constant {
  background: #f8fafc;
}

div >>> .monospace {
  font-family: monospace;
}

</style>
