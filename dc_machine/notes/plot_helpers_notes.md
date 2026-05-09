# Plot Helper Notes

This note captures initial ideas for plotting helpers to address after the first
nonlinear API implementation is complete.

## Goal

Add optional plotting helpers for common DC-machine characteristic curves so a
user can visualize the machine behavior after solving operating points.

Plotting is intentionally kept separate from the first nonlinear API iteration.
The nonlinear operating-point helpers should be stable first, and plotting can
then build on top of those helpers.

## DC Motor: Standard Plot

The most common plot for a DC motor is:

- torque on the x-axis
- speed on the y-axis

This is the standard torque-speed characteristic.

Other useful motor plots later could include:

- armature current vs torque
- efficiency vs output power
- terminal voltage vs speed for fixed excitation

## DC Generator: Standard Plots

For a DC generator, the most relevant first plots are:

1. terminal voltage vs load current
- probably the best first plotting helper for the generator
- useful at fixed speed and fixed excitation
- shows the effect of armature drop and armature reaction

2. terminal voltage vs field current
- useful at fixed speed
- similar to a loaded excitation characteristic

3. OCC / magnetization curve
- induced emf vs field current
- already foundational and can be reused directly from existing OCC data

## Most Relevant Generator Plot For Nonlinear Analysis

For the first nonlinear generator exercises, the most useful plot is:

- load current on the x-axis
- terminal voltage on the y-axis

This can clearly show:

- the compensated case
- the uncompensated case
- the effect of armature-reaction MMF

It is especially relevant for textbook exercises that compare:

- loaded voltage with compensating windings
- loaded voltage without compensating windings

## Suggested Future Helper Direction

After the nonlinear API is implemented, add plotting helpers that operate on
already computed machine quantities instead of embedding solver logic into the
plot function itself.

Good direction:

- plot helpers receive arrays of already computed values
- or receive a machine object plus a sweep variable and internally call stable
  public helpers

This keeps plotting as a thin visualization layer.

## Recommended First Plot Helper To Implement Later

Start with a generator terminal characteristic helper:

- terminal voltage vs armature current at fixed speed and fixed excitation

Then add a motor torque-speed helper after that.
