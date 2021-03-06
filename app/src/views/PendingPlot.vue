<template>
    <div class="home">
        <datetime :datetime="dt"/>
        <h1>Pending</h1>

        <div class='slider'>
            <label for="size">Size</label>
            <input name="size" type="range" min="1" max="15" v-model:value='sizeSlider' />
        </div>

        <span>
            State: {{state}}.
            Reason:
                <select v-model='reason'>
                    <option value='priority'>Priority</option>
                    <option value='any'>Any</option>
                </select>
            Partition:
                <select v-model='partition'>
                    <option v-for="p in partitions" :key="p.name" :value='p.name'>{{p.label}}</option>
                </select>
            Num entries : {{queue.length}}
        </span>

        <div v-show='rendering>0'>
            <h2>Rendering...</h2>
            <Logo size='10%' style='margin-top:0%' />
        </div>
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
import Logo from '@/components/Logo.vue'
import * as Prio from '@/assets/prio-weights'

@Component({
    components: {
        SlimGrid,datetime,Logo
    },
})
export default class PendingPlot extends Vue {
    sizeSlider = 1
    styleTip = null
    textTip = []
    state = "PENDING"
    partition = "comp"
    reason = 'priority'
    rendering=0

    @Watch('sizeSlider')
    onSliderChange() {
        d3.select("svg",this.$el)
           .attr('height',this.sizeSlider*this.queue.length)
        localStorage.setItem('sizeSlider', this.sizeSlider)
    }

    process_row(row, idx) {
        let last_prio=0
        let res = Prio.weights.map(w => {
            let prio = row[w[1]]
            let r = { type: w[1], idx: idx, prio1: last_prio, prio: prio }
            last_prio = last_prio + prio
            return r
        })
        return res
    }

    markUser() {
        let markData = this.queue.map((row,idx) => { return {row:row, idx:idx} })
                                 .filter(x => this.highlight(x.row))
        let marks = d3.select("svg",this.$el)
                      .selectAll("g.user")
                      .data(markData, x => x.idx)
        marks.exit().remove()
        let newMarks = marks.enter()
                            .append("g")
                            .attr("class","user")
        newMarks.append("rect")
               .attr("class", "user")
               .attr("x", x => 0)
               .attr("width", x => 10)
               .attr("y", x => 10*x.idx)
               .attr("height", x => 10)
               .attr("fill", "black")
        newMarks.append("line")
               .attr("class", "user")
               .attr("x1", x => 0)
               .attr("x2", x => 10)
               .attr("y1", x => 10*x.idx)
               .attr("y2", x => 10*x.idx)
               .attr("stroke", "#ddd")
    }

    renderPlot() {
        this.rendering+=1
       setTimeout(this.renderPlotReal, 10)
    }

    renderPlotReal() {
        let begin = Date.now()
        d3.select("#plot",this.$el).html("")
        let svg = d3.select("#plot",this.$el).append("svg")
        svg.attr("width","95%")
           .attr('height',this.sizeSlider*this.queue.length)
           .attr("preserveAspectRatio","none")
           .attr("viewBox", `0 0 110 ${10*this.queue.length}`)

        let xScale = d3.scaleLinear()
                       .range([0, 100])
                       .domain([0, this.maxPrio])
        let lines = svg.selectAll("g.row")
                       .data(this.queue)
        let newLines = lines.enter()
                            .append("g")
                            .attr("class","row")
        newLines.append("rect")
               .attr("x", x => 10+xScale(0))
               .attr("width", x => xScale(x.PRIORITY))
               .attr("y", (x, i) => 10*i)
               .attr("height", 10)
               .attr("fill", Prio.colourScale("Unknown"))
        newLines.selectAll("line.sub")
              .data((d,idx) => this.process_row(d,idx))
              .enter()
              .append("rect")
               .attr("class","sub")
               .attr("x", x => 10+xScale(x.prio1))
               .attr("width", x => xScale(x.prio))
               .attr("y", (x, i) => 10*x.idx)
               .attr("height", 10)
               .attr("fill", x => Prio.colourScale(x.type))

        newLines.append("line")
               .attr("x1", x => 10+xScale(0))
               .attr("x2", x => 10+xScale(x.PRIORITY))
               .attr("y1", (x, i) => 10*i)
               .attr("y2", (x, i) => 10*i)
               .attr("stroke", "#ddd")

        svg.on('mousemove', () => this.showTip(d3.mouse(svg.node())))
        svg.on('mouseout', this.hideTip)
        this.markUser()
        console.log(`Rendering the queue took ${Date.now()-begin}ms`)
        this.rendering-=1
    }

    highlight(row) {
        return this.$global.myUser && row.USER.includes(this.$global.myUser)
    }

    showTip(loc) {
        let y = Math.floor(loc[1]/10)
        if (y<0)
            y=0
        let row = this.queue[y]
        this.styleTip = {} //left: d3.event.pageX+"px", top: (d3.event.pageY-50)+"px"}
        this.textTip = Prio.weights.map(w => [w[1], row[w[1]]])
        this.textTip.unshift(["Priority", row.PRIORITY])
        this.textTip.unshift(["User", row.USER])
        this.textTip.unshift(["Rank", y + 1])
        this.textTip.push(["CPUs", row.CPUS])
        this.textTip.push(["Time Limit", row.TIME_LIMIT])
        this.textTip.push(["Reason", row.Reason])
    }

    hideTip() {
        this.styleTip = null
    }

    @Watch('queue')
    queueChanged() {
        this.renderPlot()
    }

    @Watch('globalMyUser')
    onUserChange() {
        this.markUser()
    }

    get globalMyUser() {
        return this.$global.myUser
    }

    get config() {
        return this.$global.config.config
    }

    get configAsDict() {
        return Object.fromEntries(this.config.map(x => [x.key,x.value]))
    }

    reasonMatch(job) {
        return (this.reason=='any' || this.reason==job.Reason.toLowerCase())
    }

    get queue () {
        let begin = Date.now()
        let res = this.$global.queue.data.filter(x => x.STATE==this.state &&
                                                      x.PARTITION_LIST.includes(this.partition) &&
                                                      this.reasonMatch(x) &&
                                                      x.PRIORITY>0)
        res.sort((a,b) => b.PRIORITY - a.PRIORITY)
        //console.log("Queue filtering took",Date.now()-begin)
        return res
    }
    get dt () {
        return new Date(this.$global.queue.updated)
    }

    get maxPrio() {
        return Math.max(... this.queue.map(x => x.PRIORITY))
    }

    get partitions() {
        let res = this.$global.config.partitions.map(p => { return {name: p.PartitionName}})
        let counts = {}
        res.forEach(p => { counts[p.name] = 0 })
        this.$global.queue.data.map(x => {
            if (x.STATE==this.state && this.reasonMatch(x) && x.PRIORITY>0) {
                x.PARTITION_LIST.map(p => counts[p] += 1)
            }
        })
        res.forEach(p => {
            let num = counts[p.name] || 0;
            p.count = num
            p.label = `${p.name} : ${num}`
        })
        res.sort((a,b) => b.count - a.count)
        return res;
    }

    mounted() {
        if (localStorage.sizeSlider) {
            this.sizeSlider = localStorage.getItem('sizeSlider')
        }
        this.renderPlot()
    }
}
</script>

<style src="vue-slimgrid/dist/slimgrid.css"></style>
<style scoped>
.slider {
    float:right;
    font-size: 14px;
}
.slider label {
    vertical-align: top;
}

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
