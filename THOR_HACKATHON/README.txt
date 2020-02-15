##########################

#    HACKATHON THOR

##########################

THOR - Project to select test using decision tree machine learning algorithm
       using historical bug dataset.

We have created a predictive model that estimates the probability of each test
failing for a newly proposed code change. Instead of defining the model
manually, we built it by using a data set containing results of tests on
historical code changes and then applying standard machine learning techniques
During training, our system learns a model based on features derived from
previous code changes and tests.
When the system is analyzing new code changes, we apply the learned model to a
feature-based abstraction of the code change.
For any particular test, the model is then able to predict the likelihood of
detecting a regression.
To do this, the system uses decision tree machine learning algorithm.

# Project contains following source code files

- ml.py - This scripts performs all operations to prepare dataset and
          decision tree machine learning core module functionality.

          Usage -> "python ml.py --changeid 374556 --dataset source_test_dataset"

- gerrit_tool.py - This scripts sends REST API request to Gerrit to get the list
                   of modified files using legacy Gerrit change Id number
                   provided as input.

          Usage -> "python gerrit_tool.py gerrit_changeid_list_files --gerrit_change_id 375468"

- jira_info.py - This scripts uses JIRA REST API to fetch
                 BUG No. Change Id and test name information from JIRA product
                 bugs.

          Usage -> "python jira_info.py"

- test_selector.py - This scripts performs mapping of source files to test.
                     This script uses database of source files and tests which
                     is created before test selection using machine learning
                     algorithm.

          Usage -> "python test_selector.py --modified_files minerva/py/minerva/utils/minerva_task_util.py"

- db.py - This scripts updates and reads source and test file mapping from
          persistent storage.

          Usage -> "python db.py --test_map_store map_store_source_test"

# Project also contains PPT presentation of this idea - Thor-Hackathon.pdf
