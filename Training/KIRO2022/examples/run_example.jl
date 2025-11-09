# usage:
# julia --project=. examples/run_example.jl path/to/tiny.json
using Pkg
Pkg.activate(joinpath(@__DIR__, ".."))
Pkg.instantiate()

include("../src/Scheduler.jl")
using .Scheduler


if length(ARGS) < 1
	println("Usage: julia --project=. examples/run_example.jl path/to/instance.json [out.json]")
	exit(1)
end

instpath = ARGS[1]
outpath = length(ARGS) >= 2 ? ARGS[2] : "solution_out.json"

# run solver
println("Instance path = ", instpath)

sol = Scheduler.solve_instance_file(instpath; out_path = outpath, job_order = :by_release)
