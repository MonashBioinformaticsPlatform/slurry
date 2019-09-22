<template>
    <div>
        <img class='rotate' src='/Slurmlogo.png' :width="size"/>
    </div>
</template>
<script lang='ts'>
import { Vue, Component, Prop } from 'vue-property-decorator';

@Component
export default class Logo extends Vue {
  @Prop({ default: '50%' }) readonly size!: string
}
</script>

<style scoped>

.rotate {
  animation: rotation 2s infinite linear;
}

@keyframes rotation {
  0% { transform: rotate(-10deg); }
  50% { transform: rotate(30deg); }
  100% { transform: rotate(-10deg); }
}

</style>