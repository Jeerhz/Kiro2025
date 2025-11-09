module Scheduler

using JSON

# -------------------------
# Types
# -------------------------
struct MachineOption
	machine::Int
	operators::Vector{Int}
end

struct Task
	id::Int
	p::Int                   # processing time
	machines::Vector{MachineOption}  # options
end

struct Job
	id::Int
	seq::Vector{Int}         # sequence of task ids
	release::Int
	due::Int
	weight::Float64
end

struct Instance
	nb_jobs::Int
	nb_tasks::Int
	nb_machines::Int
	nb_operators::Int
	alpha::Float64           # unit_penalty (α)
	beta::Float64            # tardiness (β)
	jobs::Dict{Int, Job}
	tasks::Dict{Int, Task}
	task_to_job::Dict{Int, Int}
end

# Solution entry for a single task
struct SolEntry
	task::Int
	start::Int
	machine::Int
	operator::Int
end

const Solution = Vector{SolEntry}

# -------------------------
# Parsing instance JSON
# -------------------------
function parse_instance(path::String)
	txt = read(path, String)
	j = JSON.parse(txt)

	params = j["parameters"]
	size = params["size"]
	costs = params["costs"]

	nb_jobs = size["nb_jobs"]
	nb_tasks = size["nb_tasks"]
	nb_machines = size["nb_machines"]
	nb_operators = size["nb_operators"]
	alpha = costs["unit_penalty"]
	beta = costs["tardiness"]

	jobs = Dict{Int, Job}()
	task_to_job = Dict{Int, Int}()

	for jobdict in j["jobs"]
		jid = jobdict["job"]
		seq = [Int(x) for x in jobdict["sequence"]]
		release = jobdict["release_date"]
		due = jobdict["due_date"]
		weight = jobdict["weight"]
		jobs[jid] = Job(jid, seq, release, due, float(weight))
		for t in seq
			task_to_job[t] = jid
		end
	end

	tasks = Dict{Int, Task}()
	for tdict in j["tasks"]
		tid = tdict["task"]
		p = tdict["processing_time"]
		mopts = MachineOption[]
		for md in tdict["machines"]
			push!(mopts, MachineOption(md["machine"], [Int(x) for x in md["operators"]]))
		end
		tasks[tid] = Task(tid, p, mopts)
	end

	Instance(nb_jobs, nb_tasks, nb_machines, nb_operators, float(alpha), float(beta), jobs, tasks, task_to_job)
end

# -------------------------
# JSON solution I/O
# -------------------------
function write_solution_json(path::String, sol::Solution)
	arr = Any[]
	for e in sol
		push!(arr, Dict(
			"task" => e.task,
			"start" => e.start,
			"machine" => e.machine,
			"operator" => e.operator,
		))
	end
	open(path, "w") do io
		JSON.print(io, arr)
	end
end

function read_solution_json(path::String)
	txt = read(path, String)
	arr = JSON.parse(txt)
	sol = SolEntry[]
	for d in arr
		push!(sol, SolEntry(d["task"], d["start"], d["machine"], d["operator"]))
	end
	return sol
end


# -------------------------
# Helpers: interval utilities
# intervals: Vector of (start,end) with end = exclusive (start..end-1)
# -------------------------
# check if resource is free on [t, t+dur)
function free_at(intervals::Vector{Tuple{Int, Int}}, t::Int, dur::Int)
	s = t;
	e = t + dur
	for (a, b) in intervals
		# overlap if not (b <= s || e <= a)
		if !(b <= s || e <= a)
			return false
		end
	end
	return true
end

# add interval
function add_interval!(intervals::Vector{Tuple{Int, Int}}, t::Int, dur::Int)
	push!(intervals, (t, t + dur))
end

# find earliest t >= start where interval of length dur fits
# naive scan up to horizon
function find_earliest_slot(intervals::Vector{Tuple{Int, Int}}, start::Int, dur::Int, horizon::Int)
	t = start
	while t <= horizon
		if free_at(intervals, t, dur)
			return t
		else
			# advance t by 1 (discrete times). For speed-ups one could jump to the end of conflicting interval.
			t += 1
		end
	end
	return nothing
