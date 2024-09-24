from synthetic_data import TreatmentData
import matplotlib.pyplot as plt


def test_generate():
    data = TreatmentData.generate(100)
    # Serialize them
    jsons = [datum.model_dump_json() for datum in data]
    print(jsons)

def test_generate_plots():
    data = TreatmentData.generate(1000)
    measurements = {treatment:[datum.measurement for datum in data if datum.treatment==treatment] for treatment in [False, True]}
    plt.xlim(0, 30)
    plt.ecdf(measurements[False])
    plt.ecdf(measurements[True])
    plt.show()