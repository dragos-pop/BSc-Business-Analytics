package assignments;

import java.io.FileReader;
import java.io.IOException;
import umontreal.ssj.charts.EmpiricalChart;
import umontreal.ssj.probdist.EmpiricalDist;
import umontreal.ssj.stat.Tally;
import java.io.PrintStream;
import java.util.Arrays;
import java.io.BufferedReader;

public class Assignment1 {
	static final int NUMBER_OF_SIMULATIONS = 5000;

	 double seed = 1346;
	 double m = Math.pow(2, 48);
	 double a = 25214903917.;
	 double c = 13.;

	int raceTo = 5;
	double winThreshold = .5;

	LCG prng;
	EmpiricalDist durationDist;

	PrintStream out;

	Assignment1() {
		out = new PrintStream(System.out);
	}

	public double[] Question1(double givenSeed, int numOutputs, boolean normalize) {
		prng = new LCG(givenSeed, a, c, m);
		double[] result = new double[numOutputs];
		for (int i = 0; i < numOutputs; i++) {
			result[i] = prng.generateNext(normalize);
		}
		return result;
	}

	public EmpiricalDist Question2(String csvFile) {
		EmpiricalDist myDist = getDurationDist(csvFile);
		return myDist;
	}

	public void plotEmpiricalCDF() {
		EmpiricalChart plot = new EmpiricalChart("Empirical CDF of the game lengths", "x", "F(x)", durationDist.getParams());
		plot.view(500, 500);
	}

	public Tally Question3() {
		Tally durations = new Tally();
		for (int i = 0; i < NUMBER_OF_SIMULATIONS; i++) {
			durations.add(simulateMatch(raceTo));
			
		}
		return durations;
	}

	public double simulateMatch(int raceTo) {
		int winsP1 = 0;
		int winsP2 = 0;
		double matchDuration = 0;
		while (winsP1 < raceTo && winsP2 < raceTo) {
			double probability = prng.generateNext(true);
			if (probability < winThreshold) {
				winsP1++;
			} else {
				winsP2++;
			}
			matchDuration += durationDist.inverseF(prng.generateNext(true));
		}
		return matchDuration;
	}

	public EmpiricalDist getDurationDist(String csvFile) {
		try {
			BufferedReader count = new BufferedReader(new FileReader(csvFile));
			BufferedReader input = new BufferedReader(new FileReader(csvFile));
			int counter = 0;
			while(count.readLine() != null) {
				counter++;
			}
			double[] gameLengths = new double[counter]; //number of entries in the csv file
			for (int i = 0; i < counter; i++) {
				String line = input.readLine();
				gameLengths[i] = Double.parseDouble(line);
			}
			Arrays.sort(gameLengths);
			durationDist = new EmpiricalDist(gameLengths);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return durationDist;	
	}

	
	public class LCG {
		public double seed;
		public final double m;
		public final double a;
		public final double c;

		public double lastOutput;

		public LCG(double seed, double a, double c, double m) {
			this.seed = seed;
			this.m = m;
			this.a = a;
			this.c = c;

			this.lastOutput = seed;
		}

		public double generateNext(boolean normalize) {
			double result = (a * seed + c) % m;
			if (normalize == false) {
				setSeed(result);
				return result;
			} else {
				setSeed(result);
				double normalized = (result + 1) / (m + 1);
				return normalized;
			}
		}

		public void setSeed(double newSeed) {
			this.seed = newSeed;
		}
	}

	public void start() {
		double givenSeed = seed;
		int numOutputs = 3;
		double[] outputRegRNG = Question1(givenSeed, numOutputs, false);
		double[] outputNormRNG = Question1(givenSeed, numOutputs, true);
		for (int i = 0; i < numOutputs; i++) {
			out.println("Regular:" + outputRegRNG[i]);
			out.println("Normalized:" + outputNormRNG[i]);
		}
		String csvFile = "game_lengths.csv";
		EmpiricalDist myDist = Question2(csvFile);
		out.println(myDist.inverseF(0.0));
		out.println(myDist.inverseF(0.25));
		out.println(myDist.inverseF(0.5));
		out.println(myDist.inverseF(0.75));
		out.println(myDist.inverseF(1.0));
		plotEmpiricalCDF();
		Tally durations = Question3();
		out.println(durations.report());
	}

	public static void main(String[] args) {
		new Assignment1().start();
	}

}