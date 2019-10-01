import * as d3 from "d3";



let weights =[["PriorityWeightAge","sprio.AGE"],
              ["PriorityWeightFairShare","sprio.FAIRSHARE"],
              ["PriorityWeightJobSize","sprio.JOBSIZE"],
              ["PriorityWeightPartition","sprio.PARTITION"],
              ["PriorityWeightQOS","sprio.QOS"]]
              //["PriorityWeightTRES","sprio.TRES"]]

let colourScale = d3.scaleOrdinal(d3.schemeSet2)
                    .domain(['Unknown'].concat(weights).map(x => x[1]))

export { weights, colourScale }

