from hdat import Suite, MetricsChecker

import numpy as np
import matplotlib.pyplot as plt

from .image_example import rotate_and_blur


class ExampleSuite(Suite):
    id = 'example-suite'

    def collect(self):
        return {
            'chicken': {
                'image_location': 'data/chicken.jpg',
            },
            'wheat': {
                'image_location': 'data/wheat.jpg',
            }
        }

    def check(self, golden_metrics, metrics):
        checker = MetricsChecker(golden_metrics, metrics)
        checker.exact('size')
        checker.close('mean')
        checker.can_decrease('std')
        checker.close('min')
        checker.close('max')
        return checker.result()

    def run(self, case_input):
        out_data = rotate_and_blur(case_input['image_location'])
        metrics = {}
        metrics['size'] = out_data.ndim
        metrics['mean'] = float(np.mean(out_data))
        metrics['std'] = float(np.std(out_data))
        metrics['min'] = int(np.amin(out_data))
        metrics['max'] = int(np.amax(out_data))
        return metrics, out_data

    def show(self, result):
        metrics = result['metrics']
        context = result['context']

        print('-----------------')
        print('image dimensions: {}'.format(metrics['size']))
        print('image mean: {:5.3f}'.format(metrics['mean']))
        print('image std dev: {:5.3f}'.format(metrics['std']))
        print('image min: {:5.3f}'.format(metrics['min']))
        print('image max: {:5.3f}'.format(metrics['max']))

        plt.imshow(context)
        plt.show()
