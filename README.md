# nba_simulation

Abstract
Target The target of this project was to produce player lines for each of the following attributes:

- Points
- 3 Pointers
- Assists
- Rebounds
- Steals
- Blocks

The lines projected were 0.5 over under lines, meaning there was a 50% chance a player score more or less than that number

 Methodology
The main methodology used was Monte Carlo simulations. This was to take into account the degree of randomness in predicting game outcomes. The output is two csv's including all game lines for all players. One for home, and one for away.

 Critics
This generally worked well for those metrics with higher values (Points, 3 pointers) but far less effectively for metrics with much lower values, such as blocks. Further work should be done to evaluate how accurate the model is at predicting these.

Some of the data provided was not used, and could certainly have proved useful. This is addressed at the end, dicusing future work.
Monte Carlo simulation to build player game lines

Original notebook is in Version1, titled NBA_player_lines

Please contact me for any reason at carterbouley@gmail.com.
