## Margaret River Experiments Created in PsychoPy. These instructions are the same for both tasks


## Requirements
* Meta installation of Python 3.8 installed in C:/Python38  
* PsychoPy 2022.2.5

## Installation
* Create virtual environment (I used anaconda, can be done directly with python with slightly different commands) 
	* conda create --name myenv python=3.8

* Install the requirements for the experiment
	* Ensure in virtual environment is activated (conda activate myenv)
	* pip install -r requirement.txt
	* pip install psychopy==2022.2.5

Your attempt to install psychopy may result in this error: "metadata-generation-failed". If so,
You can fix it with this code: 
	* pip3 install --upgrade setuptools==70.0.0
	

## Abort the Experiment
* To abort the experiment you can press **``` q ```** any time during the experiment. 
The report file will be saved up to the point the experiment was executed
