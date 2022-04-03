package assignments;

import java.util.LinkedList;
import umontreal.ssj.randvar.ExponentialGen;
import umontreal.ssj.rng.MRG32k3a;
import umontreal.ssj.rng.RandomStream;
import umontreal.ssj.simevents.Accumulate;
import umontreal.ssj.simevents.Event;
import umontreal.ssj.simevents.Sim;
import umontreal.ssj.stat.StatProbe;
import umontreal.ssj.stat.Tally;
import umontreal.ssj.stat.list.ListOfStatProbes;

public class Assignment2 {
	// First all pre-written classes are defined: ArrivalProcess, Customer, Server, StopEvent

	class ArrivalProcess extends Event {
		ExponentialGen arrivalTimeGen;
		double arrivalRate;

		public ArrivalProcess(RandomStream rng, double arrivalRate) {
			this.arrivalRate = arrivalRate;
			arrivalTimeGen = new ExponentialGen(rng, arrivalRate);
		}

		@Override
		public void actions() {
			double nextArrival = arrivalTimeGen.nextDouble();
			schedule(nextArrival);// Schedule this event after nextArrival time units
			handleArrival();
		}

		public void init() {
			double nextArrival = arrivalTimeGen.nextDouble();
			schedule(nextArrival);// Schedule this event after nextArrival time units
		}
	}

	class Customer {

		private double arrivalTime;
		private double startTime;
		private double completionTime;
		private double waitTime;
		private double serviceTime;
		private int chosenRegistry;

		public Customer() {
			// Record arrival time when creating a new customer
			arrivalTime = Sim.time();
			startTime = Double.NaN;
			completionTime = Double.NaN;
			waitTime = Double.NaN;
			serviceTime = serviceTimeGen.nextDouble();
		}

		// Call this method when the customer chooses a registry where he/she will be served
		public void chooseRegistry(int choice) {
			chosenRegistry = choice;
		}

		// Call this method when the service for this customer started
		public void serviceStarted() {
			startTime = Sim.time();
			waitTime = startTime - arrivalTime;
		}

		// Call this method when the service for this customer completed
		public void completed() {
			completionTime = Sim.time();
			serviceTime = completionTime - startTime;
		}
	}

	// This Event object represents a server
	class Server extends Event {
		static final double BUSY = 1.0;
		static final double IDLE = 0.0;
		Accumulate utilization; // Record utilization
		Customer currentCust; // Current customer in service
		LinkedList<Customer> queue; // Queue of the server
		boolean openServer;
		boolean busyServer;

		public Server(Accumulate utilization) {
			this.utilization = utilization;
			utilization.init(IDLE);
			currentCust = null;
			queue = new LinkedList<>();
			busyServer = false;
			openServer = true;
		}

		@Override
		public void actions() {
			utilization.update(IDLE);
			busyServer = false;
			serviceCompleted(this, currentCust);
		}

		public void startService(Customer cust) {
			utilization.update(BUSY);
			busyServer = true;
			currentCust = cust;
			cust.serviceStarted();

			schedule(cust.serviceTime);// Schedule this event after serviceTime time units
		}

		public void closeRegistry() {
			this.openServer = false;
		}

		public void openRegistry() {
			this.openServer = true;
		}
	}

	// Stop simulation by using this event
	class StopEvent extends Event {

		@Override
		public void actions() {
			Sim.stop();
		}
	}

	Server[] serverList;

	ArrivalProcess arrivalProcess;
	StopEvent stopEvent;
	ExponentialGen serviceTimeGen;

	int numServers;
	double arrivalRate;
	double serviceRate;
	double stopTime;
	int openLimit;

	Tally serviceTimeTally;
	Tally waitTimeTally;
	ListOfStatProbes<StatProbe> stats;
	ListOfStatProbes<StatProbe> stats2;

