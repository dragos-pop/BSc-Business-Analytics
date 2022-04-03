package assignments;

public class Person {
	private String state;
	private String label;
	// private Integer id;

	public Person(String label) {
		this.state = "S";
		this.label = label;
	}

	public void becomeInfected() {
		this.state = "I";
	}

	public void becomeVaccinated() {
		this.state = "V";
	}

	public void becomeRecovered() {
		this.state = "R";
	}

	public void becomeSusceptible() {
		this.state = "S";
	}

	public String getState() {
		return this.state;
	}

	public String getLabel() {
		return this.label;
	}

}