end

# -------------------------
# Greedy feasible solution builder
# -------------------------
"""
generate_feasible_solution(inst; horizon = nothing, job_order = :by_release)

Greedy heuristic:
- Order jobs (by release date or by weight descending)
- For each job, schedule tasks in sequence, for each task choose (machine,operator) that gives earliest completion >= task earliest start.
Returns Solution (Vector{SolEntry}).
"""
function generate_feasible_solution(inst::Instance; horizon = nothing, job_order = :by_release)
	# horizon default = sum processing + max release
	total_p = sum(t.p for t in values(inst.tasks))
	max_release = maximum(j.release for j in values(inst.jobs))
	horizon = isnothing(horizon) ? max_release + total_p + 50 : horizon

	# intervals for machines and operators
	machine_intervals = Dict(i => Vector{Tuple{Int, Int}}() for i in 1:inst.nb_machines)
	operator_intervals = Dict(i => Vector{Tuple{Int, Int}}() for i in 1:inst.nb_operators)

	# ordering jobs
	jobs_list = collect(values(inst.jobs))
	if job_order == :by_release
		sort!(jobs_list, by = j -> j.release)
	elseif job_order == :by_weight_desc
		sort!(jobs_list, by = j -> -j.weight)
	end

	sol = SolEntry[]

	for job in jobs_list
		earliest = job.release
		for tid in job.seq
			task = inst.tasks[tid]
			chosen = nothing
			chosen_start = typemax(Int)
			# try all machine+operator combos
			for mopt in task.machines
				m = mopt.machine
				for o in mopt.operators
					# find earliest slot for machine and operator individually >= earliest
					t_m = find_earliest_slot(machine_intervals[m], earliest, task.p, horizon)
					t_o = find_earliest_slot(operator_intervals[o], earliest, task.p, horizon)
					if t_m === nothing || t_o === nothing
						continue
					end
					# We need a common time >= earliest where both free for duration.
					# Try starting at candidate = max(t_m, t_o) and scan forward if conflict
					candidate = max(t_m, t_o, earliest)
					# We'll try a small scan to find a common slot
					found = nothing
					tscan = candidate
					while tscan <= horizon
						if free_at(machine_intervals[m], tscan, task.p) && free_at(operator_intervals[o], tscan, task.p)
							found = tscan
							break
						end
						tscan += 1
					end
					if found !== nothing && found < chosen_start
						chosen = (m, o, found)
						chosen_start = found
					end
				end
			end

			if chosen === nothing
				error("Cannot find feasible slot for task $(tid) of job $(job.id) within horizon. Consider increasing horizon.")
			end

			m, o, startt = chosen
			add_interval!(machine_intervals[m], startt, task.p)
			add_interval!(operator_intervals[o], startt, task.p)
			push!(sol, SolEntry(tid, startt, m, o))
			earliest = startt + task.p  # next task earliest = completion
		end
	end

	return sol
end

