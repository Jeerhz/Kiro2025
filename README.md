# Kiro2025

Operations Research Competition organized by the CERMICS laboratory and the company Califrais.

# Pre-requirements

The programming languages used are `Julia` and `Python`.

Please install the programming languages before anything else.

- Install version 3.14 of `Python` from [here](https://www.python.org/downloads/).
- Install the latest TLS version (June 2025) of `Julia` from [here](https://julialang.org/downloads/).

For `Python`, we will likely use `uv`, as it is the fastest package manager I know for Python and has great features. Please install it from [here](https://uv.github.io/).

We may need an optimization solver for the project (or not). The fastest one I know is Gurobi. You can get an academic license [here](https://www.gurobi.com/academia/academic-program-and-licenses/).
The process is non-trivial, and you will need to connect to a school network (eduroam) to install the license on your machine.

# Install Dependencies

Do not waste time—please initialize the Python project with:

```bash
uv venv .venv
uv run <python_script.py>
```

This will install heavy dependencies such as `torch`, so please do it before the Hackathon starts.

Go to the Julia project folder and run:

```bash
julia --project=. -e 'import Pkg; Pkg.instantiate()'
```

This will install all the dependencies listed in the `Project.toml` file.

To run a Julia script, please run inside the Julia project folder:

```bash
julia --project=. <relative_path_to_julia_script.jl> <args>
```

# Plan for the Hackathon

You can find previous KIRO subjects [here](https://kiro.enpc.org).
You can navigate to the Califrais website [here](https://www.califrais.fr/).

Califrais articles mainly focus on stock management of perishable products, with recent work on online policy selection, which you can find [here](https://arxiv.org/html/2411.19269v1).
The type of data we can work with should look like the M5 Walmart Dataset, which they often use and cite. Reference [here](https://www.kaggle.com/competitions/m5-forecasting-accuracy).

It is a good idea to look at state-of-the-art algorithms that have won time-forecasting Kaggle competitions (often DirRec with XGBoost or LightGBM). We will try to implement this later with `Python`.

Since this aligns with Califrais’ work, and as a "sure and clear" method, it is a good idea to first implement a gradient descent algorithm.

The first plan is then to implement in `Julia`:

1. Parse the input files.

- We are given instances of different sizes to run our code. The priority is to have something functional.
- We may sort data by time, handle missing values, create basic features like lags or rolling averages.

2. Create a function to calculate the cost of a solution.

   - This function takes a solution and compute the loss.

3. Create a function to generate one or more feasible solutions.

4. Create functions to explore neighborhoods.

5. Optimize using neighborhood descent.

The second plan is to implement in `Python`:

1. Preprocessing

- Load and sort data chronologically.
- Fill missing values via simple forward-fill or interpolation.
- Generate minimal features: day of week, month, lag features (1, 7 days), rolling mean/std (7 days).

2. Training

- Use a fast, robust model: LightGBM or XGBoost with default parameters.
- Use a single time-series split for validation (TimeSeriesSplit) to avoid future leakage.
