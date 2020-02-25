# CheckSoft Simulator
Simulator for Large-Scale testing of CheckSoft

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

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

## Running the tests

Explain how to run the automated tests for this system

### Launching the GUI

Please run the following commands:

```
cd CSUI
java -jar CheckSoftGUI.jar
```

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
* [WindowBuilder](https://www.eclipse.org/windowbuilder/) - GUI Development

## Authors

* **Rohan Sarkar** - [sarkar-rohan](https://github.com/sarkar-rohan)

## License

This project is not meant for any resuse. 

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