	public Assignment2(int numServers, double arrivalRate, double avgServiceTime, double stopTime, int openNew) {
		this.arrivalRate = arrivalRate;
		this.serviceRate = avgServiceTime;
		this.numServers = numServers;
		this.stopTime = stopTime;
		this.openLimit = openNew;

		serverList = new Server[numServers];
		stats = new ListOfStatProbes<>("Stats for Accumulate");
		stats2 = new ListOfStatProbes<>("Stats for Tallies");

		for (int i = 0; i < numServers; i++) {
			String id = "server " + i;
			Accumulate utilization = new Accumulate(id);
			stats.add(utilization);
			Server server = new Server(utilization);
			serverList[i] = server;
			if (i > 0) {
				server.closeRegistry();
			}
		}

		// Create inter arrival time, and service time generators
		serviceTimeGen = new ExponentialGen(new MRG32k3a(), 1 / avgServiceTime);
		arrivalProcess = new ArrivalProcess(new MRG32k3a(), arrivalRate);
		stopEvent = new StopEvent();

		// Create Tallies
		waitTimeTally = new Tally("Waittime");
		serviceTimeTally = new Tally("Servicetime");

		// Add Tallies in ListOfStatProbes for later reporting
		stats2.add(waitTimeTally);
		stats2.add(serviceTimeTally);	
	}

	public ListOfStatProbes[] simulateOneRun() {
		Sim.init();
		waitTimeTally.init();
		serviceTimeTally.init();
		arrivalProcess.init();
		stopEvent.schedule(stopTime);
		Sim.start();

		ListOfStatProbes[] output = new ListOfStatProbes[2];
		output[0] = stats;
		output[1] = stats2;
		for (int i = 0; i <= 1; i++) {
			System.out.println(output[i].report());
		}
		return output;
	}

	int Question1() {
		// Write a function that returns the index of the shortest queue
		int minSize = Integer.MAX_VALUE;
		int minIndex = numServers;
		for (int i = 0; i < numServers; i++) {
			if (serverList[i].openServer && serverList[i].queue.size() < minSize) {
				minSize = serverList[i].queue.size();
				minIndex = i;
			}
		}
		return minIndex;
	}

	boolean Question2() {
		// Write a function that returns if a new registry should be opened
		int openServers = 0;
		for (int i = 0; i < numServers; i++) {
			if (serverList[i].openServer) {
				openServers++;
			}
		}
		if (openServers < numServers) {
			if (serverList[Question1()].queue.size() == openLimit) {
				return true;
			}
		}
		return false;
	}

	void Question3() {
		// Write a function that closes all registries that can be closed
		int openServers = 0;
		int idleServers = 0;
		for (int i = 0; i < numServers; i++) {
			if (serverList[i].openServer) {
				openServers++;
				if (!serverList[i].busyServer) {
					idleServers++;
				}
			}
		}
		if (openServers == (idleServers - 1)) {
			for (int i = 0; i < numServers; i++) {
				if (serverList[i].openServer && !(serverList[i].busyServer)) {
					serverList[i].closeRegistry();
				}
			}
		}
	}

	void handleArrival() {
		// Write a function that handles the arrival of a customer to the queuing system
		Customer newCustomer = new Customer(); 

		if (Question2()) { 
			int serverToBeOpened = 1;
			int i = 0;
			while (serverToBeOpened != 0) {
				if (serverList[i].openServer) {
					i++;
				} else {
					serverList[i].openRegistry();
					serverToBeOpened--;
				}
			}
		}
		
		int smallestQueue = Question1();
		newCustomer.chooseRegistry(smallestQueue);

		if (serverList[smallestQueue].busyServer) {
			serverList[smallestQueue].queue.addLast(newCustomer);
		} else {
			serverList[smallestQueue].startService(newCustomer);
		}
		

	}

	void serviceCompleted(Server server, Customer cust) {
		// Write a function that completes the service of the customer, update the Tallies and start the service of a new customer
		cust.completed();

		waitTimeTally.add(cust.waitTime);
		serviceTimeTally.add(cust.serviceTime);

		server.queue.remove(cust);
		if (server.queue.isEmpty()) {
			Question3();
		} else {
			Customer next = server.queue.getFirst();
			server.startService(next);
		}
	}

	public static void main(String[] args) {
		int C = 5; // #Servers
		double lambda = 5; // Arrival rate
		double mu = 2; // Service rate
		double maxTime = 10000; // Simulation endtime (minutes)
		int openNew = 3; // number of customers at the registry (including the one in service) before a new registry can be opened

		Assignment2 grocery;
		grocery = new Assignment2(C, lambda, (1 / mu), maxTime, openNew);
		ListOfStatProbes[] output = grocery.simulateOneRun();
	}
}