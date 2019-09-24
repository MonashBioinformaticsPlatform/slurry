<template>
  <div class="home">
    <h1>Running</h1>
    <slim-grid :data="config"
               :downloadable="false"
               ></slim-grid>
  </div>
</template>

<script lang="js">
import { Component, Vue, Watch } from 'vue-property-decorator';
import SlimGrid from 'vue-slimgrid';

@Component({
  components: {
    SlimGrid,
  },
})
export default class Running extends Vue {
  get config () {
    var by_user = {}
    for (var row of this.$global.queue.data) {
        if (row.STATE == 'RUNNING') {
            if (!(row.USER in by_user)) {
                by_user[row.USER] = {CPUS:0, NODES:0}
            }
            by_user[row.USER].CPUS += row.CPUS
            by_user[row.USER].NODES += row.NODES
            by_user[row.USER].USER = row.USER
            by_user[row.USER].id = row.USER
        }
    }
    return Object.values(by_user)
  }
}
</script>

<style src="vue-slimgrid/dist/slimgrid.css"></style>
