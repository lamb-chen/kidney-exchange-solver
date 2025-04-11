import pool as p
import json


class JSONReader(object):
    def read_json(self, filename):
        pool = p.Pool()
        # reading from test.json and creating pool graph
        try:
            with open(filename, "r") as dataset_json:
                json_data = json.load(dataset_json)["data"]
                seen_patient_ids = set()
                for donor_id in json_data:
                    donor = json_data[donor_id]
                    dage = int(donor["dage"])
                    is_altruistic = "altruistic" in json_data[donor_id] and json_data[donor_id]["altruistic"]
                    if is_altruistic:
                        altruist = p.Altruist(donor_id, dage)
                        if "matches" in donor:
                            for matched_patient in donor["matches"]:
                                recipient_patient_id = matched_patient["recipient"]

                                if recipient_patient_id not in seen_patient_ids: 
                                    pool.patients[recipient_patient_id] = p.Patient(recipient_patient_id)
                                    seen_patient_ids.add(recipient_patient_id)

                                score = int(matched_patient["score"])
                                altruist.add_recipient(recipient_patient_id, score)
                        pool.altruists.append(altruist)
                    else:
                        donor_obj = p.Donor(donor_id, dage)
                        for source_patient_id in donor["sources"]:
                            if source_patient_id not in seen_patient_ids:
                                pool.patients[source_patient_id] = p.Patient(source_patient_id)
                                seen_patient_ids.add(source_patient_id)
                            donor_patient_node = p.DonorPatientNode(donor_obj, pool.patients[source_patient_id])
                            if "matches" in donor:
                                for matched_patient in donor["matches"]:
                                        recipient_patient_id = matched_patient["recipient"]

                                        if recipient_patient_id not in seen_patient_ids: 
                                            pool.patients[recipient_patient_id] = p.Patient(recipient_patient_id)
                                            seen_patient_ids.add(recipient_patient_id)

                                        score = int(matched_patient["score"])
                                        donor_patient_node.add_recipient(recipient_patient_id, score)
                            pool.add_donor_patient_node(donor_patient_node)
                pool.add_edges_to_nodes()
                return pool
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except json.JSONDecodeError:
            print(f"Error: Failed to parse JSON in '{filename}'.")
