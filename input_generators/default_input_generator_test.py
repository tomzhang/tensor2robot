# coding=utf-8
# Copyright 2019 The Tensor2Robot Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for estimator_models.input_generators.default_input_generator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from absl.testing import absltest
from tensor2robot.input_generators import default_input_generator
from tensor2robot.utils import tensorspec_utils
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS

BATCH_SIZE = 2
NUM_BATCHES = 3
NUM_TASKS = 3
EXAMPLES_PER_TASK = 10

_int64_feature = (
    lambda v: tf.train.Feature(int64_list=tf.train.Int64List(value=v)))


class DefaultInputGeneratorTest(tf.test.TestCase):

  def _test_input_generator(self, input_generator, is_dataset=False):
    feature_spec = tensorspec_utils.TensorSpecStruct()
    feature_spec.state = tensorspec_utils.ExtendedTensorSpec(
        shape=(64, 64, 3),
        dtype=tf.uint8,
        name='state/image',
        data_format='jpeg')
    feature_spec.action = tensorspec_utils.ExtendedTensorSpec(
        shape=(2), dtype=tf.float32, name='pose')
    label_spec = tensorspec_utils.TensorSpecStruct()
    label_spec.reward = tensorspec_utils.ExtendedTensorSpec(
        shape=(), dtype=tf.float32, name='reward')
    with self.assertRaises(ValueError):
      _ = input_generator.create_dataset_input_fn(
          mode=tf.estimator.ModeKeys.TRAIN)

    input_generator.set_feature_specifications(feature_spec, feature_spec)
    input_generator.set_label_specifications(label_spec, label_spec)

    np_features, np_labels = input_generator.create_dataset_input_fn(
        mode=tf.estimator.ModeKeys.TRAIN)().make_one_shot_iterator().get_next(
        )

    np_features = tensorspec_utils.validate_and_pack(
        feature_spec, np_features, ignore_batch=True)
    np_labels = tensorspec_utils.validate_and_pack(
        label_spec, np_labels, ignore_batch=True)
    self.assertAllEqual([2, 64, 64, 3], np_features.state.shape)
    self.assertAllEqual([2, 2], np_features.action.shape)
    self.assertAllEqual((2,), np_labels.reward.shape)

  def test_record_input_generator(self):
    base_dir = 'tensor2robot'
    file_pattern = os.path.join(
        FLAGS.test_srcdir, base_dir, 'test_data/pose_env_test_data.tfrecord')
    input_generator = default_input_generator.DefaultRecordInputGenerator(
        file_patterns=file_pattern, batch_size=BATCH_SIZE)
    self._test_input_generator(input_generator)

  def test_random_dataset(self):
    input_generator = default_input_generator.DefaultRandomInputGenerator(
        batch_size=2)
    self._test_input_generator(input_generator)

  def test_constant_dataset(self):
    input_generator = default_input_generator.DefaultConstantInputGenerator(
        constant_value=1, batch_size=2)
    self._test_input_generator(input_generator)


if __name__ == '__main__':
  absltest.main()