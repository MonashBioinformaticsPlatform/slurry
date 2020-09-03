<template>
    <div id="app">
        <div class='flex-grid' v-if="loaded">
            <div id="nav" class='col1'>
                <router-link to="/running">Running</router-link>
                <router-link to="/pending">Pending</router-link>
                <router-link to="/queue">Queue</router-link>
                <router-link to="/share">Share</router-link>
                <router-link to="/config">Config</router-link>
                <router-link to="/qos"><small>QOS/Partitions</small></router-link>
                <router-link to="/about">About</router-link>
                <input id='user-input' text='text' placeholder="user" v-model='myUser'/>
                <prio-legend />
            </div>
            <div class='col2'>
                <router-view />
            </div>
        </div>
        <div v-if="!loaded">
            <h1>Loading...</h1>
            <Logo />
        </div>
      </div>
</template>


<script lang="js">
import { Component, Vue, Watch } from 'vue-property-decorator';
import axios from "axios";
import Logo from '@/components/Logo.vue'; // @ is an alias to /src
import PrioLegend from '@/components/PrioLegend.vue'; // @ is an alias to /src

@Component({
    components: {
        Logo, PrioLegend
    },
})
export default class App extends Vue {
    configLoaded = null
    sshareLoaded = null
    queueLoaded = null
    priority_flags = ""
    myUser = ""

    get loaded() {
        return Object.keys(this.$global.config).length>0 &&
               Object.keys(this.$global.sshare).length>0 &&
               Object.keys(this.$global.queue).length>0
    }

    @Watch('configLoaded')
    processConfig(config) {
        // console.log("qos ", config.qos)
        // console.log("partitions", config.partitions)
        let res_config = config.config.map((r, idx) => {
            let o = {}
            o.id = idx
            o.key = r.key
            o.value = r.value
            if (r.key=='PriorityFlags')
                this.priority_flags = r.value
            return o
        })
        let res_qos = config.qos.map((r,idx) => {
            let o = {}
            o.id = idx
            Object.assign(o,r)
            return o;
        })
        let res_partitions = config.partitions.map((r,idx) => {
            let o = {}
            o.id = idx
            Object.assign(o,r)
            return o;
        })

        this.$global.config =
               {config: res_config,
                partitions: res_partitions,
                qos: res_qos,
                updated: config.updated
                };
    }

    @Watch('sshareLoaded')
    processShare(share) {
        let parents = []
        let last_o = null
        let res = share.data.map((r, idx) => {
            let o = {}
            Object.assign(o, r)
            o.id = idx

            // Fill in fields to represent the tree structure
            let lvl = o.Account.match(/^\s*/)[0].length
            o.Account = o.Account.substr(lvl)
            if (lvl>parents.length)
                parents.unshift(last_o)
            while (lvl < parents.length)
                parents.shift()
            o._parent = lvl==0 ? null : parents[0]
            o._indent = lvl
            o._collapsed = lvl>0
            o._leaf = true
            if (o._parent !== null)
                o._parent._leaf = false

            // Create numeric columns as appropriate
            for (let key of ["RawShares","NormShares","RawUsage","NormUsage",
                             "EffectvUsage","FairShare", 'LevelFS']) {
                if (o[key] == 'inf')
                    o[key] = Number.POSITIVE_INFINITY
                else
                    o[key] = +o[key]
            }
            last_o = o
            return o
        })
        this.$global.sshare = {data: res, updated: share.updated}
    }

    @Watch('queueLoaded')
    processQueue(queue) {
        let res = queue.data.map((r, idx) => {
            let o = {}
            Object.assign(o, r)
            o.id = idx
            // Rename some columns
            for (let [newKey, oldKey] of Object.entries({CPUS: "NumCPUs",
                                                         NODES: "NumNodes",
                                                         USER: "UserId",
                                                         JOBID: "JobId",
                                                         STATE: "JobState",
                                                         PARTITION: "Partition",
                                                         PRIORITY:"Priority"})) {
                o[newKey] = o[oldKey]
                delete o[oldKey]
            }
            o.PARTITION_LIST = o.PARTITION.split(',')
            o.USER = o.USER.replace(/\(.*/, '')
            // Create numeric columns as appropriate
            for (let key of ["CPUS","PRIORITY",
                             "sprio.AGE","sprio.FAIRSHARE","sprio.JOBSIZE",
                             "sprio.PARTITION","sprio.QOS"]) {
                o[key] = +o[key]
            }
            o.NODES = parseInt(o.NODES)

            o['NodeList(Reason)'] = r.NodeList=='(null)' ? `(${r.Reason})` : r.NodeList
            return o
        })
        this.$global.queue = {data: res, updated: queue.updated}
    }

    @Watch('myUser')
    saveMyUser() {
        this.$global.myUser = this.myUser
        localStorage.setItem('myUser', this.myUser)
    }

    // We don't refresh config, it won't change anyway.  TODO - it probably will occasionally
    refresh() {
        let sshare = axios.get("/api/slurm/sshare")
        let queue = axios.get("/api/slurm/queue")
        Promise.all([sshare,queue]).then((values) => {
            this.sshareLoaded = values[0].data
            this.queueLoaded  = values[1].data
        })

    }

    mounted () {
        if (localStorage.myUser) {
            this.myUser = localStorage.getItem('myUser')
        }
        this.$eventBus.$on('refresh', this.refresh)

        let config = axios.get("/api/slurm/config")
        let sshare = axios.get("/api/slurm/sshare")
        let queue = axios.get("/api/slurm/queue")
        Promise.all([config,sshare,queue]).then((values) => {
            this.configLoaded = values[0].data
            this.sshareLoaded = values[1].data
            this.queueLoaded  = values[2].data
        })
    }

}
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
/* #nav {
  float: left;
  margin: 0 50px 0 10px;
} */
.flex-grid {
    display: flex;
}
.col1 {
    flex: 0;
}
.col2 {
    flex: 1;
}

#nav a {
  font-size: 18pt;
  font-weight: bold;
  color: #2c3e50;
  display: block;
  text-align: left;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

#user-input {
    margin-top: 30px;
}
</style>
