<template>
    <div class="home">
        <datetime :datetime="dt"/>
        <h1>QOS</h1>
        <div class='qos-container'>
            <slim-grid :data="qos"
                    :downloadable="false"
                    :explicit-columns="qosColumns"
                    :column-options="columns"
                    ></slim-grid>
        </div>
        <h1>Partitions</h1>
        <div class='partitions-container'>
            <slim-grid :data="partitions"
                       :downloadable="false"
                       :explicit-columns="partitionsColumns"
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
    qosColumns = ["Name","Priority","MaxWall","Preempt","MaxTRESPU"]
    partitionsColumns = ["PartitionName","AllowQos","DefMemPerCPU","DefaultTime","MaxTime","Nodes","QoS","TotalCPUs","TotalNodes","State"]

    columns = {
        'PartitionName' : {
            width: 100,
            cssClass: 'left',
        },
        'DefMemPerCPU' : {
            width: 100,
            cssClass: 'right',
        },
        'TotalCPUs' : {
            width: 80,
            cssClass: 'right',
        },
        'TotalNodes' : {
            width: 80,
            cssClass: 'right',
        },
        'QoS' : {
            width: 80,
        },
        'State' : {
            width: 80,
        },
    }

    get qos () {
        return this.$global.config.qos
    }

    get partitions () {
        return this.$global.config.partitions
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
div >>> .right {
  text-align: right;
}

div >>> .qos-container {
    width: 800px;
}
div >>> .partitions-container {
    width: 1200px;
}
</style>