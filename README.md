# Golf-Score-Tracker

This site was made specifically for Bob Pierangeli's PGA Major Pools to calculate your score in real time leverage slashgolf's API, https://slashgolf.dev/quickstart.html. 

You must pick 9 golfers total in the attached excel sheet: 1 from each group (6) and 3 additional who are not listed in the sheet.  

Scoring: 
1. The golfer's score is your score. i.e. if Spieth shoots -10 then your score is -10. 
2.  Earn bonus points if your golfer is in the lead after the round. 
      a. 1st Round: -1
      b. 2nd Round: -2
      c. 3rd Round: -3
      d. Win Tournament: -5
3. Deductions: 
      a. Golfer misses the cut: +10
      b. Golfer scratch/withdrawal/DQ: receives highest score out of all the golfers at the end of tournament +5 additional strokes
4. Tiebreaker 
      a. Goes to the person who has chosen the golfer who finishes the highest after the completion of the tournament.
