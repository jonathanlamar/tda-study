import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import datetime
import os

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.units as munits
from IPython import embed


r"""
This module holds all of the plottng functions for delivering the forecast,
validation, and summary.

The methods all operate on an extension of BaseConfig with fit, validate,
predict, and summary methods.
"""


def generateDeliverable(modelOb):
    r""" Generate and save all output for delivery.  """

    # For saving in a systematic way
    modelFilePath = '%s/%s_%s' % (modelOb.outPath,
                                  modelOb.runId,
                                  modelOb.metric)

    print('Training and predicting model.')
    predDf = modelOb.predict()

    print('Generating and saving forecast plot.')
    f, _ = plotForecast(predDf, metric=modelOb.metric)
    plt.savefig('%s_forecast_plot.png' % modelFilePath)
    plt.close(f)

    print('Validating model.')
    maxDate = modelOb.lastObservedDate + relativedelta(months=-1)
    valDf = modelOb.validate(maxDate)

    print('Plotting validation metrics.')
    f, _ = plotValidation(valDf, metric=modelOb.metric)
    plt.savefig('%s_validation_plot.png' % modelFilePath)
    plt.close(f)

    print('Saving model raw output.')
    outDf = predDf.join(
        valDf.drop(
            [modelOb.metric, 'GREEN', 'YELLOW', 'RED', 'color'],
            axis=1
        )
    )
    outDf.to_csv('%s_forecast.csv' % modelFilePath)

    print('Saving model summary.')
    with open('%s_arima_summary.txt' % modelFilePath, 'w') as fh:
        fh.write(modelOb.arimaSummary)

    print('Saving global trend summary.')
    with open('%s_ols_summary.txt' % modelFilePath, 'w') as fh:
        fh.write(modelOb.globalTrendSummary)

    return predDf, valDf


######################
# Methods for plotting
######################
color_green = '#259b24'
color_blue = '#03a9f4'
color_purple = '#7e57c2'
color_red = '#e91e63'
color_gray = '#282828'
color_yellow = '#fd971f'


def plotForecast(predDf,
                 metric,
                 inSamplePredCol='InSamplePredictions',
                 ooSamplePredCol='OoSamplePredictions',
                 ciLowerCol='ConfIntLower',
                 ciUpperCol='ConfIntUpper',
                 shade_CIs=True,
                 figSize=(50, 20),
                 fontSize=40,
                 yRange=None,
                 xRange=None,
                 lineWidth=2,
                 titleText=None,
                 yAxisText=None):
    r"""
    Plot observed, in-sample, and out-of-sample predictions with confidence
    intervals.
    """

    # Axis labels
    if yAxisText is None:
        yAxisText = metric

    if titleText is None:
        titleText = metric

    # Set ranges
    if xRange is None:
        xRange = (predDf.index.min(), predDf.index.max())
    if yRange is None:
        df = predDf.loc[xRange[0]: xRange[1]].copy()

        for col in [metric, inSamplePredCol, ooSamplePredCol]:
            # Avoid nans by imputing nulls with the mean of all values.
            meanVal = df[col].dropna().mean()
            df[col] = df[col].fillna(meanVal)

        maxVal = max(df[metric].max(),
                     df[inSamplePredCol].max(),
                     df[ooSamplePredCol].max())
        minVal = max(df[metric].min(),
                     df[inSamplePredCol].min(),
                     df[ooSamplePredCol].min())

        valRange = maxVal - minVal

        yMax = maxVal + 0.25*valRange
        yMin = 0 if minVal >= 0 else minVal - 0.25*valRange

        yRange = (yMin, yMax)

    # Initalize figure with decent defaults.
    f, ax = initializeFigure(figSize=figSize,
                             fontSize=fontSize,
                             titleText=titleText,
                             yAxisText=yAxisText,
                             xRange=xRange,
                             yRange=yRange)

    # Shading between confidence intervals
    if shade_CIs:
        CILowerCols = [col for col in predDf.columns
                       if col.find(ciLowerCol) != -1]
        CIUpperCols = [col for col in predDf.columns
                       if col.find(ciUpperCol) != -1]

        CIPercentiles = [col[:col.find('%')] for col in CILowerCols]
        for lower, upper, percentile in zip(CILowerCols,
                                            CIUpperCols,
                                            CIPercentiles):
            ax.fill_between(predDf.index,
                            predDf[lower],
                            predDf[upper],
                            facecolor=color_gray,
                            alpha=0.25,
                            label=percentile+'% CI')

    ######################
    # Plot Forecast Model.
    ######################
    ax.plot(predDf[metric],
            label='Observed',
            linewidth=lineWidth,
            color=color_green)

    ax.plot(predDf[inSamplePredCol],
            label='In Sample Forecast',
            linewidth=lineWidth,
            color=color_red,
            alpha=0.5)

    ax.plot(predDf[ooSamplePredCol],
            label='Out of Sample Forecast',
            linewidth=lineWidth,
            color=color_blue,
            alpha=1)

    # label axes
    ax.set_ylabel(yAxisText, fontsize=fontSize)
    ax.set_xlabel('Date', fontsize=fontSize)

    # Set ranges
    ax.set_xlim(xRange)
    ax.set_ylim(yRange)

    ############################
    # Date formatting of x axis.
    ############################
    f, ax = formatDateTicks(f, ax)

    ###############
    # Place legend.
    ###############
    f, ax = setLegend(f, ax, fontSize)

    return f, ax


