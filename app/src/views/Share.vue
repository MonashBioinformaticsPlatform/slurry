<template>
  <div class="home">
    <div>
        <datetime :datetime="dt" />
        <a style='clear: right; float:right; font-size: small' target='_blank'
           href='https://slurm.schedmd.com/fair_tree.html#fairshare'>Fair Tree documentation</a>
    </div>
    <h1>Share</h1>
    <slim-grid ref='slimgrid'
               :data="allRows"
               :downloadable="false"
               :forceSyncScrolling="true"
               :column-options="columns"
               :sort="sorter"
               :row-formatter="rowFormatter"
               @before-init='beforeInit'
               @after-init='afterInit'
               @grid-dbl-click='dblClick'
               @grid-click='click'
               @filters-generated='filtersGenerated'
               ></slim-grid>
  </div>
</template>

<script lang="js">
import { Component, Vue, Watch } from 'vue-property-decorator';
import SlimGrid from 'vue-slimgrid';


//import { Plugins } from "slickgrid-es6";
import datetime from '@/components/datetime.vue';


@Component({
    components: {
        SlimGrid, datetime
    },
})
export default class Share extends Vue {
    //selectionModel = new Plugins.RowSelectionModel()
    originalRows = null
    filterCopy = null
    keepIDs = null

    columns = {
        'Account' : {
            order: 0,
            cssClass: 'left',
            headerInput: true,
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
            headerInput: true,
        },
        'RawShares': {
            order: 2,
            width: 100,
            cssClass: 'right monospace',
        },
        'NormShares': {
            order: 3,
            cssClass: 'monospace',
        },
        'RawUsage': {
            order: 4,
            cssClass: 'right monospace',
        },
        'NormUsage': {
            order: 5,
            cssClass: 'monospace',
        },
        'EffectvUsage': {
            order: 6,
            cssClass: 'monospace',
        },
        'FairShare': {
            order: 7,
            cssClass: 'monospace',

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
        '*': { order: 20, headerFilter: false, headerInput: false },
    }

    get allRows () {
        return this.$global.sshare.data
    }
    get dt () {
        return new Date(this.$global.sshare.updated)
    }
    get highlightIDs() {
        if (!this.$global.myUser)
            return {}
        return this.matchingIDs('User', this.$global.myUser)
    }

    matchingIDs(field, value) {
        let res = {}
        this.allRows.forEach(row => {
            if (row[field].includes(value)) {
                // This row matches.  Add it, and all its parents
                res[row.id]=1
                while (row._parent !== null) {
                    row = this.originalRows[row._parent]
                    res[row.id]=1
                }
            }
        })
        return res
    }

    sorter(e,args) {
        const sortCol = args.sortCols[0]
        const sign = sortCol.sortAsc ? 1 : -1
        const field = sortCol.sortCol.field
        args.grid.getData().sort((row1, row2) => {
            let p1 = row1
            let p2 = row2
            while (row1._indent>row2._indent)
                row1 = this.originalRows[row1._parent]
            while (row1._indent<row2._indent)
                row2 = this.originalRows[row2._parent]
            while (row1._parent != row2._parent) {
                row1 = this.originalRows[row1._parent]
                row2 = this.originalRows[row2._parent]
            }
            // row1 and row2 now at the same level, and same parent, compare them.
            let result=0
            if (row1===row2) {   // Original rows have a parent/child relationship.  Child always should be after parent
                result = p1._indent>p2._indent ? 1 : -1
            } else {
                const x = row1[field]
                const y = row2[field]
                result = (x < y ? -1 : x > y ? 1 : 0) * sign;
            }
            return result
        })
    }

    rowFormatter(row) {
        if (row.id in this.highlightIDs) {
            return {cssClasses: 'highlight'}
        } else {
            return null
        }
    }

    // Complicated mess to allow filtering by header input text boxes
    @Watch('filterCopy', { deep: true })
    onFilterChange() {
        // Header filters have changed.  Refilter
        this.keepIDs = null
        for (var columnId in this.filterCopy) {
            if (columnId !== undefined && this.filterCopy[columnId] !== "") {
                var filterVal = this.filterCopy[columnId].toLowerCase()
                var ids = this.matchingIDs(columnId, filterVal)
                if (!this.keepIDs)
                    this.keepIDs = ids
                else {
                    for (let k in this.keepIDs) {
                        if (!(k in ids))
                            delete this.keepIDs[k]
                    }
                }
            }
        }

        this.$refs.slimgrid.dataView.refresh()
    }

    filterRows(item) {
        // First check for any header filters
        if (this.keepIDs && !(item.id in this.keepIDs))
            return false

        // Now check if the row is hidden by "collapsing"
        while (item._parent!==null) {
            item = this.originalRows[item._parent]
            if (item._collapsed)
                return false
        }
        return true
    }

    beforeInit(args) {
        // Delete the standard contextmenu handler.  I don't like it since it disables right-click
        delete this.$refs.slimgrid.events.slickGrid.onContextMenu
        this.originalRows = this.allRows.slice(0)
    }

    afterInit(args) {
        this.$refs.slimgrid.dataView.setFilter(this.filterRows)
    }
2
    filtersGenerated() {
        this.filterCopy = this.$refs.slimgrid.filters
    }

    toggleRow(row) {
        let item = this.$refs.slimgrid.dataView.getItem(row);
        item._collapsed = !item._collapsed
        this.$refs.slimgrid.slickGrid.invalidateAllRows()
        this.$refs.slimgrid.dataView.refresh()
    }

    dblClick(e, args) {
        this.toggleRow(args.row)
        e.stopImmediatePropagation()
    }

    click(e, args) {
        if (e.target.classList.contains("toggle")) {
            this.toggleRow(args.row)
            e.stopImmediatePropagation()
        }
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

div >>> .monospace {
  font-family: monospace;
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

div >>> .highlight {
  background: #bbb;
}

</style>
