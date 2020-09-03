<template>
    <div class="home">
        <datetime :datetime="dt" :refresh="false"/>
        <h1>Config</h1>
        <div class='slim-container'>
            <slim-grid :data="config"
                       :downloadable="false"
                       :column-options="columns"
                       ></slim-grid>
        </div>
    </div>
</template>

<script lang="js">
import { Component, Vue, Watch } from 'vue-property-decorator';
import SlimGrid from 'vue-slimgrid';
import datetime from '@/components/datetime.vue';


@Component({
    components: {
        SlimGrid,datetime
    },
})
export default class Config extends Vue {
    columns = {
        'key' : {
            order: 0,
            width: 300,
            cssClass: 'left',
        },
        'value' : {
            order: 1,
            width: 200,
            cssClass: 'left',
        },
    }

    get config () {
        return this.$global.config.config
    }

    get dt () {
        return new Date(this.$global.config.updated)
    }
}
</script>

<style src="vue-slimgrid/dist/slimgrid.css"></style>
<style scoped>
div >>> .left {
  text-align: left;
}
div >>> .slim-container {
    width: 520px;
}

</style>