# -*- coding: utf-8 -*-
"""sales-price-bulldozers.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1z-KTVMeIdn4-IDvYT4OZtdllb9OHJyOJ
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

print('pd version:', pd.__version__) 
print('np version:', np.__version__)

from google.colab import drive
drive.mount('/content/drive')

# !unzip "drive/MyDrive/sales-price-bulldozers/bluebook-for-bulldozers.zip" -d "drive/MyDrive/sales-price-bulldozers/"

df = pd.read_csv("drive/MyDrive/sales-price-bulldozers/bluebook-for-bulldozers/TrainAndValid.csv")

df.info()

fig, ax = plt.subplots()
ax.scatter(df["saledate"][:1000], df["SalePrice"][:1000])

df.SalePrice.plot.hist()

"""## Parsing dates

When working with time series data, it's a good idea to make sure any date data is the format of a [datetime object](https://docs.python.org/3/library/datetime.html) (a Python data type which encodes specific information about dates).
"""

df = pd.read_csv("drive/MyDrive/sales-price-bulldozers/bluebook-for-bulldozers/TrainAndValid.csv",
                 low_memory=False,
                 parse_dates=["saledate"])

# check dtype of saledate
df.info()

fig, ax = plt.subplots()
ax.scatter(df["saledate"][:1000], df["SalePrice"][:1000])

df

df.head().T

df.saledate.head(20)

"""## Sort DataFrame by saledate 

As we're working on a time series problem and trying to predict future examples given past examples, it makes sense to sort our data by date.
"""

df.sort_values(by =["saledate"], inplace = True, ascending = True)

df.saledate.head(20)

"""### Make a copy of the original DataFrame
Since we're going to be manipulating the data, we'll make a copy of the original DataFrame and perform our changes there.

This will keep the original DataFrame in tact if we need it again.
"""

# Make a copy of the original DataFrame to perform edits on
df_tmp=df.copy()

"""Add datetime parameters for saledate column
Why?

So we can enrich our dataset with as much information as possible.

Because we imported the data using `read_csv()` and we asked pandas to parse the dates using `parse_dates=["saledate"]`, we can now access the [different datetime attributes](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html) of the `saledate` column.
"""

# Add datetime params for saledate
df_tmp["saleYear"] = df_tmp.saledate.dt.year
df_tmp["saleMonth"]=df_tmp.saledate.dt.month
df_tmp["saleDay"]=df_tmp.saledate.dt.day
df_tmp["saleDayofweek"]= df_tmp.saledate.dt.dayofweek
df_tmp['saleDayofyear']=df_tmp.saledate.dt.dayofyear

# drop original saledate
df_tmp.drop("saledate", axis=1, inplace=True)

df_tmp.head().T

# cheeck value counts of state columns
df_tmp["state"].value_counts()

"""## Modeling

"""

# check data info 
df_tmp.info()

# check for missing
df_tmp.isnull().sum()

"""### Convert strings to categories
One way to help turn all of our data into numbers is to convert the columns with the string datatype into a category datatype.

To do this we can use the `pandas types API` which allows us to interact and manipulate the types of data.
"""

pd.api.types.is_string_dtype(df_tmp["UsageBand"])

# these columns contain strings
for column, content in df_tmp.items():
  if pd.api.types.is_string_dtype(content):
    print(column)

# turn all string values to categorical values
for column, content in df_tmp.items():
  if pd.api.types.is_string_dtype(content):
    df_tmp[column]=content.astype('category').cat.as_ordered()

df_tmp.info()

df_tmp["state"].cat.categories

df_tmp["state"].cat.codes

df_tmp.isnull().sum()

"""## Save Processed Data"""

df_tmp.to_csv("drive/MyDrive/sales-price-bulldozers/bluebook-for-bulldozers/train_tmp.csv",
              index=False)

# import the dayta
df_tmp=pd.read_csv("drive/MyDrive/sales-price-bulldozers/bluebook-for-bulldozers/train_tmp.csv",
                   low_memory=False)

df_tmp.head().T

"""# Fill missing values

From our experience with machine learning models. We know two things:

1. All of our data has to be numerical
2. There can't be any missing values

And as we've seen using `df_tmp.isna().sum()` our data still has plenty of missing values.

Let's fill them.

## Filling numerical values first
We're going to fill any column with missing values with the median of that column.
"""

for column, content in df_tmp.items():
  if pd.api.types.is_numeric_dtype(content):
    print(column)

# check the num column that has isnull()

for column, content in df_tmp.items():
  if pd.api.types.is_numeric_dtype(content):
    if pd.isnull(content).sum():
      print(column)

# fill the numeric rows with median
for column, content in df_tmp.items():
  if pd.api.types.is_numeric_dtype(content):
    if pd.isnull(content).sum():
      # add a binary column which tells the data was missing or not
      df_tmp[column+'_is_missing']= pd.isnull(content)
      # fill the missing numeric val with median since it is more robust than mean
      df_tmp[column]=content.fillna(content.median())

