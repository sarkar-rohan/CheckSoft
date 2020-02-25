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
To run the scalability test please please open a terminal and run the commands provided below :


```
Open a new terminal
cd CSUI
chmod a+x runScalability.sh
./runScalability.sh 5
```
Please note that the parameter (5 in this case) passed is the number of iterations over which the experimental results will be averaged. The user can provide any other integer value, as desired.

Once the test completes the user can view the new results in the GUI by clicking the Scalability Test button again.
Please don't run any other tests using the GUI , when running the Sacalability Test. 

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [MPJExpress](http://mpj-express.org/) - open source Java message passing library
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Authors

* **Rohan Sarkar** - [sarkar-rohan](https://github.com/sarkar-rohan)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

