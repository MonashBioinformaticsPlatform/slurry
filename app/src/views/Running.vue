<template>
  <div class="home">
    <datetime :datetime="dt"/>
    <h1>Running</h1>
    <div class='slim-container'>
      <slim-grid ref='slimgrid'
                :data="config"
                :downloadable="false"
                :column-options="columns"
                @after-init='afterInit'
                ></slim-grid>
    </div>
  </div>
</template>

<script lang="js">
import { Component, Vue, Watch } from 'vue-property-decorator';
import SlimGrid from 'vue-slimgrid';
import datetime from '@/components/datetime.vue'

@Component({
  components: {
    SlimGrid, datetime
  },
})
export default class Running extends Vue {
  columns = {
    'CPUS': {
      order: 0,
    },
    'NODES': {
      order: 1,
    },
    'USER': {
      order: 2,
    },
    'PARTITIONS' : {
      order: 3,
      width: 200,
      cssClass: 'left',
      formatter(row, cell, value, cd, dc) {
        let res = ""
        for (const [name, num] of Object.entries(value)) {
          res += `${name}:${num}  `
        }
        return res
      }
    },
  }

  get config () {
    var by_user = {}
    for (var row of this.$global.queue.data) {
        if (row.STATE == 'RUNNING') {
            if (!(row.USER in by_user)) {
                by_user[row.USER] = {CPUS:0, NODES:0,PARTITIONS:{}}
            }
            let u = by_user[row.USER]
            u.CPUS += row.CPUS
            u.NODES += row.NODES
            u.USER = row.USER
            u.id = row.USER
            if (!(row.PARTITION in u.PARTITIONS))
              u.PARTITIONS[row.PARTITION] = 0
            u.PARTITIONS[row.PARTITION] += 1
        }
    }
    return Object.values(by_user)
  }

  afterInit(args) {
    // Get slimgrid to do the sorting
    let sortCol = 'CPUS'
    this.$refs.slimgrid.sort(null, {command: 'sort-desc', grid: args.grid, sortCols: [{field: sortCol}]})
    // And this just sets the glyph
    args.grid.setSortColumn(sortCol, false)
  }

  get dt () {
    return new Date(this.$global.queue.updated)
  }
}
</script>

<style src="vue-slimgrid/dist/slimgrid.css"></style>
<style scoped>
div >>> .left {
  text-align: left;
}
div >>> .slim-container {
    width: 720px;
}
</style>