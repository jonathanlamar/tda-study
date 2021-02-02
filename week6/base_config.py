import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from IPython import embed


class BaseConfig:
    r"""
    Class for holding data pipeline and config for any forecasting model I use.
    """

    def __init__(self,
                 dataPath='./data',
                 outPath='./out',
                 runId='TEST',
                 metric='MaxConcurrentStreamsOverall',
                 minDateData=None,  # infer
                 maxDateData=None,  # infer
                 numDaysPred=730,
                 detectAnomalies=False):
        self.runId = runId
        self.dataPath = dataPath
        self.outPath = outPath
        self.metric = metric
        self.minDateData = minDateData
        self.maxDateData = maxDateData
        self.numDaysPred = numDaysPred

        #######################
        # Load and prep dataset
        #######################
        df = pd.read_csv('%s/%s.csv' % (dataPath, metric),
                         parse_dates=True)  # This doesn't work...???
        df['Date'] = pd.to_datetime(df['Date'])

        dataset = (df
                   .drop('Time', axis=1)
                   .groupby('Date')  # V1 - only look at daily averages.
                   .mean()
                   .dropna())  # ???
        dataset.columns = [metric]

        # Limit data for testing or to remove weird behavior
        if minDateData is not None:
            minDateTime = pd.to_datetime(minDateData)
            dataset = dataset.loc[minDateTime:]
        if maxDateData is not None:
            maxDateTime = pd.to_datetime(maxDateData)
            dataset = dataset.loc[:maxDateTime]

        # Save the first and last available dates
        self.firstObservedDate = dataset.index.min()
        self.lastObservedDate = dataset.index.max()

        # Fill in missing rows and impute nulls with 1 (why 1?)
        # TODO: Use the lead(1) logic from Fourier components here.
        meanVal = df[metric].dropna().mean()
        self.dataset = self._imputeDates(dataset,
                                         self.firstObservedDate,
                                         self.lastObservedDate,
                                         imputeVal=meanVal)

        self.maxForecastEndDate = (self.lastObservedDate
                                   + relativedelta(self.lastObservedDate,
                                                   days=numDaysPred))

        if detectAnomalies:
            _ = self._detectAnomalies()

    def _detectAnomalies(self, threshold=0.5):
        r"""
        Detect days that deviate more than threshold.

        Deviation is measured in percent absolute change day over day.
        """

        today = self.dataset[self.metric]
        prevDay = today.shift(1)

        se = ((np.abs(today - prevDay) / prevDay)
              .dropna()
              .sort_values(ascending=False))

        anomalousDays = pd.Series(se[se > 0.5],
                                  name='Percent diff over previous day')

        print('Found the following anomalous days:')
        print(anomalousDays)

        return anomalousDays

    def _bumpZeros(self, valToBump=1):
        r"""
        Replace any zeros with valToBump.  Useful for Box-Cox transformation.
        """

        zeroInds = (self.dataset[self.metric] <= 0)
        self.dataset.loc[zeroInds, self.metric] = valToBump

    def patchSeries(self, firstDatePatch, lastDatePatch):
        r""" Patch anomalous values of series with linear interpolation.  """

        # Get x and y values on either side of the anomalous data for
        # interpolation
        lastDayObs = pd.to_datetime(firstDatePatch) + relativedelta(days=-1)
        nextDayObs = pd.to_datetime(lastDatePatch) + relativedelta(days=1)

        lastDateVal = self.dataset.loc[lastDayObs, self.metric]
        nextDateVal = self.dataset.loc[nextDayObs, self.metric]

        interpDf = self._interpolate(firstDatePatch,
                                     lastDatePatch,
                                     lastDateVal,
                                     nextDateVal)

        # Patch in values and recalculate rolling average
        self.dataset.loc[firstDatePatch:lastDatePatch, self.metric] = interpDf

    def _interpolate(self,
                     firstDayMissing,
                     lastDayMissing,
                     lastDateVal,
                     nextDateVal):
        r"""
        Linearly interpolate the missing values between dates.

        Assumes the rows already exist, but are null or should be overwritten
        for some reason.
        """

        numDaysImpute = (pd.to_datetime(lastDayMissing)
                         - pd.to_datetime(firstDayMissing)).days + 1

        # Rise over run.  In this case, run is the gap between observations,
        # so one plus the number of rows imputing.
        slope = (nextDateVal - lastDateVal) / (numDaysImpute + 1)

        imputedVals = pd.Series(
            np.linspace(
                lastDateVal+slope,
                nextDateVal-slope,
                numDaysImpute
            ),
            index=self._getDateIndex(
                pd.to_datetime(firstDayMissing),
                pd.to_datetime(lastDayMissing)
            )
        ).astype(int)

        return imputedVals

    def _imputeDates(self, tsDf, minDate, maxDate, imputeVal=np.nan):
        r"""
        Impute missing dates into a time series and impute with imputeVal.
        """
        imputeDf = pd.DataFrame(index=self._getDateIndex(minDate, maxDate))

        return tsDf.join(imputeDf, how='outer').fillna(imputeVal)

    def _getDateIndex(self, minDate, maxDate):
        r""" Make pandas date index of range. """
        return pd.Index(pd.date_range(minDate, maxDate), name='Date')
