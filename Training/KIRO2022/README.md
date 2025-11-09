# KIRO 2022

We use the data of KIRO 2022 to get used to the format of data and be able to set up fastly Julia environment for 2025 KIRO Hackathon.

### Requirements

1. We use Julia as programming Language to solve optimization problems.
   Please install from (here)[https://julialang.org/downloads/]

2. We may need an optimization solver for the project (or not), the fastest one I know is Gurobi. You can get an academic license (here)[https://www.gurobi.com/academia/academic-program-and-licenses/].
   The process is non trivial and you will need to connect to a school network (eduroam) to install the license on your machine.

### Set up your Julia environment

In the current folder `KIRO2022`, instantiate julia with:

`julia --project=. -e `

Install the dependencies with:
`'using Pkg; Pkg.instantiate()' `

### Running

Run the script to evaluate a solution with:

`julia --project=. examples/run_example.jl ./intances/tiny.json ./results/output.json`

You may change the script to use other instances