# -------------------------
# Feasibility checker
# -------------------------
"""
is_feasible(inst, sol)

Checks:
- All tasks present exactly once
- Starts integer >= 0
- Precedence: tasks in job sequence respect completion
- Machine chosen in Mi and operator in Oim
- Resource conflicts: no overlap on same machine or same operator
Returns (Bool, Vector{String}) -> feasible, list of violations
"""
function is_feasible(inst::Instance, sol::Solution)
	errors = String[]
	# map task -> entry
	mapentry = Dict{Int, SolEntry}()
	for e in sol
		if haskey(mapentry, e.task)
			push!(errors, "Task $(e.task) appears more than once.")
		end
		mapentry[e.task] = e
		if e.start < 0
			push!(errors, "Task $(e.task) has negative start $(e.start).")
		end
	end
	# all tasks present?
	for tid in keys(inst.tasks)
		if !haskey(mapentry, tid)
			push!(errors, "Task $(tid) missing from solution.")
		end
	end

	# precedence per job
	for job in values(inst.jobs)
		prev_completion = nothing
		for tid in job.seq
			if !haskey(mapentry, tid)
				continue
			end
			e = mapentry[tid]
			p = inst.tasks[tid].p
			if prev_completion !== nothing
				if e.start < prev_completion
					push!(errors, "Task $(tid) in job $(job.id) starts at $(e.start) < previous completion $(prev_completion).")
				end
			else
				# first task must start >= release
				if e.start < job.release
					push!(errors, "First task $(tid) of job $(job.id) starts at $(e.start) < release $(job.release).")
				end
			end
			prev_completion = e.start + p
		end
	end

	# machine/operator compatibility and resource conflicts
	# build machine->intervals and operator->intervals from sol and check overlaps
	machine_intervals = Dict(i => Vector{Tuple{Int, Int, Int}}() for i in 1:inst.nb_machines) # (start,end,task)
	operator_intervals = Dict(i => Vector{Tuple{Int, Int, Int}}() for i in 1:inst.nb_operators)

	for e in sol
		task = inst.tasks[e.task]
		# check machine compatibility
		allowed = false
		allowed_ops = Int[]
		for mopt in task.machines
			if mopt.machine == e.machine
				allowed = true
				allowed_ops = mopt.operators
				break
			end
		end
		if !allowed
			push!(errors, "Task $(e.task) assigned machine $(e.machine) not in allowed set.")
		else
			if !(e.operator in allowed_ops)
				push!(errors, "Task $(e.task) assigned operator $(e.operator) not allowed on machine $(e.machine).")
			end
		end
		s = e.start
		ed = s + task.p
		push!(machine_intervals[e.machine], (s, ed, e.task))
		push!(operator_intervals[e.operator], (s, ed, e.task))
	end

	# check overlaps
	function check_overlaps(intervals, kind)
		for (_, a) in pairs(intervals)
			# sort by start
			arr = sort(a, by = x->x[1])
			for i in 1:(length(arr)-1)
				(s1, e1, t1) = arr[i]
				(s2, e2, t2) = arr[i+1]
				if e1 > s2 # overlap
					push!(errors, "$(kind) conflict between tasks $(t1) and $(t2) at intervals [$(s1),$(e1)) and [$(s2),$(e2)).")
				end
			end
		end
	end

	check_overlaps(machine_intervals, "Machine")
	check_overlaps(operator_intervals, "Operator")

	return (length(errors) == 0, errors)
end

# -------------------------
# Cost evaluator
# -------------------------
"""
cost(inst, sol)

Computes objective ∑_j wj (Cj + α Uj + β Tj)
Also returns Dicts of Cj, Uj, Tj for inspection.
"""
function cost(inst::Instance, sol::Solution)
	# map task -> start
	startmap = Dict(e.task => e.start for e in sol)
	# compute C_i
	completion = Dict{Int, Int}()
	for (tid, t) in inst.tasks
		if !haskey(startmap, tid)
			error("Task $(tid) missing in solution")
		end
		completion[tid] = startmap[tid] + t.p
	end

	# compute job completion times
	Cj = Dict{Int, Int}()
	Uj = Dict{Int, Int}()
	Tj = Dict{Int, Int}()

	total = 0.0
	for job in values(inst.jobs)
		last_task = job.seq[end]
		cj = completion[last_task]
		Cj[job.id] = cj
		uj = cj > job.due ? 1 : 0
		tj = max(cj - job.due, 0)
		Uj[job.id] = uj
		Tj[job.id] = tj
		total += job.weight * (cj + inst.alpha * uj + inst.beta * tj)
	end

	return (total, Cj, Uj, Tj)
end

# -------------------------
# Convenience example function to run parse->solve->check->cost->write
# -------------------------
function solve_instance_file(inst_path::String; out_path::String = "solution.json", job_order = :by_release)
	inst = parse_instance(inst_path)
	sol = generate_feasible_solution(inst; job_order = job_order)
	feasible, errs = is_feasible(inst, sol)
	if !feasible
		println("Solution not feasible. Errors:")
		for e in errs
			println(" - ", e)
		end
	else
		total, Cj, Uj, Tj = cost(inst, sol)
		println("Feasible solution found. Cost = ", total)
		write_solution_json(out_path, sol)
		println("Solution written to ", out_path)
	end
	return sol
end

end # module
