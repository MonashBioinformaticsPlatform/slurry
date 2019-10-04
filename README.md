# slurry

A web accessible tool for looking a Slurm queue and the associated priorities

## Building

Install requirements using conda:

    conda env create -f environment.yml
    conda activate slurry

### Development

I recommend creating some test files for development.  On a machine with slurm
installed, run the following to create test-data files, and copy the resulting
`test-data/*` files to your development machine.

    ./mk-test-data.sh

Build frontend for development, and watch for changes

    (cd app ; ./node_modules/.bin/vue-cli-service build --mode debug --watch)

Run the backend in test mode.  This will read files from `test-data/` rather than accessing slurm

    ./server.py -d


### Deploying

    (cd app ; npm run build) && ./server.py

Note: I recommend against putting this on a publicly webserver as it leaks information such as usernames, and cluster usage.




