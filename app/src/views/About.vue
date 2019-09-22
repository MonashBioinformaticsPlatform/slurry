<template>
  <div class="about">
    <h1>Experimental Slurm queue explorer</h1>
    <h2>Written by <a href="https://github.com/drpowell">David R. Powell</a></h2>
    This app aims to allow easier understanding of the slurm queue on a HPC cluster.
    <Logo size='30%' style='margin-top:20%' />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import Logo from '@/components/Logo.vue'; // @ is an alias to /src
@Component({
  components: {
    Logo,
  },
})
export default class About extends Vue {}
</script>

