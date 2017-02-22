#! coding: utf8

import logging
import os
from collections import defaultdict

import coloredlogs
import numpy as np
from scipy.sparse import hstack
from scipy.stats import boxcox
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder


class BoxCoxScaler:
    """BoxCoxScaler with data shift."""
    def __init__(self, verbose='INFO'):
        self.delta = 0.01
        self.verbose = verbose
        self._configure_logger()

    def _configure_logger(self, file=False, stdout=True):
        """Initialize logger.

        Parameters
        --------
        file: bool (default: False).
            If True, logs will be written into text file.
        stdout: bool (default: True).
            If True, logs will be printed onto screen(stdout).
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.handlers = []  # clear old handlers
        logger.setLevel(self.verbose)

        if file:  # file logger
            if not os.path.exists('./log/'):
                os.mkdir('./log/')
            handler = logging.FileHandler(
                './log/%s.log' % os.path.basename(self.__class__.__name__)
            )
            handler.setLevel(self.verbose)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s %(name)s [%(levelname)s]: %(message)s',
                '%H:%M:%S'
            ))
            logger.addHandler(handler)

        if stdout:  # screen(stdout) logger
            coloredlogs.install(
                logger=logger,
                level=self.verbose,
                fmt='%(asctime)s %(name)s [%(levelname)s]: %(message)s',
                datefmt='%H:%M:%S',
                reconfigure=False,
            )
            """
            handler = logging.StreamHandler()
            handler.setLevel(self.verbose)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(processName)s: %(message)s',
                '%H:%M:%S'
            ))
            logger.addHandler(handler)
            """

        logger.setLevel(self.verbose)  # fix wierd bug for coloredlogs

        self.logger = logger

    def fit(self, x):
        """Fit!

        Parameters
        --------
        x: ndarray.
            Data to be fit, in the shape of (n_samples, n_features).

        Returns
        --------
        self: instance of BoxCoxScaler.
            BoxCoxScaler itself.
        """
        n_samples, n_features = x.shape
        self.lmbdas = np.zeros(n_features)
        for i in xrange(n_features):
            _, self.lmbdas[i] = boxcox(x[:, i] + self.delta)
        return self

    def transform(self, x):
        """Transform!

        Parameters
        --------
        x: ndarray.
            Data to be transformed, in the shape of (n_samples, n_features)

        Returns
        --------
        y: ndarray.
            Transformed data, in the shape of (n_samples, n_features)
        """
        n_samples, n_features = x.shape
        return np.hstack([
            boxcox(x[:, i] + self.delta, self.lmbdas[i]).reshape(-1, 1)
            for i in xrange(n_features)
        ])

    def fit_transform(self, x):
        """Fit and transform!

        Parameters
        --------
        x: ndarray.
            Data to be transformed, in the shape of (n_samples, n_features)

        Returns
        --------
        y: ndarray.
            Transformed data, in the shape of (n_samples, n_features)
        """
        return self.fit(x).transform(x)

    def inverse_transform(self, y):
        """Do the inverse transform.

        Parameters
        --------
        y: ndarray.
            Data to be inverse transformed, in the shape of (n_features,
            n_samples)

        Returns
        --------
        x: ndarray.
            Inverse transformed data, in the shape of (n_samples, n_features)
        """
        n_samples, n_features = y.shape
        ret = []
        for i in xrange(n_features):
            if self.lmbdas[i] == 0:
                ret.append(np.exp(y[:, i]))
            else:
                ret.append(np.exp(np.log([
                    np.max(j, (self.delta+1)**self.lmbdas[i])
                    for j in self.lmbdas[i]*y[:, i]+1
                ])/self.lmbdas[i]) - self.lmbdas[i])
        return np.hstack(ret)


class IcyScaler:
    """Combination of multiple scalers, used for data preprocessing."""
    def __init__(self, verbose='INFO'):
        self.verbose = verbose
        self._configure_logger()

    def _configure_logger(self, file=False, stdout=True):
        """Initialize logger.

        Parameters
        --------
        file: bool (default: False).
            If True, logs will be written into text file.
        stdout: bool (default: True).
            If True, logs will be printed onto screen(stdout).
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.handlers = []  # clear old handlers
        logger.setLevel(self.verbose)

        if file:  # file logger
            if not os.path.exists('./log/'):
                os.mkdir('./log/')
            handler = logging.FileHandler(
                './log/%s.log' % os.path.basename(self.__class__.__name__)
            )
            handler.setLevel(self.verbose)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s %(name)s [%(levelname)s]: %(message)s',
                '%H:%M:%S'
            ))
            logger.addHandler(handler)

        if stdout:  # screen(stdout) logger
            coloredlogs.install(
                logger=logger,
                level=self.verbose,
                fmt='%(asctime)s %(name)s [%(levelname)s]: %(message)s',
                datefmt='%H:%M:%S',
                reconfigure=False,
            )
            """
            handler = logging.StreamHandler()
            handler.setLevel(self.verbose)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(processName)s: %(message)s',
                '%H:%M:%S'
            ))
            logger.addHandler(handler)
            """

        logger.setLevel(self.verbose)  # fix wierd bug for coloredlogs

        self.logger = logger

    def fit(self, x, categorial_columns=None, continuous_columns=None):
        """Fit!

        Parameters
        --------
        x: pandas.DataFrame.
            Data to be fit, in the shape of (n_samples, n_features).
        categorial_columns: list of str (default: None).
            List of categorial columns. If None, categorial columns will be
            extracted automatically.
        continuous_columns: list of str (default: None).
            List of continuous columns. If None, continuous columns will be
            extracted automatically.

        Returns
        --------
        self: instance of IcyScaler.
            IcyScaler itself.
        """
        categorial_columns = categorial_columns or self._extract_categorial(x)
        continuous_columns = continuous_columns or self._extract_continuous(x)

        # encode labels
        if categorial_columns:
            categorial_data = x[categorial_columns]

            self.label_encoders = defaultdict(LabelEncoder)
            categorial_data = categorial_data.apply(
                lambda column:
                self.label_encoders[column.name].fit_transform(column)
            ).values
            self.one_hot_encoder = OneHotEncoder().fit(categorial_data)

        # encode continuous
        if continuous_columns:
            continuous_data = x[continuous_columns].values
            self.box_cox_scaler = BoxCoxScaler().fit(continuous_data)
            continuous_data = self.box_cox_scaler.transform(continuous_data)
            self.min_max_scaler = MinMaxScaler().fit(continuous_data)

        return self

    def transform(self, x, categorial_columns=None, continuous_columns=None):
        """Transform!

        Parameters
        --------
        x: ndarray.
            Data to be transformed, in the shape of (n_samples, n_features)
        categorial_columns: list of str (default: None).
            List of categorial columns. If None, categorial columns will be
            extracted automatically.
        continuous_columns: list of str (default: None).
            List of continuous columns. If None, continuous columns will be
            extracted automatically.

        Returns
        --------
        y: ndarray.
            Transformed data, in the shape of (n_samples, n_features).
            WARNING: order of columns will be changed!
        """
        categorial_columns = categorial_columns or self._extract_categorial(x)
        continuous_columns = continuous_columns or self._extract_continuous(x)

        categorial_data = continuous_data = None

        # transform labels
        if categorial_columns:
            categorial_data = x[categorial_columns]

            categorial_data = categorial_data.apply(
                lambda column:
                self.label_encoders[column.name].transform(column)
            ).values
            categorial_data = self.one_hot_encoder.transform(categorial_data)

        # transform continuous
        if continuous_columns:
            continuous_data = x[continuous_columns].values
            continuous_data = self.box_cox_scaler.transform(continuous_data)
            continuous_data = self.min_max_scaler.transform(continuous_data)
        try:
            return hstack([
                i
                for i in [categorial_data, continuous_data]
                if i is not None
            ])
        except ValueError:  # dense matrix
            return np.concatenate([
                i
                for i in [categorial_data, continuous_data]
                if i is not None
            ], axis=1)

    def fit_transform(self, x):
        return self.fit(x).transform(x)

    def _extract_categorial(self, x):
        """Extract categorial columns.

        Parameters
        --------
        x: pandas.DataFrame.
            DataFrame to be extracted.

        Returns
        --------
        lst: list of str.
            Categorial column names.
        """
        lst = x.columns[x.dtypes == object].tolist()
        self.logger.info('%s categorial columns found.' % len(lst))
        return lst

    def _extract_continuous(self, x):
        """Extract continuous columns.

        Parameters
        --------
        x: pandas.DataFrame.
            DataFrame to be extracted.

        Returns
        --------
        lst: list of str.
            Continuous column names.
        """
        lst = x.columns[x.dtypes != object].tolist()
        self.logger.info('%s continuous columns found.' % len(lst))
        return lst
