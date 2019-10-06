<template>
    <div class='plot'>
        <h4>Priority Legend</h4>
        <ul>
            <li v-for='w in weights'>
                <span class='box' v-bind:style="w.style"></span>
                {{w.name}}
            </li>
        </ul>
    </div>
</template>
<script lang='js'>
import { Vue, Component, Prop } from 'vue-property-decorator'

import * as Prio from '@/assets/prio-weights'

@Component
export default class PrioLegend extends Vue {
    get weights() {
        return [[0,"Unknown"]].concat(Prio.weights).map(w => {
            return {name: w[1], style: {"background-color": Prio.colourScale(w[1])} }
        })
    }
}
</script>

<style scoped>
.plot {
    margin-top: 50px;
    width: 19ex;
}
ul {
    padding-left: 0;
}
li {
    list-style-type: none;
    text-align: left;
}
span.box {
    display: inline-block;
    width: 10px;
    height: 10px;
}
</style>