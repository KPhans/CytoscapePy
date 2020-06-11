import pandas as pd
import numpy as np
from scipy.stats import chi2
import scipy as sp
from sklearn.linear_model import LogisticRegression
from sklearn.utils import resample
from sklearn import preprocessing

dataa= pd.read_excel('data/HRDATA.xlsx')
dataa.info()
dataa.isnull().sum() #zero missing values.

#We group our variables into binomial factors. 4 being High and anything lower being low.

dataa.loc[dataa['PerformanceRating'] > 3, 'PerformanceRating'] = 1
dataa.loc[dataa['PerformanceRating'] == 3, 'PerformanceRating'] = 0
dataa.loc[dataa['PerformanceRating'] == 2, 'PerformanceRating'] = 0

#WE label encode all our character columns.
for i in dataa.loc[:, dataa.columns != 'PerformanceRating']:
    le = preprocessing.LabelEncoder()
    if dataa[i].dtype != np.int64:
        dataa[str(i)] = le.fit_transform(dataa[str(i)])
    else:
        pass

#We do a quick feature selection.
#cor = dataa.corr()
#cor_target = abs(cor['PerformanceRating']).sort_values(ascending=False) #we will use top 5 correlations.

dataa = dataa[['EmpEnvironmentSatisfaction','EmpLastSalaryHikePercent','YearsSinceLastPromotion','EmpDepartment',
       'ExperienceYearsInCurrentRole', 'PerformanceRating']]

#Use mahalanobis distance to remove outliers.

def mahalanobis(x=None, data=None, cov=None):
    x_minus_mu = x - np.mean(data)
    if not cov:
        cov = np.cov(data.values.T)
    inv_covmat = sp.linalg.inv(cov)
    left_term = np.dot(x_minus_mu, inv_covmat)
    mahal = np.dot(left_term, x_minus_mu.T)
    return mahal.diagonal()

dataa['mahala'] = mahalanobis(x=dataa.iloc[:, : 4], data=dataa.iloc[:, : 4])

threshold = chi2.ppf((1-0.01), df=2)

dataa = dataa.drop(dataa[dataa['mahala'] > threshold].index)

#Test for imbalance

dataa['PerformanceRating'].value_counts()
dataa = dataa.drop(['mahala'], axis=1)
#We see a major imbalance. Lets fix that.


df_majority = dataa[dataa.PerformanceRating== 0]
df_minority = dataa[dataa.PerformanceRating== 1]

df_minority_upsampled = resample(df_minority,
                                 replace=True,
                                 n_samples=1012,
                                 random_state=123)

df_upsampled = pd.concat([df_majority, df_minority_upsampled])


#We are now ready to perform logistic regression.

y = df_upsampled.PerformanceRating
X = df_upsampled.drop('PerformanceRating', axis=1)

XNew = [[1,2,3,4,5]]


clf_0 = LogisticRegression().fit(X, y)

pred_y_0 = clf_0.predict(X)
