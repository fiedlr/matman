# matman
A school project (an analysis of the [MatMat.cz dataset](https://github.com/adaptive-learning/matmat-web/blob/master/data/data_description.md))

**error** = abs(expected - value)

**success rate** (item or student) = number of correct answers / number of all answers

**faker** (student) = average response < general average and success rate > general success rate
**under average** (student) = average response < general average and success rate < general success rate
**over average** (student) = average response > general average and success rate > general success rate

**difficulty** (item) = average error * response median / success rate
