<template>
  <div class="home">
    <h1>Config</h1>
    <slim-grid :data="config"></slim-grid>
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
export default class Config extends Vue {
  get config () {
    return this.$global.config
  }
}
</script>

<style src="vue-slimgrid/dist/slimgrid.css"></style>
