# FlappyBirdAI
An artificial intelligence project for Texas Tech University CS 3368

# Requirements
Python 3.10.7
Python packages are in `requirements.txt`

# Usage

`cd src`<br>
`python main.py [debug]`

`[debug]` can be set to `True` or `False` to enable/disable previewing the current best path and threat line.

# Configuration

Comments are provided in `const.py` for what each variable is for.

The main two performance settings are `TREE_DELTA` and `TREE_DEPTH`, which is the time between frame renders and the
amount of frames the AI will look ahead respectively. `TREE_DEPTH` values too high will do nothing but waste memory.
`TREE_DELTA` values too high will break the AI, but greatly improve performance. It seems to break between `0.15` and
`0.2`.

The provided config file runs at 15 frames per second, if you would like to run at different frame rates
then change `TREE_DELTA` to `1 / <your desired fps`, for example `0.06` is `15fps` and `0.03` is `30fps`.

__The higher the framerate, the more states that have to be searched in the tree.__

Performance is mostly ok at 15fps. As an extreme measure, reduce `TREE_DELTA` to `0.2` and `TREE_DEPTH` to `20` for an
increase in performance. If this is not enough, then `0.5` and `10` 