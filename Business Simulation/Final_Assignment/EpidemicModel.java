package assignments;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.Random;
import umontreal.ssj.charts.EmpiricalChart;
import umontreal.ssj.rng.MRG32k3a;
import umontreal.ssj.rng.RandomStream;
import umontreal.ssj.stat.Tally;

public class EpidemicModel {
	static final int NUMBER_OF_SIMULATIONS = 5000;
	static final int TIME_STEPS = 50;
	Graph graph;
	Person[] persons; // Array of vertices which includes the status of each
	int numPersons;
	String graphFile;
	double alpha;
	double beta;
	double gamma;
	RandomStream rng;

	Random rand = new Random(); // used to alter the start of the RandomStream to obtain varying results

	public EpidemicModel(double alpha, double beta, double gamma, int numPersons, String graphFile, MRG32k3a rng) {
		this.alpha = alpha;
		this.beta = beta;
		this.gamma = gamma;
		this.numPersons = numPersons;
		this.graphFile = graphFile;
		this.rng = rng;
	}

	public static void main(String[] args) {
		String edgeFile = "social_graph.csv"; // Adjust this to the location of social_graph.csv
		int numPersons = 1000;
		double alpha = 1. / 20;
		double beta = 1. / 3;
		double gamma = 1. / 8;
		MRG32k3a myRNG = new MRG32k3a();
		EpidemicModel model = new EpidemicModel(alpha, beta, gamma, numPersons, edgeFile, myRNG);
		model.start();
	}

	public void start() {
		// This is your local test function
		graph = loadGraph(graphFile, ",", numPersons);

		MRG32k3a myRNG = new MRG32k3a();
		long[] seed = new long[6];
		for (int i = 0; i < seed.length; i++) {
			seed[i] = (long) rand.nextInt();
		}
		myRNG.setSeed(seed);
		rng = myRNG; // update the RandomStream

		// printSpreadOfDisease(TIME_STEPS)

		 System.out.println("Answer to Question 1:");
		 Tally prob1 = Q1(0.05);
		 System.out.println(prob1.report());
		
		 System.out.println("Answer to Question 2:");
		 Tally prob2 = Q2(0.05);
		 System.out.println(prob2.report());
		
		 double fraction3 = 0.5;
		 System.out.println("Answer to Question 3:");
		 Tally prob3 = Q1(fraction3);
		 System.out.println(prob3.report());
		 System.out.printf("Maximum is %.4f\n", prob3.max());
		
		 double fraction4 = 0.07;
		 System.out.println("Answer to Question 4:");
		 Tally prob4 = Q2(fraction4);
		 System.out.println(prob4.report());
		 System.out.printf("Maximum is %.4f\n", prob4.max());
		
		 System.out.println("Answer to Question 5:");
		 Tally prob5 = Q5(0.05);
		 System.out.println(prob5.report());
	}

	public Tally Q1(double fraction) {
		Tally prob = new Tally();
		for (int i = 0; i < NUMBER_OF_SIMULATIONS; i++) {
			loadGraph(graphFile, ",", numPersons);
			vaccinateRandomFraction(fraction);
			initializeDisease();
			prob.add(getFractionInfected());
			for (int j = 0; j < TIME_STEPS; j++) {
				simulateOneRun();
				prob.add(getFractionInfected());
			}
			// System.out.println("loading " + ((i + 1) * 100 / NUMBER_OF_SIMULATIONS) + "%");
		}
		return prob;
	}

	public void vaccinateNodes(double fraction) {
		// This function should vaccinate a fraction of the nodes chosen at random.
		int personsToBeVaccinated = (int) (numPersons * fraction);
		while (personsToBeVaccinated > 0) {
			int random = rand.nextInt(numPersons);
			if (!(persons[random].getState() == "V")) {
				persons[random].becomeVaccinated();
				if (graph.getVertex(persons[random].getLabel()) != null) {
					graph.removeVertex(persons[random].getLabel());
				}
				personsToBeVaccinated--;
			}
		}
	}

