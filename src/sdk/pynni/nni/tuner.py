# Copyright (c) Microsoft Corporation. All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ==================================================================================================


import logging

import nni
from .recoverable import Recoverable

_logger = logging.getLogger(__name__)


class Tuner(Recoverable):
    # pylint: disable=no-self-use,unused-argument

    def generate_parameters(self, parameter_id, **kwargs):
        """Returns a set of trial (hyper-)parameters, as a serializable object.
        User code must override either this function or 'generate_multiple_parameters()'.
        parameter_id: int
        """
        raise NotImplementedError('Tuner: generate_parameters not implemented')

    def generate_multiple_parameters(self, parameter_id_list, **kwargs):
        """Returns multiple sets of trial (hyper-)parameters, as iterable of serializable objects.
        Call 'generate_parameters()' by 'count' times by default.
        User code must override either this function or 'generate_parameters()'.
        If there's no more trial, user should raise nni.NoMoreTrialError exception in generate_parameters().
        If so, this function will only return sets of trial (hyper-)parameters that have already been collected.
        parameter_id_list: list of int
        """
        result = []
        for parameter_id in parameter_id_list:
            try:
                _logger.debug("generating param for {}".format(parameter_id))
                res = self.generate_parameters(parameter_id, **kwargs)
            except nni.NoMoreTrialError:
                return result
            result.append(res)
        return result

    def receive_trial_result(self, parameter_id, parameters, value, **kwargs):
        """Invoked when a trial reports its final result. Must override.
        By default this only reports results of algorithm-generated hyper-parameters.
        Use `accept_customized_trials()` to receive results from user-added parameters.
        parameter_id: int
        parameters: object created by 'generate_parameters()'
        value: object reported by trial
        customized: bool, true if the trial is created from web UI, false if generated by algorithm
        trial_job_id: str, only available in multiphase mode.
        """
        raise NotImplementedError('Tuner: receive_trial_result not implemented')

    def accept_customized_trials(self, accept=True):
        """Enable or disable receiving results of user-added hyper-parameters. 
        By default `receive_trial_result()` will only receive results of algorithm-generated hyper-parameters.
        If tuners want to receive those of customized parameters as well, they can call this function in `__init__()`.
        """
        self._accept_customized = accept

    def trial_end(self, parameter_id, success, **kwargs):
        """Invoked when a trial is completed or terminated. Do nothing by default.
        parameter_id: int
        success: True if the trial successfully completed; False if failed or terminated
        """
        pass

    def update_search_space(self, search_space):
        """Update the search space of tuner. Must override.
        search_space: JSON object
        """
        raise NotImplementedError('Tuner: update_search_space not implemented')

    def load_checkpoint(self):
        """Load the checkpoint of tuner.
        path: checkpoint directory for tuner
        """
        checkpoin_path = self.get_checkpoint_path()
        _logger.info('Load checkpoint ignored by tuner, checkpoint path: %s' % checkpoin_path)

    def save_checkpoint(self):
        """Save the checkpoint of tuner.
        path: checkpoint directory for tuner
        """
        checkpoin_path = self.get_checkpoint_path()
        _logger.info('Save checkpoint ignored by tuner, checkpoint path: %s' % checkpoin_path)

    def import_data(self, data):
        """Import additional data for tuning
        data: a list of dictionarys, each of which has at least two keys, 'parameter' and 'value'
        """
        pass

    def _on_exit(self):
        pass

    def _on_error(self):
        pass
