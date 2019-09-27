<template>
  <div class="home">
    <datetime :datetime="dt" />
    <h1>Share</h1>
    <slim-grid ref='slimgrid'
               :data="allRows"
               :downloadable="false"
               :forceSyncScrolling="true"
               :column-options="columns"
               :selection-model='selectionModel'
               @before-init='beforeInit'
               @after-init='afterInit'
               @grid-dbl-click='dblClick'
               @grid-click='click'
               ></slim-grid>
  </div>
</template>

<script lang="js">
import { Component, Vue, Watch } from 'vue-property-decorator';
import SlimGrid from 'vue-slimgrid';
import { Plugins } from "slickgrid-es6";
import datetime from '@/components/datetime.vue';


@Component({
    components: {
        SlimGrid, datetime
    },
})
export default class Share extends Vue {
    selectionModel = new Plugins.RowSelectionModel()

    columns = {
        'Account' : {
            order: 0,
            cssClass: 'left',
            formatter(row, cell, value, cd, dc) {
                let spacer = "<span style='display:inline-block;height:1px;width:" + (15 * dc._indent) + "px'></span>";
                if (dc._leaf) {
                    return spacer + " <span class='toggle'></span>&nbsp;" + value;
                } else {
                    if (dc._collapsed) {
                        return spacer + " <span class='toggle expand'></span>&nbsp;" + value
                    } else {
                        return spacer + " <span class='toggle collapse'></span>&nbsp;" + value
                    }
                }
            }
        },
        'User': {
            order: 1,
        },
        'RawShares': {
            order: 2,
            width: 90,
        },
        'NormShares': {
            order: 3,
        },
        'RawUsage': {
            order: 4,
            cssClass: 'right'
        },
        'NormUsage': {
            order: 5,
        },
        'TRESRunMins': { hidden: true },
        'Partition': { hidden: true },
        'Cluster': { hidden: true},
        'GrpTRESMins': { hidden: true},
        'ID': {hidden: true},
        '_collapsed' : { hidden: true },
        '_parent' : { hidden: true },
        '_indent' : { hidden: true },
        '_leaf' : { hidden: true},
        '*': { order: 20 }
    }

    get allRows () {
        return this.$global.sshare.data
    }
    get dt () {
        return new Date(this.$global.sshare.updated)
    }

    filterRows(item) {
        while (item._parent!==null) {
            item = this.allRows[item._parent]
            if (item._collapsed)
                return false
        }
        return true
    }

    beforeInit(args) {
        // Delete the standard contextmenu handler.  I don't like it since it disables right-click
        delete this.$refs.slimgrid.events.slickGrid.onContextMenu
    }

    afterInit(args) {
        this.$refs.slimgrid.dataView.setFilter(this.filterRows)
    }

    dblClick(e, args) {
        let item = this.$refs.slimgrid.dataView.getItem(args.row);
        item._collapsed = !item._collapsed
        this.$refs.slimgrid.dataView.updateItem(item.id, item);
        e.stopImmediatePropagation()
    }

    click(e, args) {
        if (e.target.classList.contains("toggle")) {
            let item = this.$refs.slimgrid.dataView.getItem(args.row);
            item._collapsed = !item._collapsed
            this.$refs.slimgrid.dataView.updateItem(item.id, item);
        }
        e.stopImmediatePropagation()
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

div >>> .toggle {
    height: 9px;
    width: 9px;
    display: inline-block;
}

div >>> .toggle.expand {
    background: url(/expand.gif) no-repeat center center;
}

div >>> .toggle.collapse {
    background: url(/collapse.gif) no-repeat center center;
}
</style>
