import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from dateutil.relativedelta import relativedelta

# ARIMA
from pmdarima import ARIMA

# statistics
from scipy.stats import boxcox
from scipy.special import inv_boxcox
import statsmodels.api as sm

# My stuff
from base_config import BaseConfig


class DecomposedArima(BaseConfig):
    r"""
    An ARIMA model which is decomposed into global trend + fourier + ARIMA.
    """

    def __init__(self,
                 dataPath='./data',
                 outPath='./out',
                 runId='TEST',
                 metric='MaxConcurrentStreamsOverall',
                 minDateData=None,  # infer
                 maxDateData=None,  # infer
                 numDaysPred=30,
                 detectAnomalies=False):

        print('Initializing V3 model.  Set instance attirbutes directly or they'
              ' will be inferred.')
        # Initalize dataset
        super().__init__(dataPath=dataPath,
                         outPath=outPath,
                         runId=runId,
                         metric=metric,
                         minDateData=minDateData,
                         maxDateData=maxDateData,
                         numDaysPred=numDaysPred,
                         detectAnomalies=detectAnomalies)

        # Boxcox stuff
        self.boxCoxLambda = None
        self.manualBoxCox = False

        # Global trend stuff
        self.globalSlope = None
        self.globalIntercept = None
        self.globalTrendExponent = 1.0
        self.globalTrendSummary = None
        self.manualCarryingCapacity = False
        self.carryingCapacity = None

        # Seasonal trend stuff
        self.numFourierComponents = 3
        self.seasonalTrend = None

        # ARIMA stuff
        self.arimaOrder = (1, 0, 1)
        self.arimaSeasonalOrder = (1, 1, 1, 7)
        self.arimaSummary = None

        # True iff boxcox, global, and seasonal have been learned
        self.isTrendLearned = False
        # True iff fit on *full* dataset
        self.isTrained = False
        self.currentModel = None

    ########################################
    # Methods for learning trend parameters.
    ########################################

    def learnTrendParams(self):
        r""" Learn all trend parameters.  """
        tsData = self.dataset[self.metric]

        print('Learning and saving trend parameters.')

        # These depend on each other, so we have to learn them in sequence.
        rollingData = self.getRollingAvg(tsData)
        self.learnCarryingCapacity(rollingData)
        bcRolling = self.learnBoxCoxParam(rollingData)
        detrendData = self.learnGlobalTrend(bcRolling)
        self.learnSeasonalTrend(detrendData)

        self.isTrendLearned = True

    def getRollingAvg(self, tsData):
        r""" Centered 7 day rolling average. """

        return tsData.rolling(7, center=True).mean().dropna()

    def setBoxCoxParam(self, val):
        r"""
        Manually set lambda for Box-Cox transformation.

        Sometimes the automatic procedure finds a negative optimal value and
        this is bad.
        """
        self.manualBoxCox = True
        self.boxCoxLambda = val

    def learnBoxCoxParam(self, tsData):
        r"""
        Find and store the optimal value of lambda for Box-Cox transformation.

        This is found via MLE for the transformed distribution under a normality
        assumption.
        """

        if self.manualBoxCox:
            print('Using manually set Box-Cox parameter.')

            if self.boxCoxLambda is None:
                raise RuntimeError('Box-Cox lambda was never set, even though \
                                    the manual flag was set.')

            bcRolling = boxcox(tsData, lmbda=self.boxCoxLambda)

        else:
            print('Learning Box-Cox parameter.')

            bcRolling, optimalLmda = boxcox(tsData)

            if optimalLmda < 0:
                raise RuntimeError('Box-Cox optimization found negative lambda.  '
                                   'Please set manually.')

            self.boxCoxLambda = optimalLmda

        return pd.Series(bcRolling, index=tsData.index)

    def learnGlobalTrend(self, tsData):
        r"""
        Train OLS regression on Box-Cox transformed rolling average.

        Stores slope, intercept, and summary string.
        """

        print('Learning global trend.')

        X = np.arange(0, tsData.shape[0])

        XPow = X**self.globalTrendExponent
        m, b = np.polyfit(XPow, tsData, deg=1)
        G = m*XPow + b

        # Now fit statsmodels OLS to get summary.
        df = pd.DataFrame({
            'x_pow': XPow,
            'intercept': 1
        })

        linear_model = sm.OLS(tsData.values, df)
        statsLR = linear_model.fit()

        self.globalSlope = m
        self.globalIntercept = b
        self.globalTrendSummary = statsLR.summary2().as_text()

        globalTrend = pd.Series(G, tsData.index)

        return tsData - globalTrend

    def setCarryingCapacity(self, val):
        r"""
        Manually set carrying capacity.

        For some app types in early adoption, e.g. AppleTV, we stick with a
        constant growth model.
        """
        self.manualCarryingCapacity = True
        self.carryingCapacity = val

    def learnCarryingCapacity(self, tsData):
        r"""
        Set carrying capacity based on values of rolling average of dataset.

        Ideally, this should not be used.
        """

        if self.manualCarryingCapacity:
            print('Using manually set carrying capacity.')

        else:
            print('Estimating carrying capacity.')

            self.carryingCapacity = 2.2*tsData.max()

    def learnSeasonalTrend(self, tsData):
        r""" Use Fourier transform to model seasonal trend.  """

        print('Learning seasonal trend.')

        lastYear = str(tsData
                       .dropna()
                       .index
                       .max()
                       .year - 1)

        lastYearData = tsData.loc[lastYear]
        idx = lastYearData.index

        fftData = np.fft.fft(lastYearData)
        fftFiltered = self._topComponentFilter(fftData)

        fourierSum = np.fft.ifft(fftFiltered).real

        self.seasonalTrend = pd.Series(fourierSum, index=idx)

    def _topComponentFilter(self, Z, threshold=12):
        Z_filtered = Z.copy()  # necessary to copy?  I don't want any side effects

        # kill high frequency components to avoid weekly seasonality dominating
        Z_filtered[range(threshold+1, len(Z_filtered))] = 0

        if self.numFourierComponents == 0:
            # If numFourierComponents is zero, null out everything
            Z_filtered = np.zeros(Z.shape)
        else:
            # indices of all but top weighted components
            inds = (np.abs(Z_filtered)
                    .argsort()[: -self.numFourierComponents])

            Z_filtered[inds] = 0

        return Z_filtered

    def getFreshARIMA(self):
        r""" Returns an untrained model. """

        return ARIMA(
            order=self.arimaOrder,
            seasonal_order=self.arimaSeasonalOrder,
            with_intercept=False,
            trend=None
        )

    ###############################################
    # Methods for transforming data to ARIMA space.
    ###############################################

    def toArimaSpace(self, tsData):
        r"""
        Transform data to ARIMA space, i.e., Box-Cox transform, then subtract
        global trend, then subtract seasonality.
        """

        if not self.isTrendLearned:
            raise RuntimeError('Box-Cox, Global, and Seasonal parameters have '
                               'not been learned.')

        bcData = self.boxCoxTransform(tsData)
        detrendData = self.subtractGlobalTrend(bcData)
        deSeasonData = self.subtractSeasonality(detrendData)

        return deSeasonData

    def boxCoxTransform(self, tsData):
        r""" Transform data using Box-Cox transformation.  """

        if self.boxCoxLambda is None:
            raise RuntimeError('Box-Cox lambda has not been learned or set.')

        bcVals = boxcox(tsData, lmbda=self.boxCoxLambda)

        return pd.Series(bcVals, index=tsData.index)

    def subtractGlobalTrend(self, tsData):
        r""" Subtract global trend from tsData.  """

        globalTrend = self._yieldLinearTrend(tsData.index)

        return tsData - globalTrend

    def _yieldLinearTrend(self, idx):
        r""" Extrapolate global trend onto the provided index. """

        if self.globalSlope is None or self.globalIntercept is None:
            raise RuntimeError(
                'Linear trend parameters have not been learned.')

        if idx.max() > self.lastObservedDate or idx.min() < self.firstObservedDate:
            raise RuntimeError('Index outside allowed range.')

        # Get index of min date, where zero is firstObservedDate.
        startX = (idx.min() - self.firstObservedDate).days

        # Construct regressor
        X = np.arange(startX, startX + len(idx))

        Xpow = X**self.globalTrendExponent
        globalTrend = self.globalSlope*Xpow + self.globalIntercept

        return pd.Series(globalTrend, index=idx)

    def subtractSeasonality(self, tsData):
        r"""
        Tile self.seasonalTrend over the date range of tsData and return their
        difference.
        """

        seasonalTrend = self._yieldSeasonalTrend(tsData.index)

        return tsData - seasonalTrend

    def _yieldSeasonalTrend(self, idx):
        r""" Tile self.seasonalTrend onto idx and return. """

        if self.seasonalTrend is None:
            raise RuntimeError('Seasonal trend has not been learned.')

        def getMonthDay(dateTime):
            return dateTime.strftime('%m-%d')

        # Dataframe of just month and day.
        idxDates = pd.Series(idx, index=idx).apply(getMonthDay)
        tmpMonthDay = pd.DataFrame({'tmpMonthDay': idxDates})

        # Fourier sum and tmpMonthDay
        fourierIdx = self.seasonalTrend.index
        fourierDates = pd.Series(
            fourierIdx, index=fourierIdx).apply(getMonthDay)
        fourierDf = pd.DataFrame({
            'FourierSum': self.seasonalTrend,
            'tmpMonthDay': fourierDates
        })

        fourierTiledDf = (tmpMonthDay
                          .reset_index()
                          .merge(fourierDf,
                                 left_on='tmpMonthDay',
                                 right_on='tmpMonthDay',
                                 how='left')
                          .set_index('Date'))

        # Lag 1 and fill nulls with previous day.  This imputes missing values
        # for leap year days.
        fourierTiledDf['lag'] = fourierTiledDf['FourierSum'].shift(1)
        fourierTiledDf.loc[fourierTiledDf['FourierSum'].isnull(), 'FourierSum'] = (
            fourierTiledDf.loc[fourierTiledDf['FourierSum'].isnull(), 'lag']
        )

        return fourierTiledDf['FourierSum']

    ######################################################
    # Methods for transforming data back from ARIMA space.
    ######################################################

    def backFromArimaSpace(self, tsData):
        r"""
        Back-transform data from the ARIMA prediction space to raw metric.
        """

        if not self.isTrendLearned:
            raise RuntimeError('Trend has not been learned.')

        seasonalData = self.addSeasonality(tsData)
        trendData = self.addGlobalTrend(seasonalData)
        rawData = self.invBoxCoxTransform(trendData)

        return rawData

    def invBoxCoxTransform(self, bcData):
        r""" Transform data using inverse Box-Cox transformation.  """

        if self.boxCoxLambda is None:
            raise RuntimeError('Box-Cox lambda has not been learned or set.')

        rawVals = inv_boxcox(bcData, self.boxCoxLambda)

        return pd.Series(rawVals, index=bcData.index)

    def addGlobalTrend(self, tsData):
        r""" Add global trend to tsData. """

        globalTrend = self._yieldGlobalTrend(tsData.index)

        return tsData + globalTrend

    def _yieldGlobalTrend(self, idx):
        r"""
        Use linear and logistic functions to extrapolate global trend onto the
        given dataset.
        """

        maxDate = idx.max()

        if maxDate <= self.lastObservedDate:
            globalTrend = self._yieldLinearTrend(idx)

        else:
            # In this case, the data spills over into the test set, where we
            # assume the linear trend starts to decay.

            # Index on training set
            trainIdx = idx[idx <= self.lastObservedDate]

            # Index on test set
            testIdx = idx[idx > self.lastObservedDate]

            linearPart = self._yieldLinearTrend(trainIdx)
            logisticPart = self._yieldLogisticTrend(testIdx)

            globalTrend = pd.concat([linearPart, logisticPart])

        return globalTrend

    def _yieldLogisticTrend(self, idx):
        r""" Extrapolate global trend forward with decaying logistic curve.  """

        if self.globalSlope is None or self.globalIntercept is None:
            raise RuntimeError('Global trend has not been learned.')

        if self.carryingCapacity is None:
            raise RuntimeError(
                'Carrying capacity has not been learned or set.')

        if idx.min() <= self.lastObservedDate:
            raise RuntimeError('Index outside allowed range.')

        # Get index of min date, where zero is lastObservedDate.
        startX = (idx.min() - self.lastObservedDate).days

        numDaysTrain = (self.lastObservedDate
                        - self.firstObservedDate
                        + relativedelta(days=1)).days

        # This is the value of the "linear" trend on self.lastObservedDate.
        valueAtZero = self.globalSlope * \
            (numDaysTrain - 1) + self.globalIntercept

        #############################
        # Derive Logistic parameters.
        #############################
        # This seems version-related, but boxcox can't handle a single float
        # input... So we do it manually.
        if self.carryingCapacity == 0:
            horizAsymptote = np.log(self.carryingCapacity)
        else:
            horizAsymptote = (
                (self.carryingCapacity**self.boxCoxLambda - 1)
                / self.boxCoxLambda
            )

        # Continuous growth rate of logistic curve
        r = (
            (horizAsymptote * self.globalSlope)
            / ((horizAsymptote - valueAtZero) * valueAtZero)
        )

        ###################################
        # Apply logistic equation to range.
        ###################################
        Xs = np.arange(startX, startX + len(idx))
        num = horizAsymptote * valueAtZero
        denom = valueAtZero + (horizAsymptote - valueAtZero) * np.exp(-r*Xs)

        # Logistic curve as numpy array
        Ys = num*(denom**(-1))

        return pd.Series(Ys, index=idx)

    def addSeasonality(self, tsData):
        r"""
        Tile self.seasonalTrend over the date range of tsData and return their
        sum.
        """

        seasonalTrend = self._yieldSeasonalTrend(tsData.index)

        return tsData + seasonalTrend

    def fit(self):
        r""" Fit the model.  Returns fit model. """

        print('Fitting model.')

        if not self.isTrendLearned:
            self.learnTrendParams()

        tsData = self.dataset[self.metric]

        trainEndog = self.toArimaSpace(tsData)

        model = self.getFreshARIMA()

        print('Fitting ARIMA.')

        model.fit(trainEndog)

        self.currentModel = model
        self.isTrained = True
        self.arimaSummary = str(model.summary())

        return model

    def predict(self, alpha=0.2):
        r""" Return predictions in and out of sample. """

        if self.isTrained:
            fitModel = self.currentModel
        else:
            fitModel = self.fit()

        ############################
        # Get in sample predictions.
        ############################
        trainPreds = fitModel.predict_in_sample()

        trainDf = pd.DataFrame(
            data={'ArimaInSamplePred': trainPreds},
            index=self._getDateIndex(
                self.firstObservedDate,
                self.lastObservedDate
            )
        )

        #########################################################
        # Get out of sample predictions and confidence intervals.
        #########################################################
        begin = self.lastObservedDate + relativedelta(days=1)
        end = self.lastObservedDate + relativedelta(days=self.numDaysPred+1)

        yPred, predCis = fitModel.predict(
            n_periods=self.numDaysPred,
            return_conf_int=True,
            alpha=0.2
        )

        predIdx = predExog.index

        CiColnamePrefix = '%d%%ConfInt' % int(100*(1-alpha))
        forecastDf = pd.DataFrame(
            data={
                'ArimaOoSamplePred': yPred,
                'Arima' + CiColnamePrefix + 'Lower': predCis[:, 0],
                'Arima' + CiColnamePrefix + 'Upper': predCis[:, 1]
            },
            index=predIdx
        )

        predDf = (self.dataset[[self.metric]]
                  .join(trainDf)
                  .join(forecastDf, how='outer'))

        inSamplePreds = self.backFromArimaSpace(predDf['ArimaInSamplePred'])
        predDf['InSamplePredictions'] = inSamplePreds

        ooSamplePreds = self.backFromArimaSpace(predDf['ArimaOoSamplePred'])
        predDf['OoSamplePredictions'] = ooSamplePreds

        ciLower = self.backFromArimaSpace(
            predDf['Arima' + CiColnamePrefix + 'Lower']
        )
        predDf[CiColnamePrefix+'Lower'] = ciLower

        ciUpper = self.backFromArimaSpace(
            predDf['Arima' + CiColnamePrefix + 'Upper']
        )
        predDf[CiColnamePrefix+'Upper'] = ciUpper

        return predDf[[
            self.metric,
            'InSamplePredictions',
            'OoSamplePredictions',
            CiColnamePrefix + 'Lower',
            CiColnamePrefix + 'Upper'
        ]]

    def validate(self, maxDate, alpha=0.05):
        r"""
        Create new DecomposedArima instance with data limited to maxDate,
        generate predictions from it, and compare to data after maxDate.
        """

        print('Creating new instance to validate.')

        if maxDate >= self.lastObservedDate:
            raise RuntimeError('maxDate must be less than lastObservedDate.')

        firstPredDate = maxDate + relativedelta(days=1)
        numDaysVal = (self.lastObservedDate - maxDate).days

        valModel = DecomposedArima(
            dataPath=self.dataPath,
            outPath=self.outPath,
            runId=self.runId,
            metric=self.metric,
            minDateData=self.minDateData,
            maxDateData=maxDate,
            numDaysPred=numDaysVal
        )

        # Copy self.dataset in case any manual smoothing was done.
        valModel.dataset = self.dataset.loc[:maxDate]

        # If Box-Cox lambda was manually set, then do the same here.
        if self.manualBoxCox:
            valModel.setBoxCoxParam(self.boxCoxLambda)

        # Get out of sample predictions.
        valDf = (valModel.predict(alpha=alpha)
                 .drop('InSamplePredictions', axis=1))

        # Augment
        valDf[self.metric] = self.dataset[self.metric]
        valDf.columns = [
            self.metric,
            'ValidationPred',
            valDf.columns[2],
            valDf.columns[3]
        ]

        # Attach metrics to validation df.
        err = valDf[self.metric] - valDf['ValidationPred']
        valDf['AbsoluteError'] = np.abs(err)
        valDf['SquaredError'] = np.square(valDf['AbsoluteError'])
        valDf['PercentError'] = 100*(valDf['AbsoluteError']/valDf[self.metric])

        return valDf.loc[firstPredDate:]
