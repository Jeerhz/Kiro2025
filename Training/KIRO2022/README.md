# KIRO 2022

### We train on the KIRO 2022 session

julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. examples/run_example.jl ./intances/tiny.json output.json
