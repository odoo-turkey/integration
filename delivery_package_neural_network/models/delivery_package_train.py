# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields, api

from tensorflow import keras
from keras.models import Sequential, model_from_json
from keras.layers import Dense
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tensorflow.keras.optimizers import RMSprop
from pandas.core.frame import DataFrame


class DeliveryPackageTrain(models.Model):
    _name = 'delivery.package.train'
    _description = 'Train model for delivery package prediction.'

    @api.model
    def action_debug_train(self):
        pass