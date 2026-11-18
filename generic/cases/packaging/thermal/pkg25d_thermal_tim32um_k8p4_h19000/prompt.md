# 2.5D accelerator package -- steady thermal analysis

A logic ASIC and two HBM stacks sit side by side on a silicon interposer, over an
organic substrate and under a lidded thermal path. Heat leaves the compute block
partly straight up through the TIM into the lid and partly sideways through the
interposer -- and the sideways part is what lands on the memory. Find out how hot it gets.

## Geometry

All dimensions in millimetres. In-plane coordinates are measured from the
lower-left corner of the substrate; `x` runs along the 52 mm side.

| part | x | y |
|---|---|---|
| organic substrate | 0 to 52.0 | 0 to 34.0 |
| silicon interposer, and every layer above it | 4.0 to 48.0 | 5.0 to 29.0 |
| west HBM stack | 5.6 to 16.6 | 11.5 to 22.5 |
| logic die | 18.6 to 32.6 | 9.0 to 25.0 |
| east HBM stack | 35.8 to 46.8 | 11.5 to 22.5 |
| compute block inside the logic die | 22.0 to 29.2 | 12.8 to 21.2 |

The stack, bottom to top:

| layer | thickness | material | in-plane extent |
|---|---|---|---|
| organic substrate | 1.200 | laminate | substrate footprint |
| C4 joints and underfill | 0.080 | C4 composite | interposer footprint |
| silicon interposer | 0.100 | silicon | interposer footprint |
| microbumps and underfill | 0.025 | microbump composite | interposer footprint |
| die layer | 0.750 | silicon inside a die footprint, gap filler everywhere else | interposer footprint |
| TIM | 0.032 | TIM | interposer footprint |
| copper lid | 1.500 | copper | interposer footprint |

All three dies are ground to the same 0.750 mm height, so the TIM bond line is
uniform over the whole lid. The bump and underfill layers are already
homogenised into the effective properties below -- model them as continuous
layers, not as discrete joints. Every layer is perfectly bonded to the ones it
touches: all of the resistance in the stack is the bulk material listed below,
and there is no separate interface resistance anywhere.

## Materials

| material | k (W/m/K) |
|---|---|
| organic substrate (laminate) | 22.0 in-plane, 0.65 through-thickness |
| C4 + underfill composite | 0.58 |
| silicon (interposer and all three dies) | 118.0 |
| microbump + underfill composite | 1.35 |
| gap filler | 0.80 |
| TIM | 8.4 |
| copper lid | 385.0 |

## Operating point

| | |
|---|---|
| logic die total power | 265.0 W |
| fraction of it dissipated in the compute block | 0.5 |
| west HBM stack power | 14.2 W |
| east HBM stack power | 11.3 W |
| lid top face | convection to 25 degC at h = 19000 W/m^2/K |
| substrate underside | convection to 25 degC at h = 14.0 W/m^2/K |
| every vertical outer face | adiabatic |

Each die's power is uniform through its own volume: within the logic die,
50% of the total is spread uniformly through the compute block and the
remaining 50% uniformly through the rest of the die. Steady state.

## What to report

| column | quantity | unit |
|---|---|---|
| `t_asic_max_c` | highest temperature anywhere in the logic die | degC |
| `t_hbm_w_max_c` | highest temperature anywhere in the west HBM stack | degC |
| `t_hbm_e_max_c` | highest temperature anywhere in the east HBM stack | degC |

## Output file

`results.csv` in the submission root -- one header row and one data
row:

```
t_asic_max_c,t_hbm_w_max_c,t_hbm_e_max_c
8888.1,8888.2,8888.3
```

Those numbers are placeholders, not a hint at the answer.

How you mesh the stack, which element technology you use and how you drive the
solve are yours to decide.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy, with every piece of
solver output deleted, under a hard limit of **1220 seconds**.
