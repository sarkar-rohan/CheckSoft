# CheckSoft Simulator
Simulator for Large-Scale testing of CheckSoft

## Getting Started

The software has been tested on an Ubuntu System. A conda environment needs to be created and activated as follows: 

### Prerequisites

JDK 8
MPJExpress 

```
conda create -n sim_env python=2.7 matplotlib
conda activate sim_env
```

### Installing

Please run the following commands : 

```
git clone https://github.com/sarkar-rohan/CheckSoft/
cd CS_GUI
chmod a+x runInitialize.sh
./runInitialize.sh
```
## Running tests for Verification 

### Launching the Main GUI

Please run the following commands:

```
java -jar CheckSoftGUI.jar
```
### Modifying the Simulation Parameters
* First select the Test Application
* Based on the selected application, the default simulation parameters are already provided. 
* If the user wants to modify the simulation parameters, please follow the guidelines provided on selecting the Test Application. Error messages will pop-up if the values entered are not acceptable. 
### Validating CheckSoft
* First select the Test Application
* To run CheckSoft with the user provided simulation parameters please press the Run CheckSoft button. 
* On successful completion the accuracy of CheckSoft and the latencies associated with the different events will be displayed in the bottom-left part of the GUI.  
### Verifying the FSM based Inference Logic 
* First select the Test Application
* On clicking the Verify Inference Logic Button, the GUI will check if acceptable parameters have been entered and then display the inferences made and the anomalies detected in a separate window. 
## Running Performance Tests
### Scalability Test
To run the scalability test please open a terminal and run the commands provided below :


```
./runScalability.sh 5
```

### Noise Tolerance Test
To run the Noise Tolerance test please open a terminal and run the commands provided below :


```
./runTolerance.sh 5
```
Please note that the parameter (5 in this case) passed is the number of iterations over which the experimental results will be averaged. The user can provide any other integer value, as desired.

Once the test completes the user can view the new results in the GUI by clicking the Scalability Test or the Noise Tolerance button again.
Please don't run any other tests using the GUI , when running these tests. 

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [MPJExpress](http://mpj-express.org/) - open source Java message passing library
* [WindowBuilder](https://www.eclipse.org/windowbuilder/) - GUI Development in Eclipse

## Authors

* **Rohan Sarkar** - [sarkar-rohan](https://github.com/sarkar-rohan)

## License

This project is only meant for testing purposes and is not meant for any resuse. 

%## Acknowledgments

%* Hat tip to anyone whose code was used
%* Inspiration
%* etc

