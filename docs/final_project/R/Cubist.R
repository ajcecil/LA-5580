#Welcome to Agron 665's Cubist Lab
#
training_data <- read.csv('traingng_data.csv') #replace with training data file


library(caret)

#
t_data <- na.omit(training_data[,c(1,33:52)]) # property to be modeled and range of training data (Remote sensing data and others)
#
dim (t_data)
#
rctrl1 <- trainControl(method = "cv", number = 10, verboseIter = TRUE)
#
cov <- t_data[,2:21]
target <- t_data[,1]
#
grid <- expand.grid(committees = c(1),neighbors = c(0))
#
set.seed(392020)
#
cub1 <- train(x = cov, y = target, method = "cubist", tuneGrid = grid , trControl = rctrl1)
#
cub1
#
summary(cub1)
#
vars <- cub1$vars$used[1:((length(cub1$vars$used)-2))]
capture.output(summary(cub1), file=paste("property_rule.txt"))