"""Why add a binary column indicating whether the data was missing or not?

We can easily fill all of the missing numeric values in our dataset with the median. However, a numeric value may be missing for a reason. In other words, absence of evidence may be evidence of absence. Adding a binary column which indicates whether the value was missing or not helps to retain this information.
"""

# check is null still in numeric columns
for column, content in df_tmp.items():
  if pd.api.types.is_numeric_dtype(content):
    if pd.isnull(content).sum():
      print(column)

# using auctioneerID check out how many where missing
df_tmp["auctioneerID_is_missing"].value_counts()

"""### Filling and turning categorical variables to numbers
Now we've filled the numeric values, we'll do the same with the categorical values at the same time as turning them into numbers.
"""

for column, content in df_tmp.items():
  if not pd.api.types.is_numeric_dtype(content):
    print(column)

# turn cat barables into numbers
for column, content in df_tmp.items():
  if not pd.api.types.is_numeric_dtype(content):
    # add binary col for missing value
    df_tmp[column+"_is_missing"]= pd.isnull(content)
    # add +1 coss pandas encodes missing categories as -1
    df_tmp[column]= pd.Categorical(content).codes+1

df_tmp.info()

df_tmp.isnull().sum()

df_tmp.head().T

df_tmp.head()

"""### Splitting data into train/valid sets

According to the [Kaggle data page](https://www.kaggle.com/c/bluebook-for-bulldozers/data), the validation set and test set are split according to dates.

This makes sense since we're working on a time series problem.

E.g. using past events to try and predict future events.

Knowing this, randomly splitting our data into train and test sets using something like `train_test_split()` wouldn't work.

Instead, we split our data into training, validation and test sets using the date each sample occured.

In our case:

* Training = all samples up until 2011
* Valid = all samples form January 1, 2012 - April 30, 2012
* Test = all samples from May 1, 2012 - November 2012

For more on making good training, validation and test sets, check out the post [How (and why) to create a good validation set](https://www.fast.ai/posts/2017-11-13-validation-sets.html) by Rachel Thomas.
"""

df_tmp["saleYear"].value_counts()

# split data into training and validation
df_val = df_tmp[df_tmp.saleYear == 2012]
df_train = df_tmp[df_tmp.saleYear != 2012]

len(df_val), len(df_train)

# split data into X&y

X_train, y_train = df_train.drop("SalePrice", axis =1), df_train['SalePrice']
X_val, y_val = df_val.drop("SalePrice", axis=1), df_val["SalePrice"]

X_train.shape, y_train.shape, X_val.shape, y_val.shape

"""### Building an evaluation function

According to Kaggle for the Bluebook for Bulldozers competition, [the evaluation function](https://www.kaggle.com/c/bluebook-for-bulldozers/overview/evaluation) they use is root mean squared log error (RMSLE).

RMSLE = generally you don't care as much if you're off by $10 as much as you'd care if you were off by 10%, you care more about ratios rather than differences. MAE (mean absolute error) is more about exact differences.

It's important to understand the evaluation metric you're going for.

Since Scikit-Learn doesn't have a function built-in for RMSLE, we'll create our own.

We can do this by taking the square root of Scikit-Learn's [mean_squared_log_error](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_squared_log_error.html#sklearn.metrics.mean_squared_log_error) (MSLE). MSLE is the same as taking the log of mean squared error (MSE).

We'll also calculate the MAE and R^2 for fun.
"""

# create evaluation funtion( the compoetition uses root MSLE)
from sklearn.metrics import mean_squared_log_error, mean_absolute_error

def rmsle(y_test, y_preds):
  return np.sqrt(mean_squared_log_error(y_test, y_preds))

# create funct tp evaluate model
def show_scores(model):
  train_preds = model.predict(X_train)
  val_preds = model.predict(X_val)
  scores = {
            "Training MAE": mean_absolute_error(y_train, train_preds),
            "Validation MAE": mean_absolute_error(y_val, val_preds),
            "Training RMSLE": rmsle(y_train, train_preds),
            "Validation RMSLE": rmsle(y_val, val_preds),
            "Training R^2": model.score(X_train, y_train),
            "Validatin R^2": model.score(X_val, y_val)
          }
  return scores

from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor()

# Commented out IPython magic to ensure Python compatibility.
# %%time
# # training on training data
# model.fit(X_train, y_train)
# show_scores(model)

"""### Hyperparameter tuning with RandomizedSearchCV"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# from sklearn.model_selection import RandomizedSearchCV
# 
# rf_grid = {
#             "n_estimators": np.arange(10,100,10),
#             "max_depth": [None, 3,5,10],
#             "min_samples_split": np.arange(2,20,2),
#             "min_samples_leaf": np.arange(1,20,2),
#             "max_features": [0.5,1, "sqrt", "auto"],
#           }
# 
# rs_model = RandomizedSearchCV(
#                               RandomForestRegressor(),
#                               param_distributions=rf_grid,
#                               n_iter=20,
#                               cv=5,
#                               verbose=True
#                             )
# 
# rs_model.fit(X_train, y_train)

# Find the best parameters from the RandomizedSearch 
rs_model.best_params_

# Evaluate the RandomizedSearch model
show_scores(rs_model)

"""### Train a model with the best parameters
In a model I prepared earlier, I tried 100 different combinations of hyperparameters (setting `n_iter` to 100 in `RandomizedSearchCV`) and found the best results came from the ones you see below. 

