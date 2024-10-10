# Running the analysis with Snakemake

``` bash
nohup snakemake --cluster "sbatch -A {cluster.account} -q {cluster.qos} -c {cluster.cpus-per-task} -N {cluster.Nodes}  -t {cluster.runtime} --mem {cluster.mem} -J {cluster.jobname} --mail-type={cluster.mail_type} --mail-user={cluster.mail}" --cluster-config cluster.json --jobs 100 --latency-wait 120 &```
