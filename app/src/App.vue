<template>
	<div id="app">
    	<div v-if="loaded">
		    <div id="nav">
		        <router-link to="/running">Running</router-link>
		        <router-link to="/queue">Queue</router-link>
		        <router-link to="/share">Share</router-link>
		        <router-link to="/config">Config</router-link>
		        <router-link to="/about">About</router-link>
		    </div>
			<h1 v-if='priority_flags != "FAIR_TREE"'>PriorityFlags != FAIR_TREE</h1>
		    <router-view />
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

@Component({
    components: {
        Logo,
    },
})
export default class App extends Vue {
    loaded = false
    config = null
    sshare = null
    queue = null
    priority_flags = ""

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
        })
    }

    processQueue(queue) {
        queue.data.forEach((r, idx) => {
            r.id = idx
            for (var key of ["CPUS","NODES","PRIORITY",
                             "sprio.AGE","sprio.FAIRSHARE","sprio.JOBSIZE",
                             "sprio.PARTITION","sprio.QOS"]) {
                r[key] = +r[key]
            }
        })
    }


    mounted () {
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
#nav {
  float: left;
  margin: 0 50px 0 10px;
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
</style>