We'll instantiate a new model with these discovered hyperparameters and reset the `max_samples` back to its original value.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# ideal_model = RandomForestRegressor(
#                                       n_estimators=60,
#                                       min_samples_leaf=3,
#                                       min_samples_split=14,
#                                       max_features=0.5,
#                                       n_jobs=-1,
#                                       max_samples=None
#                                     )
# 
# ideal_model.fit(X_train, y_train)

show_scores(ideal_model)

"""
###Make predictions on test data
Now we've got a trained model, it's time to make predictions on the test data.

Remember what we've done.

Our model is trained on data prior to 2011. However, the test data is from May 1 2012 to November 2012.

So what we're doing is trying to use the patterns our model has learned in the training data to predict the sale price of a Bulldozer with characteristics it's never seen before but are assumed to be similar to that of those in the training data."""

df_test = pd.read_csv('drive/MyDrive/sales-price-bulldozers/bluebook-for-bulldozers/Test.csv',
                      parse_dates=["saledate"])
df_test.head()

"""### Preprocessing the test data 
Our model has been trained on data formatted in the same way as the training data.

This means in order to make predictions on the test data, we need to take the same steps we used to preprocess the training data to preprocess the test data.

Remember: Whatever you do to the training data, you have to do to the test data.

Let's create a function for doing so (by copying the preprocessing steps we used above).
"""

def preprocess_data(df):
  # add datetime params for saledate
  df['saleYear'] = df.saledate.dt.year
  df["saleMonth"] = df.saledate.dt.month
  df["saleDay"]  = df.saledate.dt.day
  df["saleDayofweek"] = df.saledate.dt.dayofweek
  df["saleDayofyear"] = df.saledate.dt.dayofyear

  # drop original saledate
  df.drop("saledate", axis = 1, inplace = True)
  
  # fil numeric rows with median
  for column, content in df.items():
    if pd.api.types.is_numeric_dtype(content):
      if pd.isnull(content).sum():
        df[column+"_is_missing"] = pd.isnull(content)
        df[column] = content.fillna(content.median())

    # turn categorical variable to numerical
    if not pd.api.types.is_numeric_dtype(content):
      df[column+"_is_missing"]=pd.isnull(content)
      # add +1 because pandaas encodes missing categories as -1
      df[column]= pd.Categorical(content).codes+1
  
  return df

df_test = preprocess_data(df_test)
df_test.head()

df_test.head().T

X_train.head().T

X_val.head().T

# We can find how the columns differ using sets
set(X_train.columns) - set(df_test.columns)

"""In this case, it's because the test dataset wasn't missing any `auctioneerID` fields.

To fix it, we'll add a column to the test dataset called `auctioneerID_is_missing` and fill it with `False`, since none of the `auctioneerID` fields are missing in the test dataset.
"""

# match the test dataset column with train dataset
df_test["auctioneerID_is_missing"] = False

df_test.head().T

# Make predictions on the test dataset using the best model
test_preds = ideal_model.predict(df_test)

"""When looking at the [Kaggle submission requirements](https://www.kaggle.com/c/bluebook-for-bulldozers/overview/evaluation), we see that if we wanted to make a submission, the data is required to be in a certain format. Namely, a DataFrame containing the SalesID and the predicted SalePrice of the bulldozer.

Let's make it.
"""

df_preds = pd.DataFrame()
df_preds["SalesID"] = df_test["SalesID"]
df_preds["SalePrice"] = test_preds
df_preds

# export to csv
df_preds.to_csv("drive/MyDrive/sales-price-bulldozers/bluebook-for-bulldozers/predictions.csv",
                index = False)

import datetime
import os

def save_model( model, suffix=None):
  """
  Saves a given model in a models directory and appends a suffix (str)
  for clarity and reuse.
  """
  # import pickle for saving randomforestregrssi model
  import pickle

  # Create model directory with current time
  modeldir = os.path.join("drive/MyDrive/sales-price-bulldozers/models",
                          datetime.datetime.now().strftime("%Y%m%d-%H%M%s"))
  model_path =  modeldir + "-" + suffix + ".pkl" # save format of model
  print(f"Saving model to: {model_path}...")
  pickle.dump(model, open(model_path, "wb"))
  return model_path

def load_model(model_path):
  """
  Loads a saved model from a specified path.
  """
  import pickle
  print(f"Loading saved model from: {model_path}")
  pickle.load(open(model_path, "rb"))
  
  return model

save_model(ideal_model, suffix ="-by-sasumwen")

ld = load_model("/content/drive/MyDrive/sales-price-bulldozers/models/20230209-19201675970402--by-sasumwen.pkl")

ld.score(X_val, y_val)

ld.score(X_train, y_train)