	public Tally Q2(double fraction) {
		Tally prob = new Tally();
		loadGraph(graphFile, ",", numPersons);
		vaccinateWithRule(fraction);
		for (int i = 0; i < NUMBER_OF_SIMULATIONS; i++) {
			initializeDisease();
			prob.add(getFractionInfected());
			for (int j = 0; j < TIME_STEPS; j++) {
				simulateOneRun();
				prob.add(getFractionInfected());
			}
			// System.out.println("loading " + ((i + 1) * 100 / NUMBER_OF_SIMULATIONS) + "%");
		}
		return prob;
	}

	public void vaccinateNodesAlternative(double fraction) {
		// This function should use the alternative vaccination rule stated in Question
		// 2 of your report
		int personsToBeVaccinated = (int) (numPersons * fraction);
		while (personsToBeVaccinated > 0) {
			int max = -1;
			int index = -1;
			for (int i = 0; i < numPersons; i++) {
				if (graph.getVertex(persons[i].getLabel()) != null
						&& graph.getVertex(persons[i].getLabel()).getNeighborCount() >= max) {
					max = graph.getVertex(persons[i].getLabel()).getNeighborCount();
					index = i;
				}
			}
			persons[index].becomeVaccinated();
			graph.removeVertex(persons[index].getLabel());
			personsToBeVaccinated -= 1;
		}
	}

	public Tally Q5(double fraction) {
		Tally prob = new Tally();
		for (int i = 0; i < 1; i++) {
			loadGraph(graphFile, ",", numPersons);
			initializeDisease();
			prob.add(getFractionInfected());
			for (int j = 0; j < 10; j++) {
				simulateOneRun();
				prob.add(getFractionInfected());
			}
			vaccinateNodesDelayed(fraction);
			for (int j = 10; j < TIME_STEPS; j++) {
				simulateOneRun();
				prob.add(getFractionInfected());
			}
			 System.out.println("loading " + ((i + 1) * 100 / NUMBER_OF_SIMULATIONS) +"%");
		}
		return prob;
	}

	public void vaccinateNodesDelayed(double fraction) {
		// This function should use the delayed vaccination strategy stated in Question 5 of your report
		int personsToBeVaccinated = (int) (numPersons * fraction);
		while (personsToBeVaccinated > 0) {
			int max = -1;
			int index = -1;
			for (int i = 0; i < numPersons; i++) {
				if (graph.getVertex(persons[i].getLabel()) != null && !(persons[i].getState() == "I")
						&& countInfectedNeighbors(persons[i]) > 0 && graph.getVertex(persons[i].getLabel())
								.getNeighborCount() > max - countInfectedNeighbors(persons[i])) {
					max = graph.getVertex(persons[i].getLabel()).getNeighborCount();
					index = i;
				}
			}
			persons[index].becomeVaccinated();
			graph.removeVertex(persons[index].getLabel());
			personsToBeVaccinated -= 1;
		}
	}

	public void simulateSpreadOfDisease(int t) {
		// This function should simulate the spread of the disease for t time steps
		for (int i = 0; i < t; i++) {
			simulateOneRun();
		}
	}

	public void simulateOneRun() {
		for (int j = 0; j < numPersons; j++) {
			if (persons[j].getState() == "I") {
				recovers(persons[j]);
			}
			if (persons[j].getState() == "R") {
				turnSusceptible(persons[j]);
			}
			if (persons[j].getState() == "S") {
				getsInfected(persons[j], countInfectedNeighbors(persons[j]));
			}
		}
	}

	public void turnSusceptible(Person recovered) {
		// recovered person has alpha chance to become susceptible again
		double random = rand.nextDouble();
		if (random < alpha) {
			recovered.becomeSusceptible();
		}
	}

	public void recovers(Person infected) {
		// infected person has gamma chance to recover
		double random = rand.nextDouble();
		if (random < gamma) {
			infected.becomeRecovered();
		}
	}

