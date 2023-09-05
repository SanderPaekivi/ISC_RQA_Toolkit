###########################################################
### Generating ISC tables for modalities and localizers ###
###########################################################


### From a DataFrame listing each individuals time-series under question (separated by modality and localizer or soundbite etc) called "subject_df" here, 
### one ISC matrix is calculated simply via list comprehension
import scipy.stats as stats
isc_df = pd.DataFrame([ [1-stats.pearsonr(subject_df[c], subject_df[y])[0] for y in subject_df.columns] for c in subject_df.columns], columns = subject_df.columns, index = subject_df.columns);





###########################################################
################ Generating RSA table #####################
###########################################################

### From a DataFrame listing as columns every row-col combination of the ISC tables, as well as Model 1 and Model 2 values, called "df" here. 

import scipy.stats as stats
import numpy as np

### Calculate simple correlation table between all columns
cor_tab = df.corr(method = "kendall") 

### Calculate corresponding p-values, to be used as mask info during plotting
p_tab = pd.DataFrame([ [stats.kendalltau(df[c], df[y])[1] for y in df.columns] for c in df.columns], columns = df.columns, index = df.columns)

###
### NB: The full audiodrama scan is done with the same tools, simply windowed over changing data underneath to complete Kendall Tau analysis with Model 2, keeping track of consecutive successes and faileours. 
###





###########################################################
################### RQA via. PyRqa ########################
###########################################################


from pyrqa.time_series import TimeSeries
from pyrqa.analysis_type import Cross
from pyrqa.settings import Settings
from pyrqa.neighbourhood import FixedRadius
from pyrqa.neighbourhood import FAN
from pyrqa.metric import EuclideanMetric
from pyrqa.analysis_type import Classic
from pyrqa.computation import RQAComputation

### Defining a sought-after recurrence rate (RR), for which to calculate radius of similarity, as PyRqa only has input for radius
fixed_rr = 0.03

### Depending on the data, zeros should or should not be considered as meaningful. In case zeros are not important, cross-RQA can be conducted between two identical time-series, 
### with zeros replaced by large numbers outside of the regular value variation, and with different sign as to not capture them in calculations.  

xd = df.copy()
xd.loc[xd[xd.iloc[:,2]==0].index] = -999 
xd = xd.iloc[:,2]

yd = df.copy()
yd.loc[yd[yd.iloc[:,2]==0].index] == 999
yd = yd.iloc[:,2]

### Calculating list of all differences between two series
flat_list_x = [item for sublist in [[abs(i-j) for i in xd] for j in xd] for item in sublist]

### Estimating radius yielding sought-after recurrence rate by quantile 
ex = ( np.quantile(flat_list_x, fixed_rr) ) 


### Creating suitable time-series object, with chosen embedding and delay
time_series_x = TimeSeries(xd,
                           embedding_dimension=1,
                           time_delay=0)
time_series_y = TimeSeries(yd,
                           embedding_dimension=1,
                           time_delay=0)
time_series = (time_series_x,
               time_series_y)


settings = Settings(time_series,
                    analysis_type=Cross,
                    neighbourhood=FixedRadius(ex),
                    #neighbourhood=FAN(30),
                    similarity_measure=EuclideanMetric,
                    theiler_corrector=0)


### Running PyRQA computation
computation = RQAComputation.create(settings,
                                    verbose=False)
result = computation.run()
result.min_diagonal_line_length = 2
result.min_vertical_line_length = 2
result.min_white_vertical_line_length = 2

print(result.recurrence_rate)


### For plotting, the computation must be ran again after outputing numeric results, quirk of PyRQA it seems. 
from pyrqa.computation import RPComputation
from pyrqa.image_generator import ImageGenerator

computation = RPComputation.create(settings)
result = computation.run()

plt.imshow(result.recurrence_matrix_reverse)
plt.show()