def plotValidation(valDf,
                   metric,
                   valPredCol='ValidationPred',
                   figSize=(50, 20),
                   yRange=None,
                   fontSize=40,
                   lineWidth=2,
                   titleText=None,
                   yAxisText=None,
                   greenYellowThreshold=5,
                   yellowRedThreshold=15):
    r"""
    Plot observed and predicted over the validation set with some decoration.
    """

    # Axis labels
    if yAxisText is None:
        yAxisText = metric

    if titleText is None:
        titleText = metric

    # Set ranges
    xRange = (valDf.index.min(), valDf.index.max())
    if yRange is None:
        maxVal = max(valDf[metric].max(),
                     valDf[valPredCol].max())
        minVal = min(valDf[metric].min(),
                     valDf[valPredCol].min())

        valRange = maxVal - minVal

        yMax = maxVal + 0.25*valRange
        yMin = minVal - 0.25*valRange

        yRange = (yMin, yMax)

    # Initalize figure with decent defaults.
    f, ax = initializeFigure(figSize=figSize,
                             fontSize=fontSize,
                             titleText=metric,
                             yAxisText=metric,
                             xRange=xRange,
                             yRange=yRange)

    ############################################
    # Compute some derived metrics for plotting.
    ############################################
    # We are going to plot each day's prediction via a scatter plot.
    # The colors will be based on the given threshold percentage abs. error.
    def parse_bools_to_color(x, y, z):
        if x:
            return color_green
        elif y:
            return color_yellow
        elif z:
            return color_red
        else:
            return color_purple

    # construct green, yellow, red labels for days in various ranges.
    valDf['GREEN'] = valDf['PercentError'] <= greenYellowThreshold
    valDf['YELLOW'] = ((valDf['PercentError'] > greenYellowThreshold)
                       & (valDf['PercentError'] <= yellowRedThreshold))
    valDf['RED'] = valDf['PercentError'] > yellowRedThreshold

    valDf['color'] = valDf[['GREEN', 'YELLOW', 'RED']].apply(
        lambda row: parse_bools_to_color(row[0], row[1], row[2]),
        axis=1,
        result_type='reduce'
    )

    # Plot Forecast Model
    ax.plot(valDf[metric],
            label='Observed',
            linewidth=lineWidth,
            color=color_green,
            alpha=0.5)
    ax.plot(valDf[valPredCol],
            label='Validation Predictions',
            linewidth=lineWidth,
            color=color_blue,
            alpha=0.5)
    ax.scatter(valDf.index,
               valDf[valPredCol],
               label=None,
               c=valDf['color'],
               s=3*fontSize)

    ############################
    # Date formatting of x axis.
    ############################
    f, ax = formatDateTicks(f, ax)

    ###############
    # Place legend.
    ###############
    f, ax = setLegend(f, ax, fontSize)

    return f, ax


def initializeFigure(figSize,
                     fontSize,
                     titleText,
                     yAxisText,
                     xRange,
                     yRange):
    r""" Create figure with reasonable defaults. """

    # Initialize figure
    f, ax = plt.subplots(1, 1, figsize=figSize)

    # Label axes
    ax.set_ylabel(yAxisText, fontsize=fontSize)
    ax.set_xlabel('Date', fontsize=fontSize)
    ax.set_title(titleText, fontsize=1.5*fontSize)

    # Set ranges
    ax.set_xlim(xRange)
    ax.set_ylim(yRange)

    # Other decoration
    ax.grid(axis='x')
    ax.tick_params(axis='both', which='major', labelsize=fontSize)
    ax.tick_params(axis='both', which='minor', labelsize=fontSize)

    return f, ax


def formatDateTicks(f, ax):
    r"""
    Use some reasonable auto-formatting for time-based x ticks.

    Taken from here:
    https://matplotlib.org/3.1.0/gallery/ticks_and_spines/date_concise_formatter.html
    """
    formats = ['%y',          # ticks are mostly years
               '%b',     # ticks are mostly months
               '%d',     # ticks are mostly days
               '%H:%M',  # hrs
               '%H:%M',  # min
               '%S.%f', ]  # secs

    # these can be the same, except offset by one level....
    zero_formats = [''] + formats[:-1]

    # ...except for ticks that are mostly hours, then its nice to have month-day
    zero_formats[3] = '%d-%b'
    offset_formats = ['',
                      '%Y',
                      '%b %Y',
                      '%d %b %Y',
                      '%d %b %Y',
                      '%d %b %Y %H:%M', ]

    converter = mdates.ConciseDateConverter(formats=formats,
                                            zero_formats=zero_formats,
                                            offset_formats=offset_formats)

    munits.registry[np.datetime64] = converter
    munits.registry[datetime.date] = converter
    munits.registry[datetime.datetime] = converter

    return f, ax


def setLegend(f, ax, fontSize):
    r""" Draw legend. """
    leg = ax.legend(loc=2, prop={'size': fontSize})
    for line in leg.get_lines():
        line.set_linewidth(0.5*fontSize)

    return f, ax