	public void getsInfected(Person susceptible, int numberOfInfectedNeighbors) {
		for (int i = 0; i < numberOfInfectedNeighbors; i++) {
			double random = rand.nextDouble();
			if (random < beta) {
				susceptible.becomeInfected();
				return;
			}
		}
	}

	public int countInfectedNeighbors(Person p) {
		int numberOfInfectedNeighbors = 0;

		if (graph.getVertex(p.getLabel()) == null) {
			return 0;
		}
		for (int j = 0; j < numPersons; j++) {
			if (persons[j].getState() == "I" && graph.getVertex(persons[j].getLabel()) != null) {
				Edge e = new Edge(graph.getVertex(p.getLabel()), graph.getVertex(persons[j].getLabel()));
				Edge f = new Edge(graph.getVertex(persons[j].getLabel()), graph.getVertex(p.getLabel()));

				if (graph.containsEdge(e) || graph.containsEdge(f)) {
					numberOfInfectedNeighbors++;
				}
			}
		}
		return numberOfInfectedNeighbors;
	}

	public void initializeDisease() {
		// Select the first infected individual
		int infectedPersons = 1;
		do {
			int random = rand.nextInt(numPersons);
			if (!(persons[random].getState() == "V")) {
				persons[random].becomeInfected();
				infectedPersons--;
			}
		} while (infectedPersons == 0);
	}

	public void printSpreadOfDisease(int t) {
		initializeDisease();
		double maxs[] = new double[t];
		for (int i = 0; i < t; i++) {
			simulateOneRun();
			maxs[i] = getFractionInfected();
		}
		EmpiricalChart plot = new EmpiricalChart("Graph", "y", "x", maxs);
		plot.view(500, 500);
	}

	/*
	 * DO NOT CHANGE ANY FUNCTIONS FROM HERE!
	 */

	public double getFractionInfected() {
		int numInfected = 0;
		for (Person person : persons) {
			String s = person.getState();
			if (s == "I") {
				numInfected++;
			}
		}
		return (double) numInfected / numPersons;
	}

	public double getDelayedSpreadOfDisease(int timeSteps, double fraction) {
		initializeDisease();
		simulateSpreadOfDisease(10);
		vaccinateNodesDelayed(fraction);
		simulateSpreadOfDisease(timeSteps - 10);
		return getFractionInfected();
	}

	public double getSpreadOfDisease(int timeSteps) {
		initializeDisease();
		simulateSpreadOfDisease(timeSteps);
		return getFractionInfected();
	}

	public void vaccinateRandomFraction(double fraction) {
		vaccinateNodes(fraction);
	}

	public void vaccinateWithRule(double fraction) {
		vaccinateNodesAlternative(fraction);
	}

	public void resetGraphStatus() {
		for (String vertexLabel : graph.vertexKeys()) {
			int id = graph.getVertex(vertexLabel).getId(); // Update status to Susceptable
			persons[id].becomeSusceptible();
		}
	}

	public Graph loadGraph(String edgeFile, String separator, int nodeRange) {
		Graph temp = new Graph();

		Vertex[] vertices = new Vertex[nodeRange];
		persons = new Person[nodeRange];
		String line;

		for (int i = 0; i < nodeRange; i++) {
			vertices[i] = new Vertex("Node " + i, i);
			persons[i] = new Person("Node " + i);
		}

		try (BufferedReader br = new BufferedReader(new FileReader(edgeFile))) {
			while ((line = br.readLine()) != null) {
				// use comma as separator
				String[] nodes = line.split(separator);
				try {
					Integer sid = Integer.parseInt(nodes[0]);
					Integer tid = Integer.parseInt(nodes[1]);

					if (!temp.containsVertex(vertices[sid])) {
						temp.addVertex(vertices[sid], false);
					}

					if (!temp.containsVertex(vertices[tid])) {
						temp.addVertex(vertices[tid], false);
					}

					temp.addEdge(vertices[sid], vertices[tid]);
				} catch (NumberFormatException e) {
					// This will catch the Error caused by the header line of the data-file
				}

			}

		} catch (IOException e) {
			e.printStackTrace();
		}

		return temp;
	}
}
