<template>
    <div id="app">
        <div class='flex-grid' v-if="loaded">
            <div id="nav" class='col1'>
                <router-link to="/running">Running</router-link>
                <router-link to="/pending">Pending</router-link>
                <router-link to="/queue">Queue</router-link>
                <router-link to="/share">Share</router-link>
                <router-link to="/config">Config</router-link>
                <router-link to="/about">About</router-link>
                <input id='user-input' text='text' placeholder="user" v-model='myUser'/>
                <prio-legend />
            </div>
            <div class='col2'>
                <h1 v-if='priority_flags != "FAIR_TREE"'>PriorityFlags != FAIR_TREE</h1>
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
    loaded = false
    config = null
    sshare = null
    queue = null
    priority_flags = ""
    myUser = ""

    checkLoaded() {
        if (this.config && this.sshare && this.queue) {
            this.processConfig(this.config)
            this.processQueue(this.queue)
            this.processShare(this.sshare)

            this.$global.config = this.config
            this.$global.sshare = this.sshare
            this.$global.queue = this.queue
            this.loaded = true
        }
    }

    processConfig(config) {
        config.data.forEach((r, idx) => {
            r.id = idx
            if (r.key=='PriorityFlags')
                this.priority_flags = r.value
        })
    }

    processShare(share) {
        let parents = []
        share.data.forEach((r, idx) => {
            r.id = idx

            // Fill in fields to represent the tree structure
            let lvl = r.Account.match(/^\s*/)[0].length
            r.Account = r.Account.substr(lvl)
            if (lvl>parents.length)
                parents.unshift(idx-1)
            while (lvl < parents.length)
                parents.shift()
            r._parent = lvl==0 ? null : parents[0]
            r._indent = lvl
            r._collapsed = lvl>0
            r._leaf = true
            if (r._parent !== null)
              share.data[r._parent]._leaf = false

            // Create numeric columns as appropriate
            for (var key of ["RawShares","NormShares","RawUsage","NormUsage",
                             "EffectvUsage","FairShare", 'LevelFS']) {
                if (r[key] == 'inf')
                    r[key] = Number.POSITIVE_INFINITY
                else
                    r[key] = +r[key]
            }
        })
    }

    processQueue(queue) {
        queue.data.forEach((r, idx) => {
            r.id = idx
            // Rename some columns
            for (let [newKey, oldKey] of Object.entries({CPUS: "NumCPUs",
                                                         NODES: "NumNodes",
                                                         USER: "UserId",
                                                         JOBID: "JobId",
                                                         STATE: "JobState",
                                                         PARTITION: "Partition",
                                                         PRIORITY:"Priority"})) {
                r[newKey] = r[oldKey]
                delete r[oldKey]
            }
            r.USER = r.USER.replace(/\(.*/, '')
            // Create numeric columns as appropriate
            for (var key of ["CPUS","PRIORITY",
                             "sprio.AGE","sprio.FAIRSHARE","sprio.JOBSIZE",
                             "sprio.PARTITION","sprio.QOS"]) {
                r[key] = +r[key]
            }
            r.NODES = parseInt(r.NODES)

            r['NodeList(Reason)'] = r.NodeList=='(null)' ? `(${r.Reason})` : r.NodeList
        })
    }

    @Watch('myUser')
    saveMyUser() {
        this.$global.myUser = this.myUser
        localStorage.setItem('myUser', this.myUser)
    }

    mounted () {
        if (localStorage.myUser) {
            this.myUser = localStorage.getItem('myUser')
        }

        axios.get("/api/slurm/config")
                .then(response => { this.config = response.data; this.checkLoaded() })
        axios.get("/api/slurm/sshare")
                .then(response => { this.sshare = response.data; this.checkLoaded() })
        axios.get("/api/slurm/queue")
                .then(response => { this.queue = response.data; this.checkLoaded() })
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
