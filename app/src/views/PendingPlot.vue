<template>
    <div class="home">
        <datetime :datetime="dt"/>
        <h1>Pending</h1>
        State: {{state}}.  Partition: {{partition}}.  Num entries : {{queue.length}}
        <div id='plot'></div>
        <div class='tip' v-show='styleTip!=null' :style='styleTip'>
            <table>
            <tr v-for='k in textTip'>
                <td class='key'>{{k[0]}}</td>
                <td class='value'>{{k[1]}}</td>
            </tr>
            </table>
        </div>

    </div>
</template>

<script lang="js">
import { Component, Vue, Watch } from 'vue-property-decorator'
import SlimGrid from 'vue-slimgrid'
import * as d3 from "d3"

import datetime from '@/components/datetime.vue'
import * as Prio from '@/assets/prio-weights'

@Component({
    components: {
        SlimGrid,datetime
    },
})
export default class PendingPlot extends Vue {
    styleTip = null
    textTip = []
    state = "PENDING"
    partition = "comp"

    process_row(row, idx) {
        let last_prio=0
        let res = Prio.weights.map(w => {
            let next_prio = last_prio+row[w[1]]
            let r = { type: w[1], idx: idx, prio1: last_prio, prio2: next_prio }
            last_prio = next_prio
            return r
        })
        return res
    }

    renderPlot() {
        d3.select("#plot",this.$el).html("")
        let svg = d3.select("#plot",this.$el).append("svg")
        svg.attr("height", this.queue.length)
           .attr("width", "80%")

        let xScale = d3.scaleLinear()
                       .range([40,svg.node().clientWidth])
                       .domain([0, this.maxPrio])
        let lines = svg.selectAll("g.row")
                       .data(this.queue)
        let newLines = lines.enter()
                            .append("g")
                            .attr("class","row")
        newLines.append("line")
               .attr("x1", x => this.highlight(x) ? 0 : xScale(0))
               .attr("x2", x => xScale(x.PRIORITY))
               .attr("y1", (x, i) => i)
               .attr("y2", (x, i) => i)
               .attr("stroke", Prio.colourScale("Unknown"))
        newLines.selectAll("line.sub")
              .data((d,idx) => this.process_row(d,idx))
              .enter()
              .append("line")
               .attr("class","sub")
               .attr("x1", x => xScale(x.prio1))
               .attr("x2", x => xScale(x.prio2))
               .attr("y1", x => x.idx)
               .attr("y2", x => x.idx)
               .attr("stroke", x => Prio.colourScale(x.type))
        svg.on('mousemove', () => this.showTip(d3.mouse(svg.node())))
        svg.on('mouseout', this.hideTip)
    }

    highlight(row) {
        return this.$global.myUser && row.USER.includes(this.$global.myUser)
    }

    showTip(loc) {
        let y = Math.floor(loc[1])
        if (y<0)
            y=0
        let row = this.queue[y]
        this.styleTip = {} //left: d3.event.pageX+"px", top: (d3.event.pageY-50)+"px"}
        this.textTip = Prio.weights.map(w => [w[1], row[w[1]]])
        this.textTip.unshift(["Priority", row.PRIORITY])
        this.textTip.unshift(["User", row.USER])
        this.textTip.unshift(["Rank", y])
        this.textTip.push(["CPUs", row.CPUS])
        this.textTip.push(["Time Limit", row.TIME_LIMIT])
    }

    hideTip() {
        //this.styleTip = null
    }

    @Watch('queue')
    queueChanged() {
        this.renderPlot()
    }

    get config() {
        return this.$global.config.data
    }

    get configAsDict() {
        return Object.fromEntries(this.config.map(x => [x.key,x.value]))
    }

    get queue () {
        let res = this.$global.queue.data.filter(x => x.STATE==this.state &&
                                                      x.PARTITION==this.partition &&
                                                      x.PRIORITY>0)
        res.sort((a,b) => b.PRIORITY - a.PRIORITY)
        return res
    }
    get dt () {
        return new Date(this.$global.queue.updated)
    }

    get maxPrio() {
        return Math.max(... this.queue.map(x => x.PRIORITY))
    }

    mounted() {
        this.renderPlot()
    }
}
</script>

<style src="vue-slimgrid/dist/slimgrid.css"></style>
<style scoped>
div >>> .right {
    text-align: right;
}
div >>> .priority {
    position: absolute;
    top: 0;
    right: 10px;
    color: black;
}
div >>> .tip {
    position: fixed;
    top: 40px;
    right: 20px;
    border: thin solid black;
    background: #ddd;

    font-size: 10px;
}

div >>> .tip .key {
    font-weight: bold;
    text-align: left;
}
div >>> .tip .value {
    text-align: right;
}
</style>
