from project.app.ml.generators.session_simulator import SyntheticSessionSimulator


def test_simulator_runs():
    simulator = SyntheticSessionSimulator()

    task_metadata = {
        "declared_difficulty": 0.5
    }

    sessions = simulator.simulate_cohort(task_metadata, num_sessions=200)

    assert len(sessions) == 200
    assert "accuracy" in sessions[0]
    assert "response_time" in sessions[0]
