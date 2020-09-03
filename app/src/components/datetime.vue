<template>
    <div>
        Update: {{datetime.toLocaleDateString()}} {{datetime.toLocaleTimeString()}}
        <button v-if='refresh' v-on:click="do_refresh">Refresh</button>
    </div>
</template>
<script lang='ts'>
import { Vue, Component, Prop } from 'vue-property-decorator';

@Component
export default class Datetime extends Vue {
  @Prop() readonly datetime!: Date;
  @Prop({default:true, type:Boolean}) readonly refresh!: Boolean;

  do_refresh() {
      (this as any).$eventBus.$emit('refresh')
  }
}
</script>

<style scoped>
div {
    font-family: monospace;
    font-size: 10pt;
    float: right;
}
button {
    margin: 0;
    font-size: 8pt;
}
</style>