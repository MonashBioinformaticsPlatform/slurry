<template>
    <div>
        Update: {{datetime.toLocaleDateString()}} {{datetime.toLocaleTimeString()}}
    </div>
</template>
<script lang='ts'>
import { Vue, Component, Prop } from 'vue-property-decorator';

@Component
export default class Logo extends Vue {
  @Prop() readonly datetime!: Date;
}
</script>

<style scoped>
div {
    font-family: monospace;
    font-size: 10t;
    float: right;
}
</style>