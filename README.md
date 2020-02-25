# CheckSoft Simulator
Simulator for Large-Scale testing of CheckSoft

## Getting Started

The software has been tested on an Ubuntu System. 

### Prerequisites

JDK 8
MPJExpress 

```

```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running tests for Verification 

### Launching the Main GUI

Please run the following commands:

```
cd CSUI
java -jar CheckSoftGUI.jar
```
Default simulation parameters are already provided. 
If the user wants to modify the simulation parameters please follow the guidelines provided on selecting the Test Application. Error messages will pop-up if the values entered are not acceptable. 

To run CheckSoft with the user provided simulation parameters please press the Run CheckSoft button. On successful completion the accuracy of CheckSoft and the latencies associated with the different events will be displayed in the bottom-left part of the GUI.  

## Running Performance Tests
### Scalability Test
To run the scalability test please open a terminal and run the commands provided below :


```
cd CSUI
chmod a+x runScalability.sh
./runScalability.sh 5
```

### Noise Tolerance Test
To run the Noise Tolerance test please open a terminal and run the commands provided below :


```
cd CSUI
chmod a+x runTolerance.sh
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

This project is not meant for any resuse. 

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

